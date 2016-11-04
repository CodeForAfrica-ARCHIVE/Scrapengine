"""
Source: http://www.saflii.org/na/other/NAGovGaz/

Archive: 1990 - 2007

Root: http://www.saflii.org/na/other/NAGovGaz/
 |
  -Year page:  http://www.saflii.org/na/other/NAGovGaz/{year}
   |
   - Document page:  http://www.saflii.org/na/other/NAGovGaz/{year}/{ID}.pdf


- Loop through years:
  - Extract document URLs
  - Download PDF

"""
import requests
from bs4 import BeautifulSoup

YEAR_URL = "http://www.saflii.org/na/other/NAGovGaz/{year}"
PDF_URL = "http://www.saflii.org/na/other/NAGovGaz/{year}/{ID}.pdf"
OUTPUTFILE = "/tmp/na_gazettes.txt"
FILE_NAME_SCHEME = "OpenGazettes | Namibia | %s ( %s )"
START_YEAR = 1990
END_YEAR = 2007

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
    """
    write content `value` to file `fileobj` and append a newline
    """
    try:
        fileobj.write(str(value).encode('utf-8'))
        fileobj.write("\n")
    except UnicodeEncodeError:
        print "ERROR: %s" % value

def exists(url):
    """
    returns True if page is found; else False
    """
    return True if requests.get(url) else False

def main():
    """
    1. Loop through all pages (years) and hold onto the raw PDF URLs
    2. Loop through the raw PDF URLs and write each as a newline in the CSV output file
    Return the output file
    """
    all_gazette_documents = []
    start_year = START_YEAR
    outputfile = openfile(OUTPUTFILE)
    year = start_year
    id_ = 1
    while year <= END_YEAR:
        # Looop through until you get a 404
        raw_document = PDF_URL.format(year=year, ID=id_)
        valid = exists(raw_document)
        print "%s - %s - %s" % (year, raw_document, valid)
        id_ += 1
        if valid:
            # write to file
            all_gazette_documents.append(raw_document)
        else:
            # 404. Move to next year
            print "%s documents from %s" % (id_-1, year)
            year += 1
            id_ = 1

    for url in all_gazette_documents:
        default_name = url.split("/").pop()
        custom_file_name = FILE_NAME_SCHEME % (default_name, date)
        write_content = """wget %s -O "%s.pdf" """ % (pdf_url, custom_file_name)
        write_to_file(outputfile, write_content)

    outputfile.close()
    return OUTPUTFILE
