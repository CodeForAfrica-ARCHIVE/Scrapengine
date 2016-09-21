"""
Scrape news articles from www.the-star.co.ke/api/mobile/views/mobile_app?args%5B0%5D=24&limit=3
"""
import time
import requests
from Scrapengine.configs import ARCHIVE

SOURCE_URL = "http://www.the-star.co.ke/api/mobile/views/mobile_app?args[0]=24&limit=%s"
OUTPUTFILE = "starhealth_news-output"

def get_articles(count=50):
    """
    return a `list` of articles from API
    """
    try:
        resp = requests.get(SOURCE_URL % count)
        resp.raise_for_status()
        return resp.json()
    except Exception, err:
        print "ERROR: get_articles() - %s" % str(err)
        return []

def output(articles, outputfile=OUTPUTFILE):
    try:
        _file = open("%s/%s-%s.json" % (ARCHIVE, outputfile, time.time()), "w")
        _file.write(str(articles))
        _file.close()
    except Exception, err:
        print "ERROR: output() - %s" % str(err)
        raise err


def main():

    print "Done"
