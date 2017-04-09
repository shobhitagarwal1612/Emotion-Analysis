#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/
import json
import os
import sys
from time import sleep

import requests
from bs4 import BeautifulSoup


def get_asin(url):
    return url.split("/dp/")[1].split("/")[0]


def get_domain(url):
    return url.split("/")[2]


# use : scrapy crawl amazon to run the spider crawler

###review page
def ParseReviews(page):
    # This script has only been tested with Amazon.com

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
        'price': product_price,
        'name': product_name
    }
    return data, reviews_list


page_count = 1
url = sys.argv[1]
domain = get_domain(url)
asin = get_asin(url)
base_url = 'http://' + domain
start_urls = [base_url + '/product-reviews/' + asin]
reviews = []
stop = False

# Add some recent user agent to prevent amazon from blocking the request
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 '
                  'Safari/537.36'}


def start_requests(url):
    global stop, next_link, page_count
    sleep(3)
    response = requests.get(url, headers=headers).text
    print('--------------------------')

    parsed_data, review_list = ParseReviews(response)
    reviews.extend(review_list)

    page_count += 1
    soup = BeautifulSoup(response, 'lxml')
    try:
        next_link = soup.find('li', class_='a-last').find('a')['href']
    except TypeError:
        print('No more pages found')
        stop = True

    if not stop and page_count < 4:
        next_link = base_url + next_link
        start_urls.append(next_link)
    else:
        parsed_data['reviews'] = reviews
        f = open(os.getcwd() + '/amazon_data.json', 'w')
        json.dump(parsed_data, f, indent=4)
        f.close()


def save_product_details():
    response = requests.get(url=url, headers=headers).text
    soup = BeautifulSoup(response, 'lxml')
    product_image = soup.select_one('#landingImage')['src']
    img = str.replace(product_image, "\r", "")
    img = str.replace(img, "\n", "")
    img = '"' + img + '"'
    path = os.getcwd()
    output = open(path + "/imageData.txt", "w")
    output.write(img)
    output.close()

    product_details = soup.select('.col1 td')
    output = open(os.getcwd() + "/specs.txt", "w")
    for row in product_details:
        if row != '':
            output.write(row.text + "\n")
    output.close()

    print("details saved")


save_product_details()

for url in start_urls:
    start_requests(url)

print('Parsing complete')
