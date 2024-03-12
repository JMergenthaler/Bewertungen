import requests
import json
from bs4 import BeautifulSoup
import re
import os
from translate import Translate
from bertaus import auswertung
from test_mariadb import mariadb_add
from mariadb_ueberpruefen import datenbank_test
from tobi import zurueck

def get_itemid(url):
    headers_dict = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "de-DE,de;q=0.6",
        "Content-Type": "application/json",
        "Glassversion": "f69593a",
        "Sec-Ch-Ua": "\"Not A(Brand\";v=\"99\", \"Brave\";v=\"121\", \"Chromium\";v=\"121\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Gpc": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers_dict)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tags = soup.find_all('script')
        for script_tag in script_tags:
            match = re.search(r'"model_number":"(\w+)', script_tag.text)
            if match:
                return match.group(1)

def get_reviews(itemid,limit,offset, filename, url):
    headers_dict = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "de-DE,de;q=0.6",
    "Content-Type": "application/json",
    "Glassversion": "f69593a",
    "Referer": url,
    "Sec-Ch-Ua": "\"Not A(Brand\";v=\"99\", \"Brave\";v=\"121\", \"Chromium\";v=\"121\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Gpc": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    review_url = f'https://www.adidas.de/api/models/{itemid}/reviews?bazaarVoiceLocale=de_DE&feature%2A&limit={limit}&offset={offset}&sort=newest'
    response = requests.get(review_url, headers=headers_dict)
    if response.status_code == 200:
        data = response.json()
        reviews = []
        for review_data in data['reviews']:
            title = review_data['title']
            text = review_data['text']
            rating = review_data['rating']
            autor = review_data['userNickname']
            reviews.append({'title':title, 'text': text, 'rating': rating, 'autor': autor})
        if len(data['reviews']) == 0:
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_reviews = json.load(f)
                reviews.extend(existing_reviews)  # Add to existing data
        except FileNotFoundError:  
            pass  # Ignore if the file doesn't exist yet

        # Save all reviews 
        with open(filename, 'w', encoding='utf-8') as f:
             json.dump(reviews, f, ensure_ascii=False, indent=4)
        offset += 10
        if offset < 100:
            get_reviews(itemid,limit, offset, filename, url)

def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)

def adidas(url, filename):
    itemid = get_itemid(url)
    neu = datenbank_test("adidas", itemid)
    isneu = not neu[0]
    if isneu:
        delete_file(filename)
        get_reviews(itemid, 10,0, filename, url)
        Translate()
        bewertung = auswertung()
        fake = bewertung['Fake']
        mariadb_add('adidas', itemid, fake)
        zurueck()
    else:
        zurueck()

if __name__ == "__main__":
    adidas('https://www.adidas.de/stan-smith-lux-shoes/IF8846.html?pr=home_still_interested_rr&slot=3&rec=mt' ,'./testamazon/json/s/review.json')