# -*- coding: utf-8 -*-
import json
from time import sleep

import scrapy
from bs4 import BeautifulSoup


def get_asin(url):
    return url.split("/dp/")[1].split("/")[0]


def get_domain(url):
    return url.split("/")[2]


# use : scrapy crawl amazon to run the spider crawler

###review page
def ParseReviews(url, asin, page):
    # This script has only been tested with Amazon.com
    amazon_url = 'http://' + url + '/product-reviews/' + asin

    soup = BeautifulSoup(page, 'lxml')
    XPATH_PRODUCT_NAME = soup.select_one('.a-link-normal')
    XPATH_PRODUCT_PRICE = soup.select_one('.arp-price,.a-link-normal')
    XPATH_REVIEW_SECTION = soup.find(
        attrs={'class': 'a-text-left a-fixed-left-grid-col reviewNumericalSummary celwidget '
                        'a-col-left'})
    XPATH_RATINGS_TABLE = XPATH_REVIEW_SECTION.find('table', id='histogramTable')
    XPATH_REVIEW_LIST = soup.find('div', id='cm_cr-review_list')

    product_price = XPATH_PRODUCT_PRICE.text.replace(',', '')
    product_name = XPATH_PRODUCT_NAME.text.strip()
    total_ratings = XPATH_REVIEW_SECTION.select_one('.totalReviewCount').text
    reviews = XPATH_REVIEW_LIST.find_all('div', attrs={'class': 'a-section review'})

    ratings_dict = {}
    reviews_list = []

    # grabing the rating  section in product page
    for ratings in XPATH_RATINGS_TABLE:
        extracted_rating = ratings.find_all('td')
        if extracted_rating:
            # print(extracted_rating)
            try:
                rating_key = extracted_rating[0].a.text
                rating_value = extracted_rating[2].a.text
            except AttributeError:
                rating_key = extracted_rating[0].span.text
                rating_value = 0
            if rating_key:
                ratings_dict.update({rating_key: rating_value})

    # Parsing individual reviews
    for review in reviews:
        review = review.div
        raw_review_author = review.find('a', class_='author').text
        raw_review_rating = review.find('i', class_='review-rating').span.text
        raw_review_header = review.find('a', class_='review-title').text
        raw_review_posted_date = review.find('span', class_='review-date').text.split(' ', 1)[1]
        raw_review_text = review.find('span', class_="a-size-base review-text").text

        # cleaning data
        review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')

        review_dict = {
            'review_text': raw_review_text,
            'review_posted_date': raw_review_posted_date,
            'review_header': raw_review_header,
            'review_rating': review_rating,
            'review_author': raw_review_author

        }
        reviews_list.append(review_dict)

    data = {
        'total_ratings': total_ratings,
        'ratings': ratings_dict,
        # 'reviews': reviews_list,
        'url': amazon_url,
        'price': product_price,
        'name': product_name
    }
    return data, reviews_list


def ReadAsin(domain, asin, page, count):
    # Add your own ASINs here
    print("Downloading and processing page http://" + domain + "/product-reviews/" + asin + " page : " + str(count))
    parsed_data, reviews_list = ParseReviews(domain, asin, page)
    sleep(5)

    # f = open('amazon_data.json', 'w')
    # json.dump(extracted_data, f, indent=4)
    return parsed_data, reviews_list


class Item(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    reviews = scrapy.Field()
    ratings = scrapy.Field()
    total_ratings = scrapy.Field()


class AmazonSpider(scrapy.Spider):
    url = 'http://www.amazon.in/Moto-Plus-4th-Gen-White/dp/B01DDP85BY/ref=sr_1_2?s=electronics&rps=1&ie=UTF8&qid' \
          '=1487658956&sr=1-2 '
    page = 1
    domain = get_domain(url)
    base_url = 'http://' + domain
    name = "amazon"
    allowed_domains = [domain]
    start_urls = [base_url + '/product-reviews/' + get_asin(url)]
    reviews = []
    stop = False

    # Add some recent user agent to prevent amazon from blocking the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 '
                      'Safari/537.36'}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        print('--------------------------')
        parsed_data, review_list = ReadAsin(get_domain(self.url), get_asin(self.url), response.body, self.page)
        self.reviews.extend(review_list)

        self.page += 1
        soup = BeautifulSoup(response.body, 'lxml')
        try:
            next_link = soup.find('li', class_='a-last').find('a')['href']
        except TypeError:
            print('No more pages found')
            self.stop = True

        if not self.stop and self.page < 5:
            next_link = self.base_url + next_link
            self.start_urls.append(next_link)
            yield scrapy.Request(url=next_link, headers=self.headers, callback=self.parse)
        else:
            parsed_data['reviews'] = self.reviews
            f = open('amazon_data.json', 'w')
            json.dump(parsed_data, f, indent=4)
            f.close()
