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

def lidl(url):
    itemid = get_itemid(url)
    neu = datenbank_test("lidl", itemid)
    isneu = not neu[0]
    if isneu:
        lidlanfrage(itemid)
        Translate_Ebay()
        bewertung = auswertung()
        fake = bewertung['Fake']
        mariadb_add("lidl", itemid, fake)
        zurueck()
    else:
        zurueck()
        



        
def lidlanfrage(itemid):
    Path = './testamazon/json/s/'
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
                outputs.append({"stars": stars, "review": reviewtext})
            with open(Path + "review.json", "w") as f:
                json.dump(outputs, f)
        except:
            print("Keine Json file")

if __name__ == "__main__":
    lidl("https://www.lidl.de/p/livarno-home-polsterauflage-hochlehner-ca-120-x-50-x-8-cm/p100342500")