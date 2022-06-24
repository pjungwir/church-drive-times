Church Sites Mapper
===================

This project is to help our church find a new location. It uses the addresses of all the parish families to report how far away a potential new site is.


Files
-----

- `.env` - Not in git; contains secrets. See `.env.sample`.
- `churches.csv` - The potential church sites.
- `familes.csv.cpt` - The parish families. This file is encrypted. You need to have `ENCRYPTION_KEY` set in your `.env` file then run `make families.csv`.


TODO
----

+ Draw a Google map.
+ Plot pins for church sites.
+ Set up database for families and churches.
+ Add `.env`.
+ Encrypt `families.csv`.
+ Add a Makefile.
+ Geocode families and store the lonlat in the database.
+ Geocode churches and store the lonlat in the database.
+ Get `place_id` for each family & church and store them in the database.
  We can pass these to the distancematrix api instead of lonlat (since it is preferred),
  and also we can send them to the places api to get extra info like a tidied-up address, and other interesting things.
+ Enter all the church addresses.
- Add a drive time table and compute the driving time.
  + find optimal origin/destination size.
  + ask google for trip times.
  + save trip times to database.
  - check for OK status
  - don't ask for families/churches we already know about, unless you pass a `force` option.
  - fix minutes-vs-seconds for trip time: our db column is named minutes but Google gives us seconds.
  - write some tests?
  - improve how the db stores day-of-week and time-of-day:
    - store day-of-week as an integer?
    - maybe just store a single column with a full timestamp, especially since that's what we ask Google for?
      - I think I like this approach the best. The frontend can always treat it as a representative and just use dow and time.
- Add an html table with driving time statistics for each church:
  - mean driving time
  - median driving time
  - 5/10/90/95% driving time
  - what percent are within 10/20/30 minutes?
  - mean delta driving time (delta = change from your old driving time)
  - median delta driving time
  - 5/10/90/95% delta driving time
  - what percent are no more than 10/20/30 minutes worse?
- put it online with a password
- let people type in a new church address
- click on a marker to:
  - show the name/address/size/price
  - highlight the table row
