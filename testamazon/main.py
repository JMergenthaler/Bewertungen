import re
from scrapy import signals
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from amazon import call_spider
from ebay import ebay
from testamazon.spiders.trustpilot import TrustpilotSpider
import json
from test_mariadb import mariadb_add
from translate import Translate
from mariadb_ueberpruefen import datenbank_test
from bertaus import auswertung
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
    isneu = not neu[0]
    if isneu:
        run_spider_trust(link)
        Translate()
        bewertung = auswertung()
        mariadb_add(link, "",bewertung['fake'])
        
        #Tobi
    else:
        # Tobi
        pass

        

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
                    if match:
                        result = match.group()
                        print(result)
                        print(url)
                        print("______")
                        call_spider(url)
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
                    else:
                        print("Nicht Supportet")
                else:
                    print("No match found.")

read_file()