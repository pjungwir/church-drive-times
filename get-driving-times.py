#!/usr/bin/env python3.9

import psycopg2
import psycopg2.extras
import requests
import json
import os
import time
import datetime
import zoneinfo
import math

api_key = os.environ.get("GOOGLE_MAPS_API_KEY", None)
if api_key is None:
    raise Exception("GOOGLE_MAPS_API_KEY envvar must be set")

database_url = os.environ.get("DATABASE_URL", None)
if database_url is None:
    raise Exception("DATABASE_URL envvar must be set")

url = "https://maps.googleapis.com/maps/api/distancematrix/json"


# TODO: Is 25 really the max? We know 50 is too big and gives a MAX_DIMENSION_EXCEEDED error.
def choose_best_churches_per_call(big_c, big_f, max_dimension=25, max_elements=100):
    """Chooses the number of churches & families to ask Google about in each call.

    Returns a tuple of (churches, families).

    Google only lets us ask about 100 combinations per call.
    So we could ask for 10 families times 10 churches at once,
    or maybe 60 families per church,
    or all the churches for each family, etc.
    We want to still be efficient after we have timed everything,
    and then someone adds a church or adds a family,
    and we have to time the new combinations.
    This function chooses the optimal number of churches to ask about at once.

    Let `c` be the number of churches in one call.
    Let `f` be the number of families in one call.

    Then cf <= 100.
    Since we know we want to get as close to 100 as possible,
    f = floor(100 / c).
    
    Let `C` be the number of to-be-timed churches.
    Let `F` be the number of to-be-timed families.
    Let `N` be the number of calls to Google.

    Then N = ceil(C/c) * ceil(F/f)

    In other words we are cutting up our big C * F matrix into little matrices,
    and we want as few matrices as possible.

    The floor & ceil functions make it hard to write a math formula to minimize N,
    so let's just iterate from 1 to C and take whatever c gives the best N.
    It's lazy but it works.

    Google has some restrictions on how many origins/destinations we request at once.
    The most combinations allowed is 100, or we get a MAX_ELEMENTS_EXCEEDED error.
    Neither origin nor destination can be 50 or above or we get a MAX_DIMENSION_EXCEEDED error.
    25 is okay. We haven't tested dimensions with 26 - 49 elements yet.
    (It's tricky to test, because if you set our max_dimension parameter higher, the algorithm here may still choose a lower c or f!)
    """

    best_c = big_c
    best_f = big_f
    best_N = big_c * big_f  # start with the worst possible N.

    for c in range(1, min(big_c + 1, max_dimension)):
        f = min(max_elements // c, max_dimension)

        big_N = math.ceil(big_c / c) * math.ceil(big_f / f)
        print(f"c={c} f={f} N={big_N}")

        if big_N < best_N:
            best_N = big_N
            best_c = c
            best_f = f

    print(f"best_N={best_N}")
    return (best_c, best_f)
    
def save_trip_times(cur, departure_time, churches, families, result):
    """Parses a response from Google and saves it to the database.

    Google gives a result like this:

       "rows" : [
          {
             "elements" : [
                {
                   "distance" : {
                      "text" : "6.9 mi",
                      "value" : 11100
                   },
                   "duration" : {
                      "text" : "13 mins",
                      "value" : 808
                   },
                   "duration_in_traffic" : {
                      "text" : "13 mins",
                      "value" : 808
                   "status" : "OK"
                },
                ...
            ],
        },
        ...
      ]

    Each origin (i.e. family) has its own row.
    Each destination (i.e. church) has one element per row.

    Note that each (origin, destination) pair has both a "duration" value and a "duration_in_traffic" value.
    Only the "duration_in_traffic" value changes based on "departure_time", so we should use that one.
    """
    for i in range(0, len(families)):
        f = families[i]
        for j in range(0, len(churches)):
            ch = churches[j]
            el = result['rows'][i]['elements'][j]

            # There is *one address* where Google omits duration_in_traffic (grrr....),
            # I suppose maybe because the route goes through places where Google has no traffic data,
            # so in that case we should fall back to the regular duration value.
            duration = el.get('duration_in_traffic', None)
            if duration is None:
                duration = el['duration']
            duration = duration['value']

            # TODO: Make sure the status is OK.
            cur.execute("INSERT INTO trips (family_id, church_id, departure_time, seconds) VALUES (%s, %s, %s, %s)",
                (f['id'], ch['id'], departure_time.strftime("%Y-%m-%d %H:%M:%S %Z"), duration))

def get_trip_times(cur, departure_time):
    departure_time_str = departure_time.strftime("%B %d, %Y %H:%M %Z")
    print(f"Getting trip times for {departure_time_str} = = {int(time.mktime(departure_time.timetuple()))}")

    # Get all families that are missing a time for any church:
    # all families except those that have times for all churches.
    cur.execute("""
      SELECT  DISTINCT f.*
      FROM    families f
      CROSS JOIN churches ch
      LEFT OUTER JOIN trips t
      ON      t.church_id = ch.id
      AND     t.family_id = f.id
      AND     t.departure_time = %s
      WHERE   f.place_id IS NOT NULL
      AND     ch.place_id IS NOT NULL
      AND     t.church_id IS NULL
    """, (departure_time_str,))
    families = cur.fetchall()
    # Get all churches that are missing a time for any family:
    cur.execute("""
      SELECT  DISTINCT ch.*
      FROM    churches ch
      CROSS JOIN families f
      LEFT OUTER JOIN trips t
      ON      t.church_id = ch.id
      AND     t.family_id = f.id
      AND     t.departure_time = %s
      WHERE   ch.place_id IS NOT NULL
      AND     f.place_id IS NOT NULL
      AND     t.family_id IS NULL
    """, (departure_time_str,))
    churches = cur.fetchall()

    if len(churches) == 0 or len(families) == 0:
        print(f"No churches or families need to timing for {departure_time_str}. Skipping....")
        return

    # Choose the optimal number of churches & families to query at a time,
    # minimize the API calls:
    c, f = choose_best_churches_per_call(len(churches), len(families))

    church_groups = math.ceil(len(churches) / c)
    family_groups = math.ceil(len(families) / f)

    for i in range(0, church_groups):
        sub_churches = churches[i*c : i*c + c]
        for j in range(0, family_groups):
            sub_families = families[j*f : j*f + f]

            params = {
                'origins':      '|'.join([f"place_id:{family['place_id']}" for family in sub_families]),
                'destinations': '|'.join([f"place_id:{church['place_id']}" for church in sub_churches]),
                # It would be nicer to ask about arrival_time instead of departure_time,
                # but Google only supports arrival_time for transit queries (i.e. bus, subway, etc.), not driving.
                # Since we're making a driving query, arrival_time is ignored
                # and we would just get average answers that are the same for every time.
                'departure_time': int(time.mktime(departure_time.timetuple())),
                'language':     'en',
                'mode':         'DRIVING',
                'units':        'imperial',
                'key':          api_key,
            }
            resp = requests.get(url, params=params)
            if resp.status_code == 200:
                print(resp.text)

                result = json.loads(resp.text)
                save_trip_times(cur, departure_time, sub_churches, sub_families, result)
            else:
                raise Exception(f"Driving time failed")

def get_next_departure_time(dow, hours, minutes):
    """Given a day of week and time of day, get the next date when that happens.

    We need this because Google only gives traffic times for future dates.
    """
    now = datetime.datetime.now(zoneinfo.ZoneInfo("America/Los_Angeles"))
    days_to_add = datetime.timedelta(days=((dow - now.weekday()) % 7))
    t = now + days_to_add
    return datetime.datetime.combine(t.date(), datetime.time(hour=hours, minute=minutes))


if __name__ == '__main__':
    with psycopg2.connect(database_url) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            # Sunday morning, Saturday vespers, Friday evening:
            # for departure_time in ["June 19, 2022 10:00 PDT", "July 2, 2022 18:30 PDT", "July 1, 2022 19:00 PDT"]:
            # TODO: Google actually only uses traffic predictions for times in the future.
            # So if we run this after the dates below, we'll keep wrong results
            # (and they will be the same for all departure times).
            # So we should actually generate these dates dynamically based on when you run the program.
            for departure_time in [(6, 9, 30), (5, 18, 0), (4, 18, 30)]:
                t = get_next_departure_time(*departure_time)
                get_trip_times(cur, t)
        conn.commit()
