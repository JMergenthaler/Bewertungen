
import scrapy
from urllib.parse import urljoin



class AmazonReviewsSpider(scrapy.Spider):

    asin = ""

    def __init__(self, *args, **kwargs): 
        super(AmazonReviewsSpider, self).__init__(*args, **kwargs) 

        self.asin = [kwargs.get('asin')] 

    name = "amazon_reviews"
    custom_settings = {
        'FEEDS': {'amazon.json': {'format': 'json', 'overwrite': True}},
        'DEFAULT_REQUEST_HEADERS': {
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de',
            'Sec-Ch-Ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        },
    }

    def start_requests(self):
        asin_list = self.asin
        page_number = 1
        for asin in asin_list:
            amazon_reviews_url = f'https://www.amazon.com/product-reviews/{asin}/sortBy=recent/sortBy=recent/ref=cm_cr_getr_d_paging_btm_prev_1?sortBy=recent'
            yield scrapy.Request(url=amazon_reviews_url, callback=self.parse_reviews, meta={'asin': asin, 'retry_count': 0, 'page_number' : page_number})


    def parse_reviews(self, response):
        asin = response.meta['asin']
        retry_count = response.meta['retry_count']
        page_number = response.meta['page_number']

        ## Get Next Page Url
        next_page_relative_url = response.css("#cm_cr-pagination_bar a::attr(href)").get()
        if next_page_relative_url is not None:
            retry_count = 0
            page_number += 1
            next_page = f"https://www.amazon.com/product-reviews/{asin}/sortBy=recent/sortBy=recent/ref=cm_cr_arp_d_paging_btm_next_{page_number}?sortBy=recent&pageNumber={page_number}"
            yield {"Link": next_page}
            yield scrapy.Request(url=next_page, callback=self.parse_reviews, meta={'asin': asin, 'retry_count': retry_count, 'page_number' : page_number})
        elif retry_count < 3:
            retry_count = retry_count+1
            yield scrapy.Request(url=response.url, callback=self.parse_reviews, dont_filter=True, meta={'asin': asin, 'retry_count': retry_count, 'page_number' : page_number})

        ## Parse Product Reviews
        review_elements = response.css("#cm_cr-review_list div.review")
        for review_element in review_elements:
            yield {
                    "asin": asin,
                    "text": "".join(review_element.css("span[data-hook=review-body] ::text").getall()).strip(),
                    "title": review_element.css("*[data-hook=review-title]>span::text").get(),
                    "location_and_date": review_element.css("span[data-hook=review-date] ::text").get(),
                    "verified": bool(review_element.css("span[data-hook=avp-badge] ::text").get()),
                    "rating": review_element.css("*[data-hook*=review-star-rating] ::text").re(r"(\d+\.*\d*) out")[0],
                    }

