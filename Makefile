test:
	nosetests

scrape:
	python engine/client.py $(scraper)
