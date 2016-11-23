import csv, boto3, os
CLOUDSEARCH = os.getenv("NHIF_SEARCH_CREDS")
cl = boto3.client("cloudsearchdomain", **eval(CLOUDSEARCH))
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


def loop():
    with open('nhif.csv', 'rb') as csvfile:
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
            row[3],
            row[2]
            )
    resp = cl.upload_documents(
            documents=doc,
            contentType="application/json"
            )
    print "%s - %s - %s" % (row[0], row[3], resp.get("status"))

if __name__ == "__main__":
    loop()
