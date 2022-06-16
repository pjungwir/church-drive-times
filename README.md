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
- Geocode churches and store the lonlat in the database.
- Add a drive time table and compute the driving time.
- Enter all the church addresses.
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
