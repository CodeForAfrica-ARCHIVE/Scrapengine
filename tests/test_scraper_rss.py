"""
scrapengine/scrapers/rss.py tests
"""
import unittest
import requests
import feedparser
from Scrapengine.scrapers import rss as rss_scraper

class RssScraperTestCase(unittest.TestCase):
    
    def setUp(self,):
        from Scrapengine.configs import SCRAPERS
        self.rss_source = SCRAPERS['rss']['allafrica.com.africa']

    def test_get_source(self,):
        httpresp = requests.get(self.rss_source)
        self.assertTrue(httpresp.status_code == 200, msg="Cannot get %s. HTTP error %s" % (
            self.rss_source, str(httpresp.status_code)))
        del httpresp

        parsed = rss_scraper.get_source(self.rss_source)
        self.assertIsInstance(parsed, feedparser.FeedParserDict, msg="Unexpected object type %s for %s" %
                (type(parsed), parsed))
        self.parsed_response = parsed

    def test_response_attributes(self,):
        self.test_get_source()
        self.assertIn('feed', self.parsed_response)
        self.assertIn('entries', self.parsed_response)
        feed_metadata = self.parsed_response['feed']
        feed_entries = self.parsed_response['entries']
        for entry in feed_entries:
            self.assertIn('title', entry)
            self.assertIn('summary', entry)
            self.assertIn('link', entry)



if __name__ == '__main__':
    unittest.main()
