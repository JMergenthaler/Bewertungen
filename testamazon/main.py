import re
from scrapy import signals
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from amazon import amazon_bewertung
from new_ebay import ebay
from testamazon.spiders.trustpilot import TrustpilotSpider
import json
from test_mariadb import mariadb_add
from translate import Translate
from mariadb_ueberpruefen import datenbank_test
from bertaus import auswertung
from tobi import zurueck
from lidl import lidl
from thomann import thomann
from otto import otto
from nike import nike

os.environ['SCRAPY_SETTINGS_MODULE'] = 'testamazon.settings'
from scrapy.utils.project import get_project_settings

# save this as app.py

def run_trust_spider(link):
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    process.crawl(TrustpilotSpider, start_url=link)
    process.start()

def run_spider_trust(link):
    neu = datenbank_test(link, "")
    if not neu:
        run_trust_spider(link)
        Translate()
        bewertung = auswertung()
        mariadb_add(link, "",bewertung['Fake'])
        
        zurueck()
    else:
        zurueck()

        

def read_file():
    directory = "testamazon\\json\\"

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                if data:
                    link = data[0].get('link', '')
                    url = link
                else:
                    print("No data in the JSON.")
                    return

                regex = r"https:\/\/([\w.-]+)"

                match = re.search(regex, url)
                print(url)
                if match:
                    result = match.group(1)
                    regex_am_de = r"amazon"
                    match = re.search(regex_am_de, result)
                    regex_trust = r"trustpilot" 
                    match2 = re.search(regex_trust, result)
                    regex_ebay = r"ebay" 
                    match3 = re.search(regex_ebay, result)
                    regex_lidl = r'lidl'
                    match4 = re.search(regex_lidl, result)
                    regex_thomann = r'thomann'
                    match5 = re.search(regex_thomann, result)
                    regex_otto = r'otto'
                    match6 = re.search(regex_otto, result)
                    regex_nike = r'nike'
                    match7 = re.search(regex_nike, result)
                    if match:
                        result = match.group()
                        print(result)
                        print(url)
                        print("______")
                        amazon_bewertung(url)
                        #nextstep()
                    elif match2:
                        result = match2.group()
                        print(result)
                        print("______")
                        run_spider_trust(url)
                        #nextstep()
                    elif match3:
                        result = match3.group()
                        print(result)
                        print("______")
                        ebay(url)
                    elif match4:
                        result = match4.group()
                        print(result)
                        print("-------")
                        lidl(url)
                    elif match5:
                        result = match5.group()
                        print(result)
                        print("-------")
                        thomann(url, './testamazon/json/s/review.json')
                    elif match6:
                        result = match6.group()
                        print(result)
                        print("-------")
                        otto(url, './testamazon/json/s/review.json')
                    elif match7:
                        result = match7.group()
                        print(result)
                        print("-------")
                        nike(url, './testamazon/json/s/')
                        
                    else:
                        print("Nicht Supportet")
                else:
                    print("No match found.")

if __name__ == "__main__":
    read_file()