#!/usr/bin/env python3.8

import os
import json
import psycopg2
import psycopg2.extras

database_url = os.environ.get("DATABASE_URL", None)
if database_url is None:
    raise Exception("DATABASE_URL envvar must be set")

with psycopg2.connect(database_url) as conn:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
SELECT  t.departure_time, ch.id, ch.name, ch.address, ch.size, ch.price, ch.longitude, ch.latitude, ch.current,
        count(DISTINCT t.family_id) AS number_of_known_trip_times,
        avg(t.seconds) AS mean_seconds,
        percentile_cont(ARRAY[0.50, 0.90, 0.95]) WITHIN GROUP (ORDER BY t.seconds) AS seconds_percents,
        avg(t.seconds - st_johns.seconds) AS mean_delta_seconds,
        percentile_cont(ARRAY[0.50, 0.90, 0.95]) WITHIN GROUP (ORDER BY t.seconds - st_johns.seconds) AS delta_seconds_percents
FROM    churches ch
LEFT OUTER JOIN trips t ON t.church_id = ch.id
LEFT OUTER JOIN (
  -- Get each family's trip to St. Johns for comparison:
  SELECT  t.departure_time, t.family_id, t.seconds
  FROM    churches ch
  JOIN    trips t ON t.church_id = ch.id
  WHERE   ch.current
) AS st_johns ON t.family_id = st_johns.family_id AND t.departure_time = st_johns.departure_time
WHERE   ch.longitude IS NOT NULL AND ch.latitude IS NOT NULL
GROUP BY t.departure_time, ch.id
ORDER BY t.departure_time, mean_seconds DESC
        """)

        churches = [
            {
                **ch,
                'price': (float(ch['price']) if ch['price'] is not None else None),
				'departure_time': ch['departure_time'].strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            for ch
            in cur.fetchall()
        ]


        with open("map.html.template") as f:
            template = f.read()

        html = template.replace("{{churches}}", json.dumps(churches))

        print(html)
