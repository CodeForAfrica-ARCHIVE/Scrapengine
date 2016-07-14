"""
load and execute scrapers
"""
import csv
import time
from Scrapengine.scrapers import rss

def execute_rss(single=True):
    '''
    `single` - set True to scrape only one source. Leave it out or
               set False to scrape all pre-configured sources
    '''
    print "RSS Scrapers: %d sources" % rss.SOURCES['count']
    for source in rss.SOURCES['_all'].values():
        parsed = rss.get_source(source)
        entries = rss.get_entries(parsed)
        outputfile = rss.output(entries, destination='csv', source='engine')
        print "Output %s" % outputfile

        if single:
            break



if __name__ == "__main__":
    execute_rss()
    #execute_other()
