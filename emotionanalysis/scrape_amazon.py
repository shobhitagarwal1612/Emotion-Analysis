#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/
import json
import re
from time import sleep

import requests
from bs4 import BeautifulSoup
from lxml import html


###review page
def ParseReviews(url, asin):
    # This script has only been tested with Amazon.com
    amazon_url = 'http://' + url + '/product-reviews/' + asin
    # Add some recent user agent to prevent amazon from blocking the request
    # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 '
                      'Safari/537.36'}
    page = requests.get(amazon_url, headers=headers).text

    # parser = html.fromstring(page)
    # XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
    # XPATH_REVIEW_SECTION = '//div[@id="revMHRL"]/div'
    # XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
    # XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
    # XPATH_PRODUCT_PRICE = '//span[@id="priceblock_ourprice"]/text()'

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
            rating_key = extracted_rating[0].a.text
            rating_value = extracted_rating[2].a.text
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
        'ratings': ratings_dict,
        'reviews': reviews_list,
        'url': amazon_url,
        'price': product_price,
        'name': product_name
    }
    return data


def ReadAsin(domain, asin):
    # Add your own ASINs here
    extracted_data = []
    print("Downloading and processing page http://" + domain + "/dp/" + asin)
    extracted_data.append(ParseReviews(domain, asin))
    sleep(5)
    f = open('data.json', 'w')
    json.dump(extracted_data, f, indent=4)


def get_asin(url):
    return url.split("/dp/")[1].split("/")[0]


def get_domain(url):
    return url.split("/")[2]


if __name__ == '__main__':
    url = 'http://www.amazon.in/IZINC-Hooded-Sleeve-Cotton-T-Shirt/dp/B013WP1RDI/ref=pd_rhf_dp_s_cp_3?_encoding=UTF8' \
          '&pd_rd_i=B013WP1RDI&pd_rd_r=1J8D15T1FTNBY5NRA064&pd_rd_w=yTCw1&pd_rd_wg=npkkg&psc=1&refRID' \
          '=1J8D15T1FTNBY5NRA064 '
    domain = get_domain(url)
    asin = get_asin(url)

    ReadAsin(domain, asin)
