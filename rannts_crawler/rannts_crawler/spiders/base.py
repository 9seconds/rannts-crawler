# -*- coding: utf-8 -*-


import scrapy


class Spider(scrapy.Spider):
    allowed_domains = ["rannts.ru"]

    @staticmethod
    def follow_urls(response, css_selector, callback):
        for link in response.css(css_selector):
            url = link.extract()
            if url:
                url = response.urljoin(url)
                yield response.follow(url, callback=callback)
