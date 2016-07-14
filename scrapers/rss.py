"""
RSS Scraper
"""
import feedparser
from Scrapengine.configs import SCRAPERS

def get_source(source):
    '''
    gets and parses rss feed from `source`
    `source` is a direct URL to the RSS feed
    '''
    parsed_response = feedparser.parse(source)
    return parsed_response
