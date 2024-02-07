import re
from testamazon.spiders.amazon import AmazonReviewsSpider
from scrapy.crawler import CrawlerProcess
import os
os.environ['SCRAPY_SETTINGS_MODULE'] = 'testamazon.settings'
from scrapy.utils.project import get_project_settings


def call_spider(link):
    asin = get_asin_ref(link)
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    process.crawl(AmazonReviewsSpider, asin=asin)
    process.start()
    



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