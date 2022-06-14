SHELL := /bin/bash

map.html: make-map.py map.html.template
	./make-map.py > map.html

families.csv: families.csv.cpt .env
	source .env && export ENCRYPTION_KEY && ccrypt -E ENCRYPTION_KEY -d < $< > $@

families.csv.cpt:
	source .env && export ENCRYPTION_KEY && ccrypt -E ENCRYPTION_KEY -e < families.csv > $@

.PHONY: families.csv.cpt
