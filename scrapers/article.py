"""
Article list scraper
"""
import time
import csv
import requests
from bs4 import BeautifulSoup
from Scrapengine.configs import ARCHIVE


def get_source_html(source):
    """
    return the http body and status code

    @source:  URL to the article list
    """
    response = requests.get(source)
    return (response.content, response.status_code)


def get_links(html):
    """
    return a list of links in the html

    @html:   HTML markup
    """
    try:
        parsed = BeautifulSoup(html[0], "html.parser")
        links = parsed.find_all('a')
        return links
    except Exception, err:
        print "ERROR: scrapers.article.get_links() - %s" % err
        raise err


def _filter(links, _format='100r'):
    """
    filter out links that don't fit into `_format`

    @links:   List of http links
    @_format: Article link format

    Returns `links` without unwanted links
    """
    clean_list = {}
    for link in links:
        try:
            sections = str(link.get('href')).split("/")
            assert sections[0].startswith('http')
            assert sections[3].startswith('20')
            assert sections[4].isdigit()
            assert link.get('title')
            clean_list[link.get('href').strip()] = dict(
                    title=link.get('title'))
        except (AssertionError, IndexError):
            continue
    return clean_list


def output(links, source=""):
    """
    generates output file

    @links: dict with key as the url and value is a dict with other article
            attributes
    """
    outputfile = "%s/article-%s-output-%s.csv" % (ARCHIVE, source, time.time())
    with open(outputfile, 'wa') as csvfile:
        outputwriter = csv.writer(csvfile, delimiter="#")
        for entry in links:
            outputwriter.writerow(
                    [
                        _encode(entry),
                        _encode(links[entry]['title'])
                        ]
                    )

    csvfile.close()
    return outputfile


def _encode(_unicode):
    return _unicode.encode('utf-8')
