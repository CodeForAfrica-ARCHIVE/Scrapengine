"""
load and execute scrapers
"""
import sys
import csv
import time
from Scrapengine.scrapers import rss, article, lawyers_ke, nurses_ke
from Scrapengine.configs import SCRAPERS


def execute_rss(single=True):
    '''
    `single` - set True to scrape only one source. Leave it out or
               set False to scrape all pre-configured sources
    '''
    print "RSS Scrapers: %d sources" % rss.SOURCES['count']
    for source in rss.SOURCES['_all']:
        parsed = rss.get_source(rss.SOURCES['_all'][source])
        entries = rss.get_entries(parsed)
        outputfile = rss.output(entries, destination='csv', source=source)
        print "Output %s" % outputfile

        if single:
            break


def execute_article():
    sources = SCRAPERS['article']
    print "scraper.article sources: %s" % sources.keys()
    for source in sources:
        print "scraping %s" % source
        page = article.get_source_html(sources[source])
        links = article.get_links(page)
        article_links = article._filter(links, _format="100r")
        print "%d articles from %s" % (len(article_links), sources[source])
        output = article.output(article_links, source="engine")
        print "Outputfile: %s" % output

def execute_lawyers_ke():
    print lawyers_ke.main()

def execute_nurses_ke():
    #nurses_ke.main("single", "alice")
    #nurses_ke.main("all", names_source="Scrapengine.scrapers.names", source_type="list")
    nurses_ke.main("all", names_source="/Users/aventador/code/c4a/Scrapengine/scrapers/names.csv", source_type="csv")


if __name__ == "__main__":
    try:
        scraper = sys.argv[1]
    except IndexError:
        print "\n\n   Usage:  python client.py <scraper>\n\n"
        sys.exit(2)
    if scraper == "rss":
        execute_rss(single=False)
    elif scraper == "article":
        execute_article()
    elif scraper == "lawyers_ke":
        execute_lawyers_ke()
    elif scraper == "nurses_ke":
        execute_nurses_ke()
