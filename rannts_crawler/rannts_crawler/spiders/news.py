# -*- coding: utf-8 -*-


import scrapy.loader

from rannts_crawler import items
from . import base


class NewsSpider(base.Spider):
    name = "news"
    start_urls = [
        "https://rannts.ru/news"
    ]

    def parse(self, response):
        for result in self.follow_urls(
                response, "section.section .content h1 a::attr(href)",
                self.parse_news):
            yield result

        for result in self.follow_urls(
                response, "nav.pagination a::attr(href)", self.parse):
            yield result

    def parse_news(self, response):
        loader = scrapy.loader.ItemLoader(
            item=items.NewsItem(), response=response)

        loader.add_css("title", ".hero-body h1.title")
        loader.add_css("date", ".hero-body h2.subtitle")
        loader.add_css("text", "section.section div.content")
        loader.add_value("text_links", [
            response.urljoin(link)
            for link in response.css(
                    "section.section div.content a::attr(href)").extract()
        ])

        yield loader.load_item()
