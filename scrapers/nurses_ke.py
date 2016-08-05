"""
Largely inherited from:
    https://github.com/CodeForAfricaLabs/nurses_ke/blob/master/data/scrape.py


Prepare list of common names. Save in file / redis
For name in names:
    - Search for each name on http://nckenya.com/services/search.php?p=1&s=paul
      -- This returns a web page with the entries that satisfy the search criteria
    - Scrape the web page to extract name + license number + expiry_date
    - Append the 2nd and 3rd names to the "names" master list
    - Repeat
"""

import os, sys, csv, requests
from requests.exceptions import ReadTimeout, HTTPError
from datetime import datetime
from urllib import urlencode, quote
from names import NAMES
from Scrapengine.configs import ARCHIVE

SOURCE = "http://nckenya.com/services/search.php?"
API = "https://api.import.io/store/connector/_magic?url={url}&format=JSON&js=false&_apikey={apikey}&_apikey={apikey}"
API_KEY = os.getenv("IMPORTIO_API_KEY")
OUTPUT_FILE = "%s/names-extra.csv" % ARCHIVE


class Scraper(object):

    def __init__(self):
        self.source = SOURCE
        self.api = API

    def search_by_name(self, name):
        '''
        use import-io to scrape search result from NCKenya
        - Use name as search query
        '''
        try:
            _name = name.strip().lower()
            searchurl = self.source + urlencode(dict(p=1, s=_name))
            args = dict(url=quote(searchurl), apikey=API_KEY)
            resp = requests.get(self.api.format(**args), timeout=4)
            resp.raise_for_status()
            return resp.json()
        except (ReadTimeout, HTTPError), exc:
            print "ERROR: HTTP Error for '%s' -- %s" % (name, exc)
            return dict(tables={})

    def _count(self, resp):
        if not resp.get('tables'):
            return 0
        return len(resp['tables'][0]['results'])

    def save(self, key, value):
        '''
        save `key` in redis with `value` ONLY if it does not already exist
        '''
        #_key = self.db_key_prefix + str(key)
        #saved = self.db.set(_key, value, nx=True)
        #print "REDIS - %s - %s" % (_key, saved)
        print "save ", key, value

    def persist(self,):
        '''
        save to disk
        '''
        pass
        #self.db.save()

    def get_by_license(self, license):
        '''
        return the name of the nurse with license number `license`
        if the license number does not exist, return `None`
        '''
        _key = self.db_key_prefix + str(license).strip()
        val = self.db.get(_key)
        return val or None



def scrape_by_name(name, save='off'):
    start_time = datetime.now()
    scraper = Scraper()
    result = scraper.search_by_name(name)
    count = scraper._count(result)
    if not count or count == 1:
        print "Found no results for %s" % name
        return []
    print "Found %s results for '%s'" % (count, name)

    results = result['tables'][0]['results']
    for result in results:
        try:
            nurse = dict(
                    name=result["name_value"],
                    license=result["license_number/_source"],
                    validity=result["validtill_date/_source"]
                    )
            print "{name} | {license} | {validity}".format(**nurse)
        except KeyError:
            print "ERROR: Unexpected scrape response format for '%s' -- %s " % (name, result)
            break

        # get 2nd + 3rd names - for new list
        names = result["name_value"].strip().split(" ")
        for n in names:
            if n.upper().strip() == str(name.upper()).strip():
                continue
            else:
                # add to new names list
                #print "Adding '%s' to new names list" % n
                with open(OUTPUT_FILE, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow([n])
        
    print "done in %s seconds" % (datetime.now() - start_time).seconds
    return results

    

def main(action, names_source, source_type="csv"):
    result_count = 0
    if action == "single":
        result = scrape_by_name(names_source)
        result_count += len(result)

    elif action == "all":
        if source_type == "list":
            statement = "from %s import NAMES"
            exec(statement % names_source)
            for name in NAMES:
                result = scrape_by_name(name)
                result_count += len(result)


        elif source_type == "csv":
            with open(names_source, 'rb') as recordsreader:
                records = csv.reader(recordsreader)
                for record in records:
                    result = scrape_by_name(record[0])
                    result_count += len(result)

    print "%s RESULTS" % result_count



if __name__ == "__main__":
    usage = "\n\n Usage:\n\n  python scrape.py single <NAME> \n  OR\n  python scrape.py all <name> <list/csv>\n\n"
    try:
        action = sys.argv[1]
        name = sys.argv[2]
    except:
        print usage
        sys.exit(2)

    if action == 'single':
        main(action, name)
    elif action == 'all':
        # argv[1]  -->  the action <all>
        # argv[2]  -->  name of a module containing a list called `NAMES`
        #               or
        #               name of a csv with a list of names on one column
        # argv[3]  -->  source type <list/csv>
        try:
            _type = sys.argv[3]
            assert _type in ('list', 'csv')
        except (IndexError, AssertionError):
            print usage
            sys.exit(2)
        if _type == 'list':
            statement = "from %s import NAMES"
            exec(statement % name)
            for each in NAMES:
                main('single', name)
        elif _type == 'csv':
            with open(name, 'rb') as recordsreader:
                records = csv.reader(recordsreader)
                for record in records:
                    main('single', name)
