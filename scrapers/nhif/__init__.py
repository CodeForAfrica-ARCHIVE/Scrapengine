import csv, boto3, os
CLOUDSEARCH = os.getenv("NHIF_SEARCH_CREDS")
cl = boto3.client("cloudsearchdomain", **eval(CLOUDSEARCH))
file_location = "scrapers/nhif/nhif.csv"
print "cloud search client initiated - %s" % cl

nhif_template = """
[
 {"type": "add",
  "id":   "FACILITY-ID-%s",
  "fields": {
      "county": "%s",
      "county_facility_id": "%s",
      "county_id": "%s",
      "name": "%s",
      "service_point": "%s"
  }
 }
]
"""


def main(file_location=file_location):
    with open(file_location, 'rb') as csvfile:
        filereader = csv.reader(csvfile)
        for row in filereader:
            index(row)


def index(row):
    print "Indexing %s" % row[0]
    doc = nhif_template % (
            row[0],
            row[5],
            row[1],
            row[4],
            unicode(row[3], 'utf-8'),
            unicode(row[2], 'utf-8')
            )
    resp = cl.upload_documents(
            documents=doc,
            contentType="application/json"
            )
    print "%s - %s - %s" % (row[0], unicode(row[3], 'utf-8'), resp.get("status"))

if __name__ == "__main__":
    main()
