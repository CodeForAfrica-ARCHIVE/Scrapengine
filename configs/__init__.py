import os

SCRAPERS = dict(
        rss={
            "allafrica.com.africa": "http://allafrica.com/tools/headlines/rdf/africa/headlines.rdf",
            "allafrica.com.asiaaustraliaafrica": "http://allafrica.com/tools/headlines/rdf/asiaaustraliaandafrica/headlines.rdf"
            },

        article={
            "100r": "https://100r.org/section/all-categories/page/4/",
            },
        lawyers_ke={
            "lsk": "http://online.lsk.or.ke/index.php/index.php?option=com_content&id=4&catid=8&qw=active&finder=Active&view=article&base=%s"
            },
        nurses_ke={
            "nck": "http://nckenya.com/services/search.php?"
            }
        )

ARCHIVE = os.getenv("SCRAPENGINE_ARCHIVE_PATH", ".")


db_host = os.getenv('SCE_MYSQL_KE', 'user,password,localhost:3306/scrapengine')
DATABASE = dict(
        username=db_host.split(',')[0],
        password=db_host.split(',')[1],
        host=db_host.split(',')[2],
        table='SCRAPENGINE'
        )
