SHELL := /bin/bash

map.html: make-map.py map.html.template .env
	source .env && export DATABASE_URL && ./make-map.py > map.html

families.csv: families.csv.cpt .env
	source .env && export ENCRYPTION_KEY && ccrypt -E ENCRYPTION_KEY -d < $< > $@

families.csv.cpt:
	source .env && export ENCRYPTION_KEY && ccrypt -E ENCRYPTION_KEY -e < families.csv > $@

upload: map.html
	scp map.html ic:/var/www/ic/church-sites/

.PHONY: families.csv.cpt upload
