"""
largely inherited from:
    https://github.com/CodeForAfricaLabs/lsk_scrapers/blob/master/data/scrape.py
"""

import uuid, csv
import os, dataset, requests
from datetime import datetime
from urllib import quote
from Scrapengine.configs import DATABASE, ARCHIVE, SCRAPERS

API_KEY = os.getenv("IMPORTIO_API_KEY", "xx-yy-zz")
#API = "https://api.import.io/store/connector/_magic?url={url}&format=JSON&js=false&_apikey={apikey}&_apikey={apikey}"
API = "https://api.import.io/store/connector/_magic?url={url}&format=JSON&js=false&_apikey={apikey}"
SOURCE = SCRAPERS['lawyers_ke']['lsk']
PAGES = 204 # Get this from the site
TIMEOUT = 35 # Request timeout in seconds
PERSIST = False


class LSKScraper(object):
    def __init__(self, run_id):
        self.api = API
        self.apikey = API_KEY
        self.source = SOURCE
        self._id = run_id

        #self.db = dataset.connect("mysql://{username}:{password}@{host}".format(**DATABASE))

    def persist(self, json_data):
        '''
        save to db
        '''
        dbtable = self.db[DATABASE['table']]
        dbresp = dbtable.insert(json_data)
        print "db said %s for %s" % (str(dbresp), json_data)
    
    def scrape_page(self, page):
        try:
            args = dict(
                    url=quote(self.source % page),
                    apikey=self.apikey
                    )
            start = datetime.now()
            response = requests.get(self.api.format(**args), timeout=TIMEOUT)
            print "timer - http - %s seconds" % (datetime.now() - start).seconds
            response.raise_for_status()
            resp = response.json()
            results = resp['tables'][0]['results']
            skip_count = 0  # keep track of how many entries have been skipped
            for result in results:
                result['link_1'] = result.get('link_1', "-")
                try:
                    result['name'] = result['content_1']
                    result['number'] = result['content_2']
                    result.pop("link_2/_source")
                    result.pop("link_1/_source")
                    result.pop("link_1/_text")
                    result.pop("link_2/_text")
                    result.pop("link_2")
                    result.pop("content_1")
                    result.pop("content_2")

                    start = datetime.now()

                    if PERSIST:
                        # for DB
                        self.persist(result)
                        print "timer - db - %s seconds" % (datetime.now() - start).seconds


                except Exception, err:
                    skip_count += 1
                    print "(page %s): Skipped %s -- REASON: %s" % (page, result, str(err))
            return results, skip_count
        except Exception, err:
            print "ERROR: Failed to scrape data from page %s  -- %s" % (page, err)
            raise err

    def write(self, results=[]):
        outputfile = "%s/%s.csv" % (ARCHIVE, self._id)
        with open(outputfile, 'wa') as csvfile:
            outputwriter = csv.writer(csvfile, delimiter=",")
            for result in results:
                outputwriter.writerow([
                    _encode(result['name']),
                    _encode(result['number']),
                    _encode(result['value']),
                    _encode(result['link_1'])
                        ])
        csvfile.close()
        return outputfile


def _encode(_unicode):
    return _unicode.encode('utf-8')


def main():
    """
    Execute scraper
    """
    run_id = str(uuid.uuid4())
    lsk = LSKScraper(run_id)
    print "[%s]: START RUN ID: %s" % (datetime.now(), run_id)
    for page in range(1, PAGES+1):
        print "scraping page %s" % str(page)
        results = lsk.scrape_page(str(page))
        print "Scraped %s entries from page %s | Skipped %s entries" % (len(results[0]), page, results[1])
        saved = lsk.write(results[0])
        print "Written page %s to %s" % (page, saved)
    print "[%s]: STOP RUN ID: %s" % (datetime.now(), run_id)


if __name__ == "__main__":
    main()
