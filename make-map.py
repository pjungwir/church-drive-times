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
        cur.execute("SELECT name, address, size, price, longitude, latitude, current FROM churches WHERE longitude IS NOT NULL AND latitude IS NOT NULL")
        churches = [
            {
                **ch,
                'price': (float(ch['price']) if ch['price'] is not None else None),
            }
            for ch
            in cur.fetchall()
        ]


        with open("map.html.template") as f:
            template = f.read()

        html = template.replace("{{churches}}", json.dumps(churches))

        print(html)
