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
"""
import requests
from bs4 import BeautifulSoup

MONTH_URL = "http://kenyalaw.org/kenya_gazette/gazette/month/{month}/{year}"
VOLUME_URL = "http://kenyalaw.org/kenya_gazette/gazette/volume"
PDF_URL = "http://kenyalaw.org/kenya_gazette/gazette/download"
OUTPUTFILE = "/tmp/ke_gazettes.txt"


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
        if url.startswith(PDF_URL):
            return url
    return None


def extract_volume_urls(html_page):
    """
    return all volume URLs on the page by going through all URLs on the page
    and filtering out those that don't match the volume URL structure / pattern

    returns empty list if no volume URLs are found
    """
    volume_urls = []
    soup = BeautifulSoup(html_page, "html.parser")
    page_urls = soup.find_all("a")
    for each in page_urls:
        url = each.get("href")
        if url.startswith(VOLUME_URL):
            volume_urls.append(url)
    return volume_urls


def openfile(filename):
    return open(filename, "a")

def write_to_file(fileobj, value):
    fileobj.write(str(value))


def main():
    outputfile = openfile(OUTPUTFILE)
    year = 2006
    while year <= 2016:
        month = 1
        while month <= 12:
            month_page = get_month_html(month, year)[0]
            volume_urls = extract_volume_urls(month_page)
            print "%s/%s - %s docs" % (month, year, len(volume_urls))
            for url in volume_urls:
                volume_page = get_volume_html(str(url).strip())[0]
                pdf_url = extract_pdf_url(volume_page)
                write_to_file(outputfile, pdf_url)
            
            print "Month %s/%s done" % (month, year)
            month += 1
        
        print "Year %s done" % year
        year += 1
    outputfile.close()
    return OUTPUTFILE
