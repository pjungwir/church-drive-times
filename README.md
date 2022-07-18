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
    - We already exclude already-known families/churches. (There might be a problem though since we got dupes before.)
    - We should add a `force` option that overwrites the old values using `ON CONFLICT DO UPDATE`.
  + fix minutes-vs-seconds for trip time: our db column is named minutes but Google gives us seconds.
  - write some tests?
  + improve how the db stores day-of-week and time-of-day:
    + store day-of-week as an integer?
    + maybe just store a single column with a full timestamp, especially since that's what we ask Google for?
      + I think I like this approach the best. The frontend can always treat it as a representative and just use dow and time.
- Add an html table with driving time statistics for each church:
  + don't show "null" for size or price
  + add dollar sign & commas for price
  + mean driving time
  + 5/10/50/90/95% driving time
  - what percent are within 10/20/30 minutes?
  + mean delta driving time (delta = change from your old driving time)
  + 5/10/50/90/95% delta driving time
  - what percent are no more than 10/20/30 minutes worse?
  - csv download
  - show different arrival times (Sun morning, Sat evening, etc)
    + the numbers don't change. Isn't that fishy?
      + (It was because we needed to ask Google about a destination_time not an arrival_time, then use duration_in_traffic not duration.)
    + the dropdown should show Sunday morning at the beginning to match the table.
    + align it right not left
  - add 80%....
  - change `arrival_time` to `departure_time` in the database and elsewhere since that's what we have to ask Google
  + Why does one of the churches have a "-0" median change in drive time for Friday 7 p.m.? Don't show "-0".
    + Probably it's because the real value is in seconds and barely negative, and when we diving by 60 we get -0.
    + James and I can talk about floating point numbers!!!
  - If a popup is open and you change the departure time, then the popup doesn't get refreshed.
  - If the popup for another church is already open, and you click a table row for a different church,
    and that pin is off the map (or maybe even just close to an edge),
    then the new church's popup doesn't point to the pin. That is a bug! It should point to the pin.
    
- put it online with a password
- let people type in a new church address
  - geocode it, compute times
  - save it to the database so others can see?
- click on a church row (or maybe just the name/address) to popup its marker
- let people type in their own address and show their own drive time on the table & popup.
- let people sort the table by any column
+ click on a marker to:
  + show the name/address/size/price
  + highlight the table row
