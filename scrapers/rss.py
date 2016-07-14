"""
RSS Scraper
"""
import csv
import time
import feedparser
from Scrapengine.configs import SCRAPERS, ARCHIVE

SOURCES = dict(count=len(SCRAPERS['rss']), _all=SCRAPERS['rss'])

def get_source(source):
    '''
    gets and parses rss feed from `source`
    `source` is a direct URL to the RSS feed
    '''
    parsed_response = feedparser.parse(source)
    return parsed_response


def get_entries(parsed_response):
    '''
    extract entries from parsed RSS feed
    '''
    return parsed_response['entries']


def output(entries, destination='csv', source=''):
    for entry in entries:
        outputfile = "%s/%s-rss-output-%s.csv" % (ARCHIVE, source, time.time())
        with open(outputfile, 'wb') as csvfile:
            outputwriter = csv.writer(csvfile, delimiter=',')
            outputwriter.writerow([entry])
        csvfile.close()
    return outputfile
        
