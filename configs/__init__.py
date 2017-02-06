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
            },
        medicalboard={
            "doctors": "http://medicalboard.co.ke/online-services/retention/?currpage=%s",
            "foreign_doctors": "http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage=%s",
            "clinical_officers": "http://clinicalofficerscouncil.org/online-services/retention/?currpage=%s"
            },
        sen_companies={
            "registrar": "http://creationdentreprise.sn/rechercher-une-societe?field_rc_societe_value=&field_ninea_societe_value=&denomination=&field_localite_nid=All&field_siege_societe_value=&field_forme_juriduqe_nid=All&field_secteur_nid=All&field_date_crea_societe_value=&page=%s"
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

#Doctors domain
CLOUDSEARCH=dict(
        endpoint_url="https://doc-starhealth-register-ofeurvl5vjhloserbvjnzhypmy.eu-west-1.cloudsearch.amazonaws.com",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
        )

#Doctors domain
CLOUDSEARCH_DOCS=dict(
        endpoint_url="https://doc-doctor-register-ke-ec4lclx2pcfn76nt26xreyxmee.eu-west-1.cloudsearch.amazonaws.com",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
        )
#Clinical officers domain
CLOUDSEARCH_COS=dict(
        endpoint_url="https://doc-clinical-officer-register-ke-ai5gut3aumxdpynvchhvgr4yfe.eu-west-1.cloudsearch.amazonaws.com",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
        )
HEALTH_FACILITIES_CLOUDSEARCH_DOMAIN=dict(
        endpoint_url="",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
        )