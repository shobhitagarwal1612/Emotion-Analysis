#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/
import json
import re
from time import sleep

import requests
from lxml import html


def ParseReviews(url, asin):
    # This script has only been tested with Amazon.com
    amazon_url = 'http://' + url + '/dp/' + asin
    # Add some recent user agent to prevent amazon from blocking the request
    # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 '
                      'Safari/537.36'}
    page = requests.get(amazon_url, headers=headers).text

    parser = html.fromstring(page)
    XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
    XPATH_REVIEW_SECTION = '//div[@id="revMHRL"]/div'
    XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
    XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
    XPATH_PRODUCT_PRICE = '//span[@id="priceblock_ourprice"]/text()'

    raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
    product_price = ''.join(raw_product_price).replace(',', '')

    raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
    product_name = ''.join(raw_product_name).strip()
    total_ratings = parser.xpath(XPATH_AGGREGATE_RATING)
    reviews = parser.xpath(XPATH_REVIEW_SECTION)

    ratings_dict = {}
    reviews_list = []

    # grabing the rating  section in product page
    for ratings in total_ratings:
        extracted_rating = ratings.xpath('./td//a//text()')
        if extracted_rating:
            rating_key = extracted_rating[0]
            raw_raing_value = extracted_rating[1]
            rating_value = raw_raing_value
            if rating_key:
                ratings_dict.update({rating_key: rating_value})

    # Parsing individual reviews
    for review in reviews:
        XPATH_RATING = './div//div//i//text()'
        XPATH_REVIEW_HEADER = './div//div//span[contains(@class,"text-bold")]//text()'
        XPATH_REVIEW_POSTED_DATE = './/a[contains(@href,"/profile/")]/parent::span/following-sibling::span/text()'
        XPATH_REVIEW_TEXT_1 = './/div//span[@class="MHRHead"]//text()'
        XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing' \
                              '-showfullreview '
        XPATH_REVIEW_COMMENTS = './/a[contains(@class,"commentStripe")]/text()'
        XPATH_AUTHOR = './/a[contains(@href,"/profile/")]/parent::span//text()'
        XPATH_REVIEW_TEXT_3 = './/div[contains(@id,"dpReviews")]/div/text()'
        raw_review_author = review.xpath(XPATH_AUTHOR)
        raw_review_rating = review.xpath(XPATH_RATING)
        raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
        raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
        raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
        raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
        raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)

        author = ' '.join(' '.join(raw_review_author).split()).strip('By')

        # cleaning data
        review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
        review_header = ' '.join(' '.join(raw_review_header).split())
        review_posted_date = ' '.join(raw_review_posted_date)
        review_text = ' '.join(' '.join(raw_review_text1).split())

        # grabbing hidden comments if present
        if raw_review_text2:
            json_loaded_review_data = json.loads(raw_review_text2[0])
            json_loaded_review_data_text = json_loaded_review_data['rest']
            cleaned_json_loaded_review_data_text = re.sub('<.*?>', '', json_loaded_review_data_text)
            full_review_text = review_text + cleaned_json_loaded_review_data_text
        else:
            full_review_text = review_text
        if not raw_review_text1:
            full_review_text = ' '.join(' '.join(raw_review_text3).split())

        raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
        review_comments = ''.join(raw_review_comments)
        review_comments = re.sub('[A-Za-z]', '', review_comments).strip()
        review_dict = {
            'review_comment_count': review_comments,
            'review_text': full_review_text,
            'review_posted_date': review_posted_date,
            'review_header': review_header,
            'review_rating': review_rating,
            'review_author': author

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
    url = "http://www.amazon.in/Tapfond-Oneplus-Protection-Degree-Quicksand/dp/B01HBAI9SG/ref=sr_1_1?ie=UTF8&qid" \
          "=1486933819&sr=8-1&keywords=one+plus+3t+cover "
    domain = get_domain(url)
    asin = get_asin(url)

    ReadAsin(domain, asin)
