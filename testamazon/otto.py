import requests
from bs4 import BeautifulSoup
import json
import re
import os
from translate import Translate
from bertaus import auswertung
from test_mariadb import mariadb_add
from mariadb_ueberpruefen import datenbank_test
from tobi import zurueck

def ref_get_itemid(url):
    regex = r'kundenbewertungen\/(\w+)'
    match = re.search(regex, url)
    if match != None and match.group(1) != None:
        return match.group(1)
    else:
        return pro_get_itemid(url)
        

def pro_get_itemid(url):
    regex = r'(\w+)\/#variationId'
    regex2 = r'(\d+)\/#variationId'
    match = re.search(regex, url)
    match2 = re.search(regex2, url)
    if match != None and match.group(1) != None:
        unfinished_itemid = match.group(1)
        if match2 != None and unfinished_itemid[1:] == match2.group(1):
            return unfinished_itemid[1:]
        else:
            return unfinished_itemid
    return None
    

def get_reviews(itemid, page_number, filename):
    if page_number > 10:
        return
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    review_url = f'https://www.otto.de/product-customerreview/product/reviews/{itemid}?page={page_number}&sortingRank=newest'
    response = requests.get(review_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.select('.cr_js_review')
        reviews = []
        for div in divs:
            title = None
            text = None
            stars = None
            titles_h4 = div.select('h4.pl_headline50.pl_my25')
            text_spans = div.select('.cr_review__expander span')
            stars_spans = div.select('span.cr_ratingStars')
            for star_span in stars_spans:
                star_imgs = star_span.select('use')
                stars = 0
                for star_img in star_imgs:
                    if star_img['xlink:href'] == "/assets-static/icons/pl_icon_rating-filled.svg#pl_icon_rating-filled":
                        stars += 1

            for text_span in text_spans:
                text = text_span.get_text(strip=True)
            for title_h4 in titles_h4:
                title = title_h4.get_text(strip=True)
            reviews.append({'title':title, 'stars': stars,'text': text})
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_reviews = json.load(f)
                reviews.extend(existing_reviews)  # Add to existing data
        except FileNotFoundError:  
            pass  # Ignore if the file doesn't exist yet

        # Save all reviews 
        with open(filename, 'w', encoding='utf-8') as f:
             json.dump(reviews, f, ensure_ascii=False, indent=4)
        maxpage_buttons = soup.select('.p_btn50--3rd.cr_paging__button.cr_js_paging__button.cr_paging__button--last.cr_js_paging__button--last')
        maxpage = 1
        for maxpage_button in maxpage_buttons:
            maxpage = int(maxpage_button['data-target'])
        if page_number < maxpage:
            get_reviews(itemid, page_number+1, filename)

        
def delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)

def otto(url, filepath):
    delete_file(filepath)
    itemid = ref_get_itemid(url)
    neu = datenbank_test("otto" ,itemid)
    isneu = not neu[0]
    if isneu:
        get_reviews(itemid, 1, filepath)
        Translate()
        bewertung = auswertung()
        fake = bewertung['Fake']
        mariadb_add("otto", itemid, fake)
        zurueck()
    else:
        zurueck()

if __name__ == "__main__":
    otto('https://www.otto.de/p/jack-jones-t-shirt-kompo-tee-538986060/#variationId=1410962871','./testamazon/json/s/review.json')