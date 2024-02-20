import requests
import json
import regex as re
from translation_ebay import Translate_Ebay
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright
from datetime import datetime
from mariadb_ueberpruefen import datenbank_test
from test_mariadb import mariadb_add
from bertaus import auswertung
from tobi import zurueck
import re
from threading import Lock

def first_api_request(marke, itemid):
    review_url = f'https://www.ebay.com/fdbk/update_feedback_profile?url=username%3D{marke}%26sort%3DTIME%26filter%3Dfeedback_page%253ARECEIVED_AS_SELLER%252Cperiod%253AAll%252Cimage_filter%253Afalse%26q%3D{itemid}%26page_id%3D1%26limit%3D1000&module=modules%3DFEEDBACK_SUMMARY_V2'
    api_request(review_url)

def api_request(review_url):
    Path = './testamazon/json/s/'
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
            with open(Path + "review.json", "w") as f:
                json.dump(outputs, f)
        except:
            print(input_dict)
        
    else:
        print("API Zugriff fehlgeschlagen")
        print(f'Error: {response.status_code}') 


def noproductpage(url):
    regex = r'https:\/\/www\.ebay\.com\/fdbk\/feedback_profile\/([^?&\/]+).*?q=(\d+)'
    match = re.search(regex, url)
    regex2 = r'https:\/\/www\.ebay\.com\/fdbk\/feedback_profile\/([^?&\/]+)'
    match2 = re.search(regex2, url)
    if match != None:
        if match.group(1) != None and match.group(2) != None:
            marke = match.group(1)
            itemid = match.group(2)
            first_api_request(marke, itemid)
        elif match2 != None:
            marke = match.group(1)
            if marke != None:
                second_api_request(marke)
        else:
            print('Keine Produktbezogene Seite')
    elif match2 != None:
        marke = match2.group(1)
        if marke != None:
            second_api_request(marke)
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

def second_api_request(marke):
    review_url = f"https://www.ebay.com/fdbk/update_feedback_profile?url=username%3D{marke}%26sort%3DTIME%26filter%3Dfeedback_page%253ARECEIVED_AS_SELLER%252Cperiod%253AAll%252Cimage_filter%253Afalse%26page_id%3D1%26limit%3D1000&module=modules%3DFEEDBACK_SUMMARY_V2"
    api_request(review_url)

def itemid(url):
    regex = r'https:\/\/www\.ebay\.com\/fdbk\/feedback_profile\/([^?&\/]+).*?q=(\d+)'
    match = re.search(regex, url)
    regex2 = r'https:\/\/www\.ebay\.com\/fdbk\/feedback_profile\/([^?&\/]+)'
    match2 = re.search(regex2, url)
    if match != None:
        if match.group(1) != None and match.group(2) != None:
            marke = match.group(1)
            itemid = match.group(2)
            neu = datenbank_test("ebay", itemid)
            isneu = not neu[0]
            if isneu:
                first_api_request(marke,itemid)
                Translate_Ebay()
                bewertung = auswertung()
                fake = bewertung['Fake']
                mariadb_add("ebay", itemid, fake)
                return fake
            else:
                return neu[1]
        elif match2 != None:
            marke = match2.group(1)
            if marke != None:
                neu = datenbank_test("ebay", marke)
                isneu = not neu[0]
                if isneu:
                    second_api_request(marke)
                    Translate_Ebay()
                    bewertung = auswertung()
                    fake = bewertung['Fake']
                    mariadb_add("ebay", marke, fake)
                    return fake
                else:
                    return neu[1]
    elif match2 != None:
        marke = match2.group(1)
        if marke != None:
            neu = datenbank_test("ebay", marke)
            isneu = not neu[0]
            if isneu:
                second_api_request(marke)
                Translate_Ebay()
                bewertung = auswertung()
                fake = bewertung['Fake']
                mariadb_add("ebay", marke, fake)
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
        zurueck()

if __name__ == "__main__":
    ebay("https://www.ebay.com/fdbk/feedback_profile/quick2thrift?filter=feedback_page%3ARECEIVED_AS_SELLER&sort=RELEVANCE")