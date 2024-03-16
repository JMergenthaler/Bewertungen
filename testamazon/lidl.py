import requests
import json
import re
from translation_ebay import Translate_Ebay
from bertaus import auswertung
from test_mariadb import mariadb_add
from mariadb_ueberpruefen import datenbank_test
from tobi import zurueck

def get_itemid(url):
    regex = r'\/p(\d+)'
    match = re.search(regex, url)
    if match != None:
        if match.group(1) != None:
            return match.group(1)
    return None

def lidl(url, filepath, conifgpath):
    itemid = get_itemid(url)
    neu = datenbank_test("lidl", itemid, filepath, conifgpath)
    if not neu:
        lidlanfrage(itemid, filepath)
        Translate_Ebay(filepath)
        auswertung()
        mariadb_add("lidl", itemid, filepath, conifgpath)
        zurueck()
    else:
        zurueck()
        



        
def lidlanfrage(itemid, filepath):
    response = requests.get(f"https://www.lidl.de/u/api/product/{itemid}/DE/de?start=1&max=100&order=STARS_DESC")
    if response.status_code == 200:

        input_dict = response.json() 
        #rating = []
        outputs = []
        try:
            #print(input_dict['ratings']['pageItems'])
            for line in input_dict['ratings']['pageItems']:
                reviewtext = line['reviewText']
                stars = line['stars']
                outputs.append({"rating": stars, "text": reviewtext})
            with open(filepath + "review.json", "w") as f:
                json.dump(outputs, f)
        except:
            print("Keine Json file")

if __name__ == "__main__":
    lidl("https://www.lidl.de/p/livarno-home-polsterauflage-hochlehner-ca-120-x-50-x-8-cm/p100342500", './testamazon/json/s/', './testamazon/')