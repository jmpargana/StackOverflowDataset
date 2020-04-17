# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from dataset_creator.items import QuestionItem

import re


class SodsSpider(CrawlSpider):
    name = 'sods'

    # allowed_domains = ['stackoverflow.com']

    start_urls = ['http://stackoverflow.com/questions?pagesize=50&sort=newest']

    # rules = (
    #     Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    # )

    def parse(self, response):
        for question in response.css('div.question-summary'):
            item = QuestionItem()

            item['votes'] = int(question.css('div.votes strong::text').get())
            item['answers'] = int(question.css('div.status strong::text').get())
            item['views'] = int(re.findall(r'\d+', question.css('div.views::text').get())[0])
            item['question'] = question.css('div.summary>h3>a::text').get()

            yield item

