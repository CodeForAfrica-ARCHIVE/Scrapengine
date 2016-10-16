"""
http://www.kenyalaw.org/kenya_gazette/

Source: http://www.kenyalaw.org/kenya_gazette/

Archive: 2006 - 2016

Page source: http://kenyalaw.org/kenya_gazette/gazette/month/{month}/{year}
e.g. http://kenyalaw.org/kenya_gazette/gazette/month/1/2006

Volume URL: http://kenyalaw.org/kenya_gazette/gazette/volume/MTA2OQ--/Vol.%20CVIII-No.1  
Download URL: http://kenyalaw.org/kenya_gazette/gazette/download/Vol._CVIII-No_._1_.pdf

- Loop through years
  - Loop through months in each year
    - Get month HTML
    - Extract volume URLs
    - Loop through volume URLs
      - Get volume HTML
      - Extract Download URL
      - Download PDF


- Cron:
    30 23 * * Sun source /alephdata/srv/env_scrapengine/bin/activate && cd /alephdata/srv/Scrapengine && make scrape scraper=ke-gazette xargs=1/2016 && curl -fsS --retry 3 https://hchk.io/a225fd72-74ae-45cb-96b9-8d3d753b3f82 > /dev/null
    30 22 * * Mon bash -x /alephdata/srv/Scrapengine/scrapers/ke_gazette/download.sh
    30 23 * * Mon cd /alephdata/srv/data/sources/kenya/ke-gazette && cat /tmp/ke_gazettes.txt | bash -x 
"""
import requests
from bs4 import BeautifulSoup

MONTH_URL = "http://kenyalaw.org/kenya_gazette/gazette/month/{month}/{year}"
VOLUME_URL = "http://kenyalaw.org/kenya_gazette/gazette/volume"
PDF_URL = "http://kenyalaw.org/kenya_gazette/gazette/download"
OUTPUTFILE = "/tmp/ke_gazettes.txt"
FILE_NAME_SCHEME = "OpenGazettes | Kenya | {volume_name} ( {volume_date} )"


def get_month_html(month, year):
    """
    return 1) the html of the month page or None and 2) the requests.status_code
    """
    resp = requests.get(MONTH_URL.format(month=month, year=year))
    return resp.text, resp.status_code


def get_volume_html(volume_url):
    """
    return 1) the html of the volume page or None and 2) the requests.status_code
    """
    resp = requests.get(volume_url)
    return resp.text, resp.status_code

def extract_pdf_url(volume_page):
    """
    return PDF download URLs from the volume page or None if PDF download URL does not exist
    """
    soup = BeautifulSoup(volume_page, "html.parser")
    page_urls = soup.find_all("a")
    for each in page_urls:
        url = each.get("href")
        if not url:
            break
        if url.startswith(PDF_URL):
            return url
    return None


def extract_volume_urls_and_dates(html_page):
    """
    return all volume URLs and associated dates on the page by going through
    all URLs and filtering out those that don't match the volume URL 
    structure / pattern

    returns empty list if no volume URLs are found
    """
    volume_urls = []
    soup = BeautifulSoup(html_page, "html.parser")
    page_urls = soup.find_all("tr")
    for each in page_urls:
        url_ = each.find("a")
        if not url_:
            continue
        url = str(url_.get("href"))
        attributes = each.find_all("td")
        volume_date = attributes[len(attributes)-1].children.next()

        if url.startswith(VOLUME_URL):
            volume_urls.append(dict(url=str(url).strip(), volume_date=str(volume_date)))
    return volume_urls


def openfile(filename):
    return open(filename, "a")

def write_to_file(fileobj, value):
    try:
        fileobj.write(str(value).encode('utf-8'))
        fileobj.write("\n")
    except UnicodeEncodeError:
        print "ERROR: %s" % value


def main(xargs):
    if xargs:
        try:
            start_month = int(xargs.split("/")[0])
            start_year = int(xargs.split("/")[1])
        except Exception, err:
            print "ERROR: Unknown arguments for month and year: %s. Use format 1/2009 to start at January 2009" % xargs
            raise err
    else:
        start_month = 1
        start_year = 2006

    outputfile = openfile(OUTPUTFILE)
    year = start_year
    while year <= 2016:
        month = start_month
        while month <= 12:
            month_page = get_month_html(month, year)[0]
            volume_urls = extract_volume_urls_and_dates(month_page)
            print "%s/%s - %s docs" % (month, year, len(volume_urls))
            for url_objs in volume_urls:
                url = url_objs["url"]
                date = url_objs["volume_date"]
                print "*" * 40
                print url
                volume_page = get_volume_html(url.strip())[0]
                pdf_url = extract_pdf_url(volume_page)
                write_to_file(outputfile, pdf_url)
            
            print "Month %s/%s done" % (month, year)
            month += 1
        
        print "Year %s done" % year
        year += 1
    outputfile.close()
    return OUTPUTFILE
