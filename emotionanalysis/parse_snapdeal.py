#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/
import json
import re
from time import sleep

import requests
from bs4 import BeautifulSoup


###review page
def ParseReviews(snapdeal_url, asin, page):
    # This script has only been tested with Amazon.com
    # Add some recent user agent to prevent amazon from blocking the request
    # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 '
                      'Safari/537.36'}
    page = requests.get(snapdeal_url, headers=headers).text

    soup = BeautifulSoup(page, 'lxml')
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


def ReadAsin(url, product_id, page, count):
    # Add your own ASINs here
    extracted_data = []
    print("Downloading and processing page " + url + "/reviews/")
    extracted_data.append(ParseReviews(url + "/reviews/", product_id, page))
    sleep(5)
    f = open('snapdeal_data_%d.json' % count, 'w')
    json.dump(extracted_data, f, indent=4)


def get_product_id(url):
    refined_url = url.split('#')[0]
    p = re.compile("\d*$")
    m = re.search(p, refined_url)
    return m.group(0)


def get_product_url(url):
    id = get_product_id(url)
    return url.split(id)[0] + id


url = 'https://www.snapdeal.com/product/leeco-le2-x526-64gb-rose/658041763918#bcrumbLabelId:175'

ReadAsin(get_product_url(url), get_product_id(url), '', 1)
