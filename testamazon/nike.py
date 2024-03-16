import requests
import json
import re
from translate import Translate
from bertaus import auswertung
from test_mariadb import mariadb_add
from mariadb_ueberpruefen import datenbank_test
from tobi import zurueck

def get_itemid(url):
    regex = r'https:\/\/www\.nike\.com\/[a-z]{2}\/t\/([\w\-]+)\/(\w+)'
    match = re.search(regex, url)
    if match != None and match.group(2) != None:
        return match.group(2)

def get_reviews(itemid,filepath):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    response = requests.get(f'https://cdn-ws.turnto.com/v5/sitedata/hwf2R4pYhl2NYnKsite/{itemid}/d/review/de_DE/0/100/%7B%7D/RECENT/true/false/', headers=headers)

    if response.status_code == 200:
        try:
            page_data = response.json()
            reviews = []
            for review in page_data['reviews']:
                text = review['text']
                title = review['title']
                rating = review['rating']
                attributs = review['catItem']['attributes']
                brand = ""
                producttype = ""
                for attribut in attributs:
                    if attribut['label'] == 'Brand':
                        brand = attribut['value']
                    if attribut['label'] == 'ProductType':
                        producttype = attribut['value']
                reviews.append({'title': title, 'rating': rating, 'text': text, 'indicator': producttype + brand})
                with open(filepath + "review.json", "w") as f:
                    json.dump(reviews, f)
        except:
            print("Wrong page")

def nike(url, filepath, configpath):
    itemid = get_itemid(url)
    neu = datenbank_test("nike", itemid, filepath, configpath)
    if not neu:
        get_reviews(itemid, filepath)
        Translate(filepath)
        auswertung()
        mariadb_add("nike", itemid, filepath,configpath)
        zurueck()
    else:
        zurueck()

if __name__ == "__main__":
    #print(get_itemid('https://www.nike.com/de/t/go-flyease-schuhe-fur-einfaches-an-und-ausziehen-nfbRvV/DR5540-102'))
    nike('https://www.nike.com/de/t/mercurial-superfly-9-academy-high-top-fussballschuh-fur-verschiedene-boden-HhlDp2/DJ5625-700', './testamazon/json/s/', './testamazon/')
