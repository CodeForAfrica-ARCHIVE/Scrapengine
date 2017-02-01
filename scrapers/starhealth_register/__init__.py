"""
periodically pull the Kenya medical practitioners' database

Cron entry:
    @weekly source /alephdata/srv/env_scrapengine/bin/activate && cd /alephdata/srv/Scrapengine && make scrape scraper=starhealth-register-doctors && curl -fsS --retry 3 https://hchk.io/<ID> > /dev/null
    @weekly source /alephdata/srv/env_scrapengine/bin/activate && cd /alephdata/srv/Scrapengine && make scrape scraper=starhealth-register-foreign_doctors && curl -fsS --retry 3 https://hchk.io/<ID> > /dev/null
    @weekly source /alephdata/srv/env_scrapengine/bin/activate && cd /alephdata/srv/Scrapengine && make scrape scraper=starhealth-register-clinical_officers && curl -fsS --retry 3 https://hchk.io/<ID> > /dev/null
"""
import uuid, csv, boto3
import os, dataset, requests
from datetime import datetime
from urllib import quote
from Scrapengine.configs import DATABASE, ARCHIVE, SCRAPERS, CLOUDSEARCH_DOCS, CLOUDSEARCH_COS
from Scrapengine import index_template
from BeautifulSoup import BeautifulSoup

API_KEY = os.getenv("IMPORTIO_API_KEY", "xx-yy-zz")
API = "https://api.import.io/store/connector/_magic?url={url}&format=JSON&js=false&_apikey={apikey}"
SOURCE = dict(
        doctors=SCRAPERS["medicalboard"]["doctors"],
        foreign_doctors=SCRAPERS["medicalboard"]["foreign_doctors"],
        clinical_officers=SCRAPERS["medicalboard"]["clinical_officers"]
        )
TIMEOUT = 15 # Request timeout in seconds
PERSIST = False
OUTPUT_FILE_PREFIX = "starhealth_register"

def get_total_page_numbers(url, default_pages):
    try:
        r = requests.get(url % ('1')) # page one
        soup = BeautifulSoup(r.text)
        row = soup.find("div", {"id": "tnt_pagination"}).getText()
        start_text = "Viewing 1 of "
        i = row.index(start_text)
        start = i + len(start_text)
        end = row.index("pages.")
        return int(row[start:end].strip())
    except Exception, err:
        print "ERROR: get_total_page_numbers() - url: %s - err: %s" % (url, err)
        return default_pages

# Get this from the site
PAGES = dict(
        doctors=get_total_page_numbers(SCRAPERS["medicalboard"]["doctors"], 409),
        foreign_doctors=get_total_page_numbers(SCRAPERS["medicalboard"]["foreign_doctors"], 51),
        clinical_officers=get_total_page_numbers(SCRAPERS["medicalboard"]["clinical_officers"], 377)
        )

class MedicalBoardScraper(object):
    def __init__(self, run_id, source):
        self.api = API
        self.apikey = API_KEY
        self._id = run_id
        self.source = source
        self.source_url = SOURCE[source]
        self.cloudsearch_docs = boto3.client("cloudsearchdomain", **CLOUDSEARCH_DOCS)
        self.cloudsearch_cos = boto3.client("cloudsearchdomain", **CLOUDSEARCH_COS)
        self.fields = dict(
                doctors=dict(
                    name="name_value",
                    registration_number="regno_value",
                    qualification="qualifications_value",
                    address="address_value",
                    registration_date="regdate_date/_source",
                    specialty="specialty_value",
                    sub_specialty="sub_value"
                    ),
                foreign_doctors=dict(
                    name="name_value",
                    registration_number="licence_number/_source",
                    qualification="qualifications_value",
                    address="address_value",
                    facility="facility_value",
                    practice_type="practicetype_value",
                    ),
                clinical_officers=dict(
                    name="name_value",
                    registration_number="regnolicence_value",
                    qualification="qualifications_label",
                    address="address_value",
                    registration_date="regdate_value",
                    )
                )

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
                    url=quote(self.source_url % page),
                    apikey=self.apikey
                    )
            print "Getting page: %s" % args["url"]
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
                    for attr in self.fields[self.source]:
                        doctor_payload[attr] = result.get(self.fields[self.source][attr], "None")
                        doctor_payload["type"] = self.source

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

    def write_to_json(self, results=[]):
        """
        This function saves the data in a template ready for bulk addition or bulk deletion in json files.
        :param results:
        :return: a tuple of the file names
        """
        outputfile = "%s/%s-%s-%s-add.json" % (ARCHIVE, OUTPUT_FILE_PREFIX, self.source, self._id) #Serves as a record of items last uploaded
        deletefile = "%s/%s-%s-%s-delete.json" % (ARCHIVE, OUTPUT_FILE_PREFIX, self.source, self._id)
        with open(outputfile, 'a') as f, open(deletefile, 'a') as d:
            try:
                for i, item in enumerate(results):
                    item["id"] = item["registration_number"].strip().replace(" ", "")
                    item["type"] = self.source
                    deletion_index = item.get("id", "").encode('utf-8') + '\n'
                    d.write(deletion_index) #Save a list of
                    f.write(str(item))

            except Exception, err:
                print "ERROR - writing to json() - %s- %s - %s" % (outputfile, deletefile, err)
        return outputfile, deletefile

    def index_for_search(self, payload):
        try:
            payload_index = ''
            for i, item in enumerate(payload):
                item["id"] = item["registration_number"].strip().replace(" ", "")
                item["type"] = self.source
                payload_index += index_template.template % (
                        item.get("id", ""),
                        item.get("address", "").replace("\"","'"),
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
                if i < (len(payload) - 1): payload_index += ', '
            payload_index = '[%s]' % payload_index
            if self.source == 'clinical_officers':
                resp = self.cloudsearch_cos.upload_documents(
                    documents=payload_index, contentType="application/json"
                    )
            else:
                resp = self.cloudsearch_docs.upload_documents(
                    documents=payload_index, contentType="application/json"
                )
            print "DEBUG - index_for_search() - %s - %s" % (len(payload), resp.get("status"))
        except Exception, err:
            print "ERROR - index_for_search() - %s - %s" % (len(payload), err)

    def delete_records(self, file):
        with open(file, 'r') as f:
            rows = f.readlines()
            batches = list(self.chunkify(rows, 30))
            for batch in batches:
                no_of_items = len(batch)
                payload_index = ''
                for i, row in enumerate(batch):
                    row = row.replace('/n','').strip()
                    payload_index += index_template.delete_template % ( row )
                    if i < (len(batch) - 1): payload_index += ', '
                payload_index = '[%s]' % payload_index
                if self.source == 'clinical_officers':
                    resp = self.cloudsearch_cos.upload_documents(
                        documents=payload_index, contentType="application/json"
                    )
                else:
                    resp = self.cloudsearch_docs.upload_documents(
                        documents=payload_index, contentType="application/json"
                    )

                print "DEBUG - delete_records() - %s" % (resp.get("status"))
        os.remove(file)
        os.remove(file.replace('delete.json', 'add.json')) #To avoid loss of space
        return no_of_items

    def chunkify(self, l, n):
        n = max(1, n)
        return (l[i:i + n] for i in xrange(0, len(l), n))

def _encode(_unicode):
    return _unicode.encode('utf-8')

def main(source):
    """
    Execute scraper
    """
    run_id = str(uuid.uuid4())
    medboardscraper = MedicalBoardScraper(run_id, source)

    #Flush the repository off of old data if the delete.json file exists
    for file in os.listdir(ARCHIVE):
        if file.endswith("delete.json"):
            no_of_items_flushed = medboardscraper.delete_records(ARCHIVE + '/' + file)
            print "[%s]: FLUSHED CLOUDSEARCH : %s" % (datetime.now(), no_of_items_flushed)
            break

    doc_results = []
    print "[%s]: START RUN ID: %s" % (datetime.now(), run_id)
    for page in range(0, PAGES[source]+1):
        print "scraping page %s" % str(page)
        try:
            results = medboardscraper.scrape_page(str(page))
        except Exception, err:
            print "ERROR: main() - source: %s - page: %s - %s" % (source, page, err)
            continue
        print "Scraped %s entries from page %s | Skipped %s entries" % (len(results[0]), page, results[1])

        doc_results.extend(results[0])
        medboardscraper.index_for_search(doc_results)

    files = medboardscraper.write_to_json(doc_results)
    print "Written page %s to %s" % (page, files)
    print "[%s]: STOP RUN ID: %s" % (datetime.now(), run_id)


if __name__ == "__main__":
    pass
