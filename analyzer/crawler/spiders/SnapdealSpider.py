# -*- coding: utf-8 -*-
import json
import re
from time import sleep

import scrapy
from bs4 import BeautifulSoup


def ParseReviews(snapdeal_url, page):
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
        # 'reviews': reviews_list,
        'url': snapdeal_url,
        'price': product_price,
        'name': product_name
    }
    return data, reviews_list


def ReadAsin(url, page, count):
    # Add your own ASINs here
    extracted_data = []
    print("Downloading and processing page " + url + "/reviews/" + " page : " + str(count))
    parsed_data, reviews_list = ParseReviews(url + "/reviews/", page)
    sleep(2)
    # f = open('snapdeal_data.json' % count, 'w')
    # json.dump(extracted_data, f, indent=4)
    return parsed_data, reviews_list


def get_product_id(url):
    refined_url = url.split('#')[0]
    p = re.compile("\d*$")
    m = re.search(p, refined_url)
    return m.group(0)


def get_product_url(url):
    id = get_product_id(url)
    return url.split(id)[0] + id


class SnapdealSpider(scrapy.Spider):
    name = "snapdeal"

    url = 'https://www.snapdeal.com/product/leeco-le2-x526-64gb-rose/658041763918#bcrumbLabelId:175'
    page = 1
    allowed_domains = ["www.snapdeal.com"]
    start_urls = [get_product_url(url) + '/reviews/']
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
        parsed_data, review_list = ReadAsin(get_product_url(self.url), response.body, self.page)
        self.reviews.extend(review_list)

        self.page += 1
        soup = BeautifulSoup(response.body, 'lxml')
        try:
            next_link = soup.find('li', class_='last').find('a')['href']
            print("############" + next_link + "###########")
        except TypeError:
            print('No more pages found')
            self.stop = True

        if not self.stop and self.page < 5:
            self.start_urls.append(next_link)
            yield scrapy.Request(url=next_link, headers=self.headers, callback=self.parse)
        else:
            parsed_data['reviews'] = self.reviews
            f = open('snapdeal_data.json', 'w')
            json.dump(parsed_data, f, indent=4)
            f.close()
