"""
periodically pull the Kenya medical practitioners' database
"""
import uuid, csv
import os, dataset, requests
from datetime import datetime
from urllib import quote
from Scrapengine.configs import DATABASE, ARCHIVE, SCRAPERS

API_KEY = os.getenv("IMPORTIO_API_KEY", "xx-yy-zz")
#API = "https://api.import.io/store/connector/_magic?url={url}&format=JSON&js=false&_apikey={apikey}&_apikey={apikey}"
API = "https://api.import.io/store/connector/_magic?url={url}&format=JSON&js=false&_apikey={apikey}"
SOURCE = SCRAPERS['medicalboard']['doctors']
PAGES = 276 # Get this from the site
TIMEOUT = 15 # Request timeout in seconds
PERSIST = False
OUTPUT_FILE_PREFIX = "starhealth_register"


class MedicalBoardScraper(object):
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
            print "GETting page: %s" % args["url"]
            start = datetime.now()
            response = requests.get(self.api.format(**args), timeout=TIMEOUT)
            print "timer - http - %s seconds to GET %s" % ((datetime.now() - start).seconds, args["url"])
            response.raise_for_status()
            resp = response.json()
            results = resp['tables'][0]['results']

            skip_count = 0  # keep track of how many entries have been skipped
            all_entries = []
            for result in results:
                try:
                    doctor_payload = {}
                    doctor_payload["name"] = result.get("name_value", "None")
                    doctor_payload["registration_number"] = result.get("regno_value", "None")
                    doctor_payload["qualification"] = result.get("qualifications_value", "None")
                    doctor_payload["registration_date"] = result.get("regdate_date/_source", "None")
                    doctor_payload["address"] = result.get("address_value", "None")
                    doctor_payload["specialty"] = result.get("specialty_value", "None")
                    doctor_payload["sub_specialty"] = result.get("sub_value", "None")
                    start = datetime.now()

                    if PERSIST:
                        # for DB
                        self.persist(result)
                        print "timer - db - %s seconds" % (datetime.now() - start).seconds

                    all_entries.append(doctor_payload)

                except Exception, err:
                    skip_count += 1
                    print "ERROR: (page %s): Skipped %s -- REASON: %s" % (page, result, str(err))

            return all_entries, skip_count
        except Exception, err:
            print "ERROR: Failed to scrape data from page %s  -- %s" % (page, err)
            raise err

    def write(self, results=[]):
        outputfile = "%s/%s-%s.csv" % (ARCHIVE, OUTPUT_FILE_PREFIX, self._id)
        with open(outputfile, 'a') as csvfile:
            outputwriter = csv.writer(csvfile, delimiter=",")
            for result in results:
                outputwriter.writerow([
                    _encode(result['name']),
                    _encode(result['registration_number']),
                    _encode(result['registration_date']),
                    _encode(result['qualification']),
                    _encode(result["specialty"]),
                    _encode(result["sub_specialty"]),
                    _encode(result["address"])
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
    medboardscraper = MedicalBoardScraper(run_id)
    print "[%s]: START RUN ID: %s" % (datetime.now(), run_id)
    for page in range(0, PAGES+1):
        print "scraping page %s" % str(page)
        results = medboardscraper.scrape_page(str(page))
        print "Scraped %s entries from page %s | Skipped %s entries" % (len(results[0]), page, results[1])
        saved = medboardscraper.write(results[0])
        print "Written page %s to %s" % (page, saved)
    print "[%s]: STOP RUN ID: %s" % (datetime.now(), run_id)


if __name__ == "__main__":
    main()
