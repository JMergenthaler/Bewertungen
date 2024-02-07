import scrapy
from scrapy import signals


class TrustpilotSpider(scrapy.Spider):
    name = "trustpilot"

    def __init__(self, *args, **kwargs): 
        super(TrustpilotSpider, self).__init__(*args, **kwargs) 
    
        self.start_urls = [kwargs.get('start_url')]

    #start_urls = ["https://at.trustpilot.com/review/tfbank.at"]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': True,
        'FEEDS': {'trustpilot.json': {'format': 'json', 'overwrite': True}},
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'de-DE,de;q=0.9',
            'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        }
    }

    def parse(self, response):
        all_reviews = response.css(".styles_loadMoreLanguages__wonXg::attr(href)").get()
        last_page = response.css(".pagination_paginationEllipsis__4lfLO+ .pagination-link_item__mkuN3::attr(href)").get()
        next_page = response.css(".pagination-link_next__SDNU4::attr(href)").get()
        first_page = response.css('.pagination-link_rel__VElFy+ .pagination-link_item__mkuN3::attr(href)').get()
        if all_reviews:
            yield response.follow(response.urljoin(all_reviews), self.parse_start)
        elif last_page:
            yield {
                'last_page': last_page
            }
            yield response.follow(response.urljoin(last_page), self.parse)
        elif next_page:
            yield response.follow(response.urljoin(next_page), self.parse)
        else:
            yield response.follow(response.urljoin(first_page), self.parse_start)

    def parse_start(self, response):
        # Extract the review details from the page
        reviews = response.css('.styles_reviewCardInner__EwDq2')

        for review in reviews:
            
            name = review.css('a span.typography_appearance-default__AAY17::text').get()
            rating = review.css('.styles_reviewHeader__iU9Px img::attr(alt)').extract_first()
            title = review.css('.link_notUnderlined__szqki .typography_appearance-default__AAY17::text').extract_first()
            content = review.css('.typography_color-black__5LYEn::text').extract_first()

            yield {
                'name': name,
                'rating': rating,
                'title': title,
                'content': content,
            }

        next_page = response.css('a.pagination-link_next__SDNU4::attr(href)').get()
        if next_page:
            yield response.follow(response.urljoin(next_page), self.parse_start, dont_filter = True)

    