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
        self.parsed_response = self._get_source()

    def _get_source(self,):
        return rss_scraper.get_source(self.rss_source)
    
    def test_get_source(self,):
        # first check integrity of http source
        httpresp = requests.get(self.rss_source)
        self.assertTrue(httpresp.status_code == 200, msg="Cannot get %s. HTTP error %s" % (
            self.rss_source, str(httpresp.status_code)))
        del httpresp

        # check response type
        self.assertIsInstance(self.parsed_response,
                feedparser.FeedParserDict, msg="Unexpected object type %s for %s" %
                (type(self.parsed_response), self.parsed_response))

    def test_response_attributes(self,):
        self.assertIn('feed', self.parsed_response)
        self.assertIn('entries', self.parsed_response)
        feed_metadata = self.parsed_response['feed']
        feed_entries = self.parsed_response['entries']
        for entry in feed_entries:
            self.assertIn('title', entry)
            self.assertIn('summary', entry)
            self.assertIn('link', entry)

    def test_get_entries(self,):
        entries = rss_scraper.get_entries(self.parsed_response)
        for entry in entries:
            self.assertIsInstance(entry, dict)



if __name__ == '__main__':
    unittest.main()
