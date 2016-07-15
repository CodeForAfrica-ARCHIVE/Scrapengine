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
    outputfile = "%s/%s-rss-output-%s.csv" % (ARCHIVE, source, time.time())
    with open(outputfile, 'wa') as csvfile:
        outputwriter = csv.writer(csvfile, delimiter='#')
        for entry in entries:
            outputwriter.writerow([
                _encode(entry['id']),
                _encode(entry['published']),
                _encode(entry['title']),
                _encode(entry['summary']),
                _encode(entry['link'])
                ])
            print "writiten %s" % entry.get('id')
    csvfile.close()
    return outputfile
        

def _encode(_unicode):
    return _unicode.encode('utf-8')
