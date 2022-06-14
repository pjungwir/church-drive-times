#!/usr/bin/env python3.8

import json

# TODO: geocode on the server so we only do it once, not in the browser.
# TODO: in that case, maybe we should start putting these addresses into a database. <- MONDAY
churches = [
    ('5529 NE Century Blvd', '5.32', ''),
    ('NE Belknap Court, Hillsboro, OR 97124', '3.9', '$2,050,000'),
    ('6220 NE Pubols St., Hillsboro, OR 97124', '5.01', '')
]
churches = [
    { 'address': c[0], 'size': c[1], 'price': c[2] } for c in churches
]

families = [
]

with open("map.html.template") as f:
    template = f.read()

html = template.replace("{{churches}}", json.dumps(churches))

print(html)
