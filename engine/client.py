"""
load and execute scrapers
"""

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
        print "RSS Scraper: %s entries from %s" % (len(entries), source)
        if single:
            break



if __name__ == "__main__":
    execute_rss()
    #execute_other()
