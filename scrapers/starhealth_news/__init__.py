"""
Scrape news articles from www.the-star.co.ke/api/mobile/views/mobile_app?args[0]=24&limit=3
"""
import os
import sys
import boto
import time
import requests
from boto.s3.key import Key
from Scrapengine.configs import ARCHIVE

SOURCE_URL = "http://www.the-star.co.ke/api/mobile/views/mobile_app?args[0]=24&limit=%s"
OUTPUTFILE = "starhealth_news-output"
AWS_API_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_API_SECRET = os.getenv("AWS_SECRET_KEY")
S3_BUCKET_NAME = "starhealth-news-dump"


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


def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


def publish_output(file_to_upload):
    """
    upload output file to S3
    """
    try:
        x = file_to_upload.split("/")
        filename = x[len(x)-1] or x[len(x)-2]
        conn = boto.connect_s3(AWS_API_KEY, AWS_API_SECRET)
        bucket = conn.get_bucket(S3_BUCKET_NAME)
        k = Key(bucket)
        k.key = filename
        resp = k.set_contents_from_filename(file_to_upload, cb=percent_cb, num_cb=10)
        return resp

    except Exception, err:
        print "ERROR: publish_output() - %s" % str(err)
        raise err

def main():
    articles = get_articles()
    outputfile = output(articles)
    return publish_output(outputfile)
