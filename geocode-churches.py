#!/usr/bin/env python3.8

import psycopg2
import psycopg2.extras
import requests
import os
import json

api_key = os.environ.get("GOOGLE_MAPS_API_KEY", None)
if api_key is None:
    raise Exception("GOOGLE_MAPS_API_KEY envvar must be set")

database_url = os.environ.get("DATABASE_URL", None)
if database_url is None:
    raise Exception("DATABASE_URL envvar must be set")

url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

with psycopg2.connect(database_url) as conn:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT * FROM churches WHERE latitude IS NULL OR longitude IS NULL")
        for church in cur.fetchall():
            params = {
                'input':     f"{church['address']}, {church['city']}, {church['state']} {church['zip']}",
                'inputtype': 'textquery',
                'fields':    'formatted_address,name,geometry,place_id',
                'key':       api_key,
            }
            resp = requests.get(url, params=params)
            if resp.status_code == 200:
                print(resp.text)

                result = json.loads(resp.text)
                if len(result['candidates']) == 0:
                    # raise Exception(f"Geocoding got zero results for {church}")
                    print(f"WARNING: Geocoding got zero results for {church}")
                    continue

                result = result['candidates'][0]
                lonlat = result['geometry']['location']
                cur.execute("UPDATE churches SET latitude = %s, longitude = %s WHERE id = %s",
                    (lonlat['lat'], lonlat['lng'], church['id']))
            else:
                raise Exception(f"Geocoding failed for {church}")
        conn.commit()
