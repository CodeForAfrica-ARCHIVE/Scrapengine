"""
scrapengine/scrapers/article.py tests
"""
import unittest
import requests
from Scrapengine.scrapers import article as article_scraper
from bs4 import BeautifulSoup

class ArticleScraperTestCase(unittest.TestCase):
    
    def setUp(self,):
        from Scrapengine.configs import SCRAPERS
        self.article_source = SCRAPERS['article']['100r']
        self.article_html = self._get_source_html()

    def _get_source_html(self,):
        return article_scraper.get_source_html(self.article_source)


    def test_get_source(self,):
        self.assertEqual(self.article_html.status_code, 200)


    def test_get_links(self,):
        links = article_scraper.get_links(self.article_html)
        self.assertIsInstance(links, list)

    def test_output(self,):
        self.skipTest("will come back to this")
        



if __name__ == '__main__':
    unittest.main()
