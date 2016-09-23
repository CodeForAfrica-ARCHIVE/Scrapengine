"""
scrapengine/scrapers/ke_gazette tests
"""
import random
import unittest
from Scrapengine.scrapers import ke_gazette
from Scrapengine.configs import ARCHIVE

class KEGazetteScraperTestCase(unittest.TestCase):
    
    def setUp(self,):
        self.foo = True
        self.month_resp = self._get_month_html()
        self.volume_urls = ke_gazette.extract_volume_urls(self.month_resp[0])
        self.volume_url = self.volume_urls[random.randint(0, len(self.volume_urls)-1)]
        self.volume_resp = ke_gazette.get_volume_html(self.volume_url)

    def _get_month_html(self, ):
        month = random.randint(1, 12)
        year = random.randint(2006, 2016)
        month_resp = ke_gazette.get_month_html(month, year)
        return month_resp

    def test_get_month_html(self, ):
        self.assertEqual(self.month_resp[1], 200)
        self.assertTrue("DOCTYPE html" in self.month_resp[0][0:20], msg="Doesn't look like an html file")

    def test_extract_volume_urls(self, ):
        self.assertIsInstance(self.volume_urls, list)
        if self.volume_urls:
            for url in self.volume_urls:
                self.assertTrue(url.startswith(ke_gazette.VOLUME_URL), msg="Doesn't look like a valid volume URL")

    def test_get_volume_html(self, ):
        self.assertEqual(self.volume_resp[1], 200)
        self.assertTrue("DOCTYPE html" in self.volume_resp[0][0:20], msg="Doesn't look like an html file")

    def test_extract_pdf_url(self, ):
        pdf_url = ke_gazette.extract_pdf_url(self.volume_resp[0])
        if pdf_url:
            self.assertTrue(pdf_url.startswith(ke_gazette.PDF_URL))
            self.assertTrue(pdf_url.endswith(".pdf"))



if __name__ == '__main__':
    unittest.main()
