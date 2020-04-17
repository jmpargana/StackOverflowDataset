# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from dataset_creator.items import QuestionItem


class SodsSpider(CrawlSpider):
    name = "sods"
    start_urls = ["http://stackoverflow.com/questions?pagesize=50&sort=newest"]

    def parse(self, response):
        for question in response.css("div.question-summary"):
            item = QuestionItem()

            item["votes"] = int(question.css("div.votes strong::text").get())
            item["answers"] = int(question.css("div.status strong::text").get())
            item["views"] = int(
                re.findall(r"\d+", question.css("div.views::text").get())[0]
            )
            item["question"] = question.css("div.summary>h3>a::text").get()

            yield item

        next_page = response.css("div.s-pagination>a.s-pagination--item::attr(href)").getall()[-1]
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
