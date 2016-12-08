"""
periodically pull the Kenya medical practitioners' database

"""
import uuid, csv, boto3
import os, dataset, requests
from datetime import datetime
from urllib import quote
from Scrapengine.configs import DATABASE, ARCHIVE, SCRAPERS, CLOUDSEARCH
from Scrapengine import index_template

API_KEY = os.getenv("IMPORTIO_API_KEY", "xx-yy-zz")
API = "https://api.import.io/store/connector/_magic?url={url}&format=JSON&js=false&_apikey={apikey}"

PAGES = 1217  # Get this from the site
TIMEOUT = 15 # Request timeout in seconds
PERSIST = False
OUTPUT_FILE_PREFIX = "sen-companies-"


class CompaniesRegisterScraper(object):
    def __init__(self, run_id):
        self.api = API
        self.apikey = API_KEY
        self._id = run_id
        self.source_url = SCRAPERS["sen_companies"]["registrar"]
        #self.cloudsearch = boto3.client("cloudsearchdomain", **CLOUDSEARCH)
        self.fields = dict(
                name="dnomination_link/_text",
                head_office="sigesocial_value",
                creation_date="datecration_value",
                link="dnomination_link",
                )

    
    def scrape_page(self, page):
        try:
            args = dict(
                    url=quote(self.source_url % page),
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
                print "res - %s" % result
                try:
                    company_payload = {}
                    for attr in self.fields:
                        company_payload[attr] = result.get(self.fields[attr], "None")
                    all_entries.append(company_payload)
                except Exception, err:
                    skip_count += 1
                    print "ERROR: (page %s): Skipped %s -- REASON: %s" % (page, result, str(err))

            return all_entries, skip_count
        except Exception, err:
            print "ERROR: Failed to scrape data from page %s  -- %s" % (page, err)

    def write(self, results=[]):
        outputfile = "%s/%s-%s.csv" % (ARCHIVE, OUTPUT_FILE_PREFIX, self._id)
        with open(outputfile, 'a') as csvfile:
            outputwriter = csv.writer(csvfile, delimiter=",")
            for result in results:
                attrs = []
                for attr in self.fields:
                    attrs.append(_encode(result[attr]))
                outputwriter.writerow(attrs)
        csvfile.close()
        return outputfile

    def index_for_search(self, payload):
        try:
            for item in payload:
                item["id"] = item["registration_number"].strip().replace(" ", "")
                item["type"] = self.source
                payload_index = index_template.template % (
                        item.get("id", ""),
                        item.get("address", ""),
                        item.get("facility", ""),
                        item.get("name", ""),
                        item.get("practice_type", ""),
                        item.get("qualification", ""),
                        item.get("registration_date", ""),
                        item.get("registration_number", ""),
                        item.get("specialty", ""),
                        item.get("sub_specialty", ""),
                        item.get("type", "")
                        )
                resp = self.cloudsearch.upload_documents(
                        documents=payload_index, contentType="application/json"
                        )
                print "DEBUG - index_for_search() - %s - %s" % (item, resp.get("status"))
        except Exception, err:
            print "ERROR - index_for_search() - %s - %s" % (payload, err)


def _encode(_unicode):
    return _unicode.encode('utf-8')


def main():
    """
    Execute scraper
    """
    run_id = str(uuid.uuid4())
    companyscraper = CompaniesRegisterScraper(run_id)
    print "[%s]: START RUN ID: %s" % (datetime.now(), run_id)
    for page in range(0, PAGES):
        print "scraping page %s" % str(page)
        try:
            results = companyscraper.scrape_page(str(page))
        except Exception, err:
            print "ERROR: main() - source: %s - page: %s - %s" % (source, page, err)
            continue
        print "Scraped %s entries from page %s | Skipped %s entries" % (len(results[0]), page, results[1])
        saved = companyscraper.write(results[0])
        print "Written page %s to %s" % (page, saved)
        #indexed = companyscraper.index_for_search(results[0])
    print "[%s]: STOP RUN ID: %s" % (datetime.now(), run_id)


if __name__ == "__main__":
    pass
