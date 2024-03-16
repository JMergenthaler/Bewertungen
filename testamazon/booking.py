import requests
import chardet
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import json
import re
from translate import Translate
from bertaus import auswertung
from test_mariadb import mariadb_add
from mariadb_ueberpruefen import datenbank_test
from tobi import zurueck
import asyncio
import os

async def booking(url, filepath, configpath):
    land,pagename,label,srpvid = get_pagename_label_srpvid(url)
    neu = datenbank_test('booking', pagename, filepath, configpath)
    if not neu:
        delete_file(filepath)
        await play_async_get_reviews(pagename,land,label,srpvid,filepath, 0)
        Translate(filepath)
        auswertung()
        mariadb_add('booking', pagename, filepath, configpath)
        zurueck()
    else:
        zurueck()

def delete_file(file_path):
    if os.path.isfile(file_path + 'review.json'):
        os.remove(file_path + 'review.json')

def get_pagename_label_srpvid(url):
    regex = r'\/\/www\.booking\.com\/\w+\/(\w+)\/([\w-]*)\..*label=([\w-]+).*srpvid=([\w-]+)'
    match = re.search(regex, url)
    if match != None and match.group(1) != None and match.group(2) != None and match.group(3) != None and match.group(4) != None:
        return match.group(1), match.group(2), match.group(3), match.group(4)
    return None

async def play_get_reviews(pagename, url_label, srpvid, filepath, offset):
    review_url = f'https://www.booking.com/reviewlist.de.html?aid=304142&label={url_label}&sid=3c1855f678f51917147b6ec76cbf7faa&srpvid={srpvid}&;cc1=de&pagename={pagename}&r_lang=&review_topic_category_id=&type=total&score=&sort=f_recent_desc&time_of_year=&dist=1&offset={offset}&rows=100&rurl=&text=&translate=&_='
    async with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context()
        page = context.new_page()
        await page.goto(url=review_url, timeout=60000)
        ul_selector = 'ul.review_list li.review_list_new_item_block'
        lis = page.query_selector_all(ul_selector)
        reviews = []
        for li in lis:
            title = None
            text = ""
            rating = None
            h3s = li.query_selector_all('h3')
            for h3 in h3s:
                title = str(h3.get_property('textContent'))
            divs = li.query_selector_all('div.c-review__row')
            get_text = {}
            for div in divs:
                label = None
                rev_text = None
                revs = div.query_selector_all('.c-review__body')
                labels_selector = div.query_selector_all('.bui-u-sr-only')
                for label_selector in labels_selector:
                    label = str(label_selector.get_property('textContent'))
                for rev in revs:
                    if str(rev.get_property('textContent')) != "":
                        rev_text = str(rev.get_property('textContent'))
                get_text.update({label:rev_text})
                
            numbers = li.query_selector_all('.bui-review-score__badge')
            for number in numbers:
                rating  = str(number.get_property('textContent'))
            for key, value in get_text.items():
                if key != None:
                    text += f"{key} {value}"
                    if len(get_text) > 1:
                        text += " "
            reviews.append({'title': title, 'rating': rating, 'text': text})
        browser.close()
        try:
            with open(filepath + 'review.json', 'r', encoding='utf-8') as f:
                existing_reviews = json.load(f)
                reviews.extend(existing_reviews)  # Add to existing data
        except FileNotFoundError:  
            pass  # Ignore if the file doesn't exist yet

        with open(filepath + 'review.json', "w") as f:
            json.dump(reviews, f)
        
        offset += 25
        if offset < 100:
            await play_get_reviews(pagename, url_label, srpvid, filepath,offset)

def test(filename):
    with open(filename + 'review.json', 'r', encoding='utf-8') as f:
        existing_reviews = json.load(f)
        print(len(existing_reviews))

async def test2():
    land,pagename,label,srpvid = get_pagename_label_srpvid('https://www.booking.com/hotel/it/romance-al-colosseo.de.html?aid=304142&label=gen173nr-1FCAEoggI46AdIM1gEaDuIAQGYAQe4ARfIAQzYAQHoAQH4AQuIAgGoAgO4ApHKrK8GwAIB0gIkNTAzNjUxYmQtYzdmYi00YTRmLTkzN2EtMWEyMDMzZGMwMDc32AIG4AIB&sid=3c1855f678f51917147b6ec76cbf7faa&dest_id=1232235;dest_type=hotel;dist=0;group_adults=2;group_children=0;hapos=1;hpos=1;nflt=ht_id%3D201%3Bht_id%3D213%3Bht_id%3D219%3Bht_id%3D220%3Bht_id%3D228%3Bht_id%3D229%3Bht_id%3D230%3Bht_id%3D232%3Bht_id%3D208%3Bht_id%3D209%3Bht_id%3D210%3Bht_id%3D212%3Bht_id%3D214%3Bht_id%3D215%3Bht_id%3D216%3Bht_id%3D222%3Bht_id%3D223%3Bht_id%3D224%3Bht_id%3D227;no_rooms=1;req_adults=2;req_children=0;room1=A%2CA;sb_price_type=total;sr_order=popularity;srepoch=1709980835;srpvid=2c454b0c740d0195;type=total;ucfs=1&#hotelTmpl')
    await play_async_get_reviews(pagename,land,label,srpvid,'./testamazon/json/s/review.json', 100)

import json
import asyncio

async def play_async_get_reviews(pagename, land,url_label, srpvid, filepath, offset):
    review_url = f'https://www.booking.com/reviewlist.de.html?aid=304142&label={url_label}&sid=3c1855f678f51917147b6ec76cbf7faa&cc1={land}&dist=1&pagename={pagename}&sort=f_recent_desc&srpvid={srpvid}&type=total&offset={offset}&rows=25'
    #review_url = f'https://www.booking.com/reviewlist.de.html?aid=304142&label={url_label}&sid=3c1855f678f51917147b6ec76cbf7faa&srpvid={srpvid}&;cc1={land}&pagename={pagename}&r_lang=&review_topic_category_id=&type=total&score=&sort=f_recent_desc&time_of_year=&dist=1&offset={offset}&rows=100&rurl=&text=&translate=&_='
    print(review_url)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url=review_url, timeout=60000) 

        ul_selector = 'ul.review_list li.review_list_new_item_block'
        lis = await page.query_selector_all(ul_selector)

        reviews = []
        for li in lis:
            title = None
            text = ""
            rating = None

            h3s = await li.query_selector_all('h3')
            for h3 in h3s:
                if (await h3.get_property('textContent')) != "":
                    title = await h3.text_content()

            divs = await li.query_selector_all('div.c-review__row')
            get_text = {}
            for div in divs:
                label = None
                rev_text = None

                revs = await div.query_selector_all('.c-review__body')
                labels_selector = await div.query_selector_all('.bui-u-sr-only')

                for label_selector in labels_selector:
                    label = await label_selector.get_property('textContent')
                for rev in revs:
                    if (await rev.get_property('textContent')) != "" and (await rev.get_property('textContent')) != " ":
                        rev_text = await rev.text_content()  # Extract text content
                get_text.update({label: rev_text})

            numbers = await li.query_selector_all('.bui-review-score__badge')
            for number in numbers:
                if (await number.get_property('textContent')) != "":
                    rating = await number.text_content()

            for key, value in get_text.items():
                if key:  # Equivalent to key != None
                    text += f"{key} {value}"
                    if len(get_text) > 1:
                        text += " "
            reviews.append({'title': title, 'rating': rating, 'text': text})

        await browser.close()

    try:
        with open(filepath + 'review.json', 'r', encoding='utf-8') as f:
            existing_reviews = json.load(f)
            reviews.extend(existing_reviews)  # Add to existing data
    except FileNotFoundError:  
        pass  # Ignore if the file doesn't exist yet

    with open(filepath + 'review.json', "w") as f:
        json.dump(reviews, f)
    
    offset += 25
    if offset < 100:
        await play_async_get_reviews(pagename, land, url_label, srpvid, filepath,offset)


if __name__ == "__main__":
    asyncio.run(booking('https://www.booking.com/hotel/it/romance-al-colosseo.de.html?aid=304142&label=gen173nr-1FCAEoggI46AdIM1gEaDuIAQGYAQe4ARfIAQzYAQHoAQH4AQuIAgGoAgO4ApHKrK8GwAIB0gIkNTAzNjUxYmQtYzdmYi00YTRmLTkzN2EtMWEyMDMzZGMwMDc32AIG4AIB&sid=3c1855f678f51917147b6ec76cbf7faa&dest_id=1232235;dest_type=hotel;dist=0;group_adults=2;group_children=0;hapos=1;hpos=1;nflt=ht_id%3D201%3Bht_id%3D213%3Bht_id%3D219%3Bht_id%3D220%3Bht_id%3D228%3Bht_id%3D229%3Bht_id%3D230%3Bht_id%3D232%3Bht_id%3D208%3Bht_id%3D209%3Bht_id%3D210%3Bht_id%3D212%3Bht_id%3D214%3Bht_id%3D215%3Bht_id%3D216%3Bht_id%3D222%3Bht_id%3D223%3Bht_id%3D224%3Bht_id%3D227;no_rooms=1;req_adults=2;req_children=0;room1=A%2CA;sb_price_type=total;sr_order=popularity;srepoch=1709980835;srpvid=2c454b0c740d0195;type=total;ucfs=1&#hotelTmpl','./testamazon/json/s/', './testamazon/'))
    #test('./testamazon/json/s/end.json')
    #asyncio.run(test2())