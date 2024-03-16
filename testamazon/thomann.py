import requests
from bs4 import BeautifulSoup
import re
import os
import json
from translate import Translate
from bertaus import auswertung
from test_mariadb import mariadb_add
from mariadb_ueberpruefen import datenbank_test
from tobi import zurueck


def get_itemid(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div = soup.select("div.fx-content-product__sidebar.call-to-action.order--1000.order--lg-1000 input")
        for single_div in div:
            return single_div['value']
        
        divs = soup.select("div.keyfeature.keyfeature--grey-background")
        for div in divs:
            itemid_span = div.select("span.fx-text.fx-text--bold.fx-text--no-margin")
            print(itemid_span.get_text(strip=True))
    return None
        




def bewertung_page(itemid, page_number, filepath):
    if page_number > 10:
        return
    page_url = f"https://www.thomann.de/de/prod_ajaxGetMoreUserReviews.html?order=latest&page={page_number}&rating=0&reviewlang%5B%5D=all&ar={itemid}"
    response = requests.get(page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.select("div.fx-grid__col.fx-col--12.fx-col--lg-9.customer-review__sub-head")
        reviews = []
        for item in divs:
            review_divs = item.select('div.fx-text-collapsible.js-fx-text-collapsible.fx-text-collapsible--v2 div.fx-text-collapsible__fallback')
            review = None
            title = None
            stars = None
            review_titles = item.select('span.review-intro__headline.js-headline-original')
            stars_divs = item.select('div.fx-rating-stars__filler')
            for stars_div in stars_divs:
                stars_indicator = stars_div['style']
                regex = r'\d+'
                match = re.search(regex, str(stars_indicator))
                if match != None:
                    stars = int(match.group())/20
            for review_title in review_titles:
                title = review_title.get_text(strip=True)
            for review_div in review_divs:
                review = review_div.get_text(strip=True)
            reviews.append({'title': title, 'rating': stars, "text": review})

        try:
            with open(filepath + 'review.json', 'r', encoding='utf-8') as f:
                existing_reviews = json.load(f)
                reviews.extend(existing_reviews)  # Add to existing data
        except FileNotFoundError:  
            pass  # Ignore if the file doesn't exist yet

        # Save all reviews 
        with open(filepath + 'review.json', 'w', encoding='utf-8') as f:
             json.dump(reviews, f, ensure_ascii=False, indent=4)

        if len(divs) > 0:
            bewertung_page(itemid, page_number+1, filepath)

def delete_file(file_path):
    if os.path.isfile(file_path + 'review.json'):
        os.remove(file_path + 'review.json')

def thomann(url, filepath, configpath):
    delete_file(filepath)
    itemid = get_itemid(url)
    neu = datenbank_test("thomann" ,itemid, filepath, configpath)
    if not neu:
        bewertung_page(itemid, 1, filepath)
        Translate(filepath)
        auswertung()
        mariadb_add("thomann", itemid, filepath, configpath)
        zurueck()
    else:
        zurueck()

if __name__ == "__main__":
    #delete_file('./testamazon/json/s/review.json')
    thomann('https://www.thomann.de/de/denon_dj_sc_live_4.htm', './testamazon/json/s/', './testamazon/')
    #bewertung_page(467180, 1 ,'./testamazon/json/s/review.json')