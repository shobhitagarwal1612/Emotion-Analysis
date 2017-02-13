# -*- coding: utf-8 -*-
import os
import sys

import scrapy
from bs4 import BeautifulSoup

sys.path.append(
    os.path.abspath("/home/shobhit/Desktop/PythonProjects/Emotion-Analysis/emotionanalysis/"))

from parse_amazon import *


class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["www.amazon.in"]
    start_urls = ['http://http://www.amazon.in/product-reviews/B00JDACK3S//']

    def start_requests(self):
        url = 'http://www.amazon.in/Fostelo-Womens-Style-Shoulder-FSB-396/dp/B00Z0NMFKU/ref=sr_1_4?s=shoes&rps=1&ie=UTF8' \
              '&qid=1486955427&sr=1-4 '
        ReadAsin(get_domain(url), get_asin(url))
        urls = [
            'http://www.amazon.in/product-reviews/B00JDACK3S/ref=cm_cr_arp_d_paging_btm_1?pageNumber=1',
            # 'http://www.amazon.in/product-reviews/B00JDACK3S/ref=cm_cr_arp_d_paging_btm_2?pageNumber=2',
            # 'http://www.amazon.in/product-reviews/B00JDACK3S/ref=cm_cr_getr_d_paging_btm_3?pageNumber=3'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        next_link = soup.select_one('li.a-last').find('a')['href']
        url = 'http://www.amazon.in/Fostelo-Womens-Style-Shoulder-FSB-396/dp/B00Z0NMFKU/ref=sr_1_4?s=shoes&rps=1&ie=UTF8' \
              '&qid=1486955427&sr=1-4 '

        # page = response.url.split("/")[-2]
        # filename = 'amazon-review-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
