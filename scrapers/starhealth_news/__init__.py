"""
Scrape news articles from www.the-star.co.ke/api/mobile/views/mobile_app?args%5B0%5D=24&limit=3
"""
import os
import time
import requests
from Scrapengine.configs import ARCHIVE

SOURCE_URL = "http://www.the-star.co.ke/api/mobile/views/mobile_app?args[0]=24&limit=%s"
OUTPUTFILE = "starhealth_news-output"
DROPBOX_FOLDER = "starhealth-news"
DROPBOX_URL = "https://content.dropboxapi.com/2/files/upload"
DROPBOX_KEY = os.getenv("DROPBOX_API_KEY")


def get_articles(count=50):
    """
    return a `list` of articles from API
    """
    try:
        resp = requests.get(SOURCE_URL % count)
        resp.raise_for_status()
        return resp.json()
    except Exception, err:
        print "ERROR: get_articles() - %s" % str(err)
        return []


def output(articles, outputfile=OUTPUTFILE):
    try:
        file_fullpath = "%s/%s-%s.json" % (ARCHIVE, outputfile, time.time())
        _file = open(file_fullpath, "w")
        _file.write(str(articles))
        _file.close()
        return file_fullpath
    except Exception, err:
        print "ERROR: output() - %s" % str(err)
        raise err


def publish_output(file_to_upload):
    """
    upload the output file to Dropbox
    """
    try:
        x = file_to_upload.split("/")
        filename = x[len(x)-1] or x[len(x)-2]
        path_component = "{\"path\":\"/%s/%s\",\"mode\":{\".tag\":\"add\"},\"autorename\":false}" % (
                DROPBOX_FOLDER, filename)
        headers = { 
                "Authorization": "Bearer %s" % DROPBOX_KEY,
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": path_component
                }
        data = open(file_to_upload, "r").read()
        resp = requests.post(DROPBOX_URL, headers=headers, data=data)
        return resp.json()["path_display"]
    except Exception, err:
        print "ERROR: publish_output() - %s" % str(err)
        raise err


def main():
    articles = get_articles()
    outputfile = output(articles)
    return publish_output(outputfile)
