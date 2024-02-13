import requests
import json
import regex as re
from translation_ebay import Translate_Ebay
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright
from datetime import datetime
from mariadb_ueberpruefen import datenbank_test
import pytz
from test_mariadb import mariadb_add
from bertaus import auswertung
import re
from threading import Lock


def api_request(marke, itemid):
    review_url = f'https://www.ebay.com/fdbk/update_feedback_profile?url=username%3D{marke}%26sort%3DTIME%26filter%3Dfeedback_page%253ARECEIVED_AS_SELLER%252Cperiod%253AAll%252Cimage_filter%253Afalse%26q%3D{itemid}%26page_id%3D1%26limit%3D1000&module=modules%3DFEEDBACK_SUMMARY_V2'
    print(review_url)
    response = requests.get(review_url)

    if response.status_code == 200:
        # Parse the JSON response
        input_dict = response.json() 
        #rating = []
        outputs = []
        try:
            for x in input_dict['modules']['FEEDBACK_SUMMARY_V2']['feedbackView']['feedbackCards']:
                #rating.append(x['feedbackInfo']['rating']['name'])
                text = x['feedbackInfo']['comment']['accessibilityText']
                outputs.append({"review": text.strip()})
            with open("ebay.json", "w") as f:
                json.dump(outputs, f)
        except:
            print(input_dict)
        
    else:
        print("API Zugriff fehlgeschlagen")
        print(f'Error: {response.status_code}') 


def noproductpage(url):
    regex = r'https:\/\/www\.ebay\.com\/fdbk\/feedback_profile\/([^?&\/]+).*?q=(\d+)'
    match = re.search(regex, url)
    if match != None:
        marke = match.group(1)
        itemid = match.group(2)
        if marke != None or itemid != None:
            api_request(marke, itemid)
        else:
            print("Not the right page")
    else:
        print('Keine Produktbezogene Seite')


lock = Lock()

def ebay_pro(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            
        )

        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        # Acquire the lock before making the request
        with lock:
            page.goto(url=url, timeout=60000)
            button_selector = 'a.fake-btn.fake-btn--large.fake-btn--secondary'
            buttons = page.query_selector_all(button_selector)
            print(buttons)
            if len(buttons) == 0:
                print("hallo Welt")
            else:
                for button in buttons:
                    href = button.get_attribute('href')
                    noproductpage(href)

        browser.close()


def itemid(url):
    regex = r'https:\/\/www\.ebay\.com\/fdbk\/feedback_profile\/([^?&\/]+).*?q=(\d+)'
    match = re.search(regex, url)
    if match != None:
        marke = match.group(1)
        itemid = match.group(2)
        if marke != None or itemid != None:
            neu = datenbank_test("ebay", itemid)
            isneu = not neu[0]
            if isneu:
                api_request(marke,itemid)
                Translate_Ebay()
                bewertung = auswertung()
                fake = bewertung['Fake']
                mariadb_add("ebay", itemid, fake)
                return fake
            else:
                return neu[1]
    return produkt

def produkt(url):
    match = re.search(r"itm\/(\d+)", url)
    if match:
        itemid = match.group(1)
        neu = datenbank_test("ebay", itemid)
        isneu = not neu[0]
        if isneu:
            ebay_pro()
            Translate_Ebay()
            bewertung = auswertung()
            fake = bewertung['Fake']
            mariadb_add("ebay", itemid, fake)
            return fake
        else:
            return neu[1]
    return None


def ebay(url):
    fake = itemid(url)
    if fake != None:
        # Tobi
        pass
        
    


#url = "https://www.ebay.com/itm/202072206777?_trkparms=amclksrc%3DITM%26aid%3D777008%26algo%3DPERSONAL.TOPIC%26ao%3D1%26asc%3D20230823115209%26meid%3Db01cca98f0e244f18de655845a87062e%26pid%3D101800%26rk%3D1%26rkt%3D1%26itm%3D202072206777%26pmt%3D1%26noa%3D1%26pg%3D4375194%26algv%3DRecentlyViewedItemsV2SignedOut&_trksid=p4375194.c101800.m5481&_trkparms=parentrq%3A843b3cab18d0acf396dd1eceffff2440%7Cpageci%3A5d834461-c5cf-11ee-bafd-e2472d9809e6%7Ciid%3A1%7Cvlpname%3Avlp_homepage"
#ebay(url)
        

        
    



#ebay("https://www.ebay.com/itm/166441075580?_trkparms=amclksrc%3DITM%26aid%3D777008%26algo%3DPERSONAL.TOPIC%26ao%3D1%26asc%3D20230811153211%26meid%3Defb30b16ffd249c1933b5373994096bb%26pid%3D101775%26rk%3D1%26rkt%3D1%26itm%3D166441075580%26pmt%3D0%26noa%3D1%26pg%3D4375194%26algv%3DPersonalizedTopicsV2WithDynamicSizeRanker&_trksid=p4375194.c101775.m47269&_trkparms=parentrq%3A7379872318d0ab4c13c629f4fffe2c36%7Cpageci%3Acebf710b-c340-11ee-befa-aa9f8a5c38bf%7Ciid%3A2%7Cvlpname%3Avlp_homepage")
#Translate_Ebay()
