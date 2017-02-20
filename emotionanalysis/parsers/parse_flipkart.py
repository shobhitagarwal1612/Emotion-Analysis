#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/
import json
import re
from time import sleep

import requests
from bs4 import BeautifulSoup


###review page
def ParseReviews(snapdeal_url, page):
    # This script has only been tested with Amazon.com
    # Add some recent user agent to prevent amazon from blocking the request
    # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 '
                      'Safari/537.36'}
    page = requests.get(snapdeal_url, headers=headers).text

    soup = BeautifulSoup(page, 'lxml')

    product_details_tag = soup.select_one('.NWW_bH')
    print(product_details_tag)

    XPATH_PRODUCT_NAME = soup.find('p', class_='product-title').text
    XPATH_PRODUCT_PRICE = soup.find('p', class_='product-offer-price').text
    XPATH_PRODUCT_RATING = soup.find('span', class_='rating').text
    XPATH_TOTAL_COUNT = soup.find('p', class_='total-review-txt').text
    XPATH_REVIEW_SECTION = soup.find('div', class_='reviewareain clearfix')

    reviews = XPATH_REVIEW_SECTION.div.find_all('div', class_='commentlist')

    product_price = XPATH_PRODUCT_PRICE.strip()
    product_name = XPATH_PRODUCT_NAME.strip()
    total_ratings = XPATH_TOTAL_COUNT
    product_rating = XPATH_PRODUCT_RATING + " out of 5 stars"

    reviews_list = []

    # print(reviews)

    # Parsing individual reviews
    for review in reviews:
        raw_review_author = review.find('div', class_='_reviewUserName').text
        raw_review_rating = str(len(review.find_all('i', class_='active')))
        raw_review_header = review.find('div', class_='head').text
        raw_review_posted_date = review.find('div', class_='_reviewUserName', title=raw_review_author).text.split('on')[
            1]
        raw_review_text = review.find('p').text

        # cleaning data
        review_rating = str(float(raw_review_rating)) + ' out of 5 stars'

        review_dict = {
            'review_text': raw_review_text,
            'review_posted_date': raw_review_posted_date,
            'review_header': raw_review_header,
            'review_rating': review_rating,
            'review_author': raw_review_author

        }
        reviews_list.append(review_dict)

    data = {
        'rating': product_rating,
        'total_ratings': total_ratings,
        'reviews': reviews_list,
        'url': snapdeal_url,
        'price': product_price,
        'name': product_name
    }
    return data


def ReadAsin(url, page, count):
    # Add your own ASINs here
    extracted_data = []
    print("\n--------------------------------------------------------")
    print("Downloading and processing page : " + url)
    print("--------------------------------------------------------\n")
    extracted_data.append(ParseReviews(url, page))
    sleep(5)
    f = open('flipkart_data.json', 'w')
    json.dump(extracted_data, f, indent=4)


def get_product_url(url):
    url_ = url.split('/p/')
    url__ = url_[1].split('?')
    p = re.compile("pid=[a-zA-Z0-9]+")
    m = re.search(p, url__[1])
    flipkart_url = url_[0] + '/product-reviews/' + url__[0] + "?" + m.group(0)
    return flipkart_url


url = 'https://www.flipkart.com/texclusive-embroidered-fashion-georgette-sari/p/itmejtfsfgfpbxxf?pid=SAREJTFS4ZUZNFFP' \
      '&srno=b_1_1&otracker=hp_omu_Big%20Brands%20at%20Best%20Discounts_4_Min%2060%25%20Off_45063207-e8c2-4ba3-901a' \
      '-05deff7ff4c1_6&lid=LSTSAREJTFS4ZUZNFFPUYKIV9 '

ReadAsin(get_product_url(url), '', 1)
