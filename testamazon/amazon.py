import re
from testamazon.spiders.amazon import AmazonReviewsSpider
from scrapy.crawler import CrawlerProcess
import os
from mariadb_ueberpruefen import datenbank_test
from translate import Translate
from test_mariadb import mariadb_add
from tobi import zurueck
from bertaus import auswertung
os.environ['SCRAPY_SETTINGS_MODULE'] = 'testamazon.settings'
from scrapy.utils.project import get_project_settings


def amazon_bewertung(url):
    asin, neu = call_spider(url)
    if asin:
        if not neu[0]:
            Translate()
            bewertung = auswertung()
            mariadb_add("amazon", asin, bewertung)
            zurueck()
        else:
            
            bewertung = neu[1]
            zurueck()


def call_spider(link):
    neu = None
    neu = None
    asin = get_asin_ref(link)
    if asin != None:
        neu = datenbank_test("amazon",asin)
        isneu = not neu[0]
        if isneu:
            settings = get_project_settings()
            process = CrawlerProcess(settings)
            process.crawl(AmazonReviewsSpider, asin=asin)
            process.start()
    return asin, neu



def get_asin_ref(link):
    regex = r'\/product-reviews\/([A-Z0-9]+)'
    match = re.search(regex, link)
    try:
        asin = match.group(1)
        return asin
    except:
        return get_asin_pro(link)
    
def get_asin_pro(link):
    regex = r'\/dp\/([A-Z0-9]+)'
    match = re.search(regex, link)
    try:
        asin = match.group(1)
        return asin
    except:
        return None