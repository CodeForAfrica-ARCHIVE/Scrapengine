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
            clean_list[link.get('href').strip()] = link.get('title')
        except (AssertionError, IndexError):
            continue
    return clean_list





