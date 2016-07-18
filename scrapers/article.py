"""
Article list scraper
"""
import requests
from bs4 import BeautifulSoup


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
