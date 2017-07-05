# -*- coding: utf-8 -*-


import dateparser
import scrapy.loader

from rannts_crawler import items
from . import base


class MeetupsSpider(base.Spider):
    name = "meetups"
    start_urls = [
        "https://rannts.ru/meetups"
    ]

    def parse(self, response):
        for result in self.follow_urls(
                response, "section.section div.content h1 a::attr(href)",
                self.parse_meetups):
            yield result

        for result in self.follow_urls(
                response, "nav.pagination a::attr(href)", self.parse):
            yield result

    def parse_meetups(self, response):
        loader = scrapy.loader.ItemLoader(
            item=items.MeetupsItem(), response=response)

        loader.add_css("number", ".hero-body h1.title")
        loader.add_css("date", ".hero-body h2.subtitle")
        loader.add_css("place", ".hero-body h2.subtitle a::text")
        loader.add_css("place_link", ".hero-body h2.subtitle a::attr(href)")
        loader.add_xpath("description", "//section[2]/div/div")
        loader.add_value("talks", list(self.parse_talks(loader, response)))
        loader.add_value("description_links", [
            response.urljoin(link)
            for link in response.xpath("//section[2]/div/div") \
                .css("a::attr(href)").extract()
        ])


        yield loader.load_item()

    def parse_talks(self, base_loader, response):
        base_datetime = base_loader.load_item()["date"]

        for selector in response.xpath("//section[4]"):
            loader = scrapy.loader.ItemLoader(
                item=items.TalksItem(), selector=selector)

            loader.add_css("title", "h4")
            loader.add_css("speaker", "h5")
            loader.add_css("company", "h5")
            loader.add_value(
                "date",
                self.make_date(
                    base_datetime,
                    selector.css("div.is-2::text").extract_first()
                )
            )
            loader.add_xpath(
                "description",
                "//div/div/div[1]/div[2]/p[not(position() = 1 and @class='is-small')]"
            )

            slides_link = selector.xpath(
                "//div/div/div[1]/div[2]/p[1 and @class='is-small']/a/@href")
            loader.add_value(
                "slides_link",
                response.urljoin(slides_link.extract_first()))
            loader.add_value(
                "description_links",
                [
                    response.urljoin(url)
                    for url in selector.xpath(
                            "//div/div/div[1]/div[2]/p[not(position() = 1 and @class='is-small')]/a/@href").extract()
                ]
            )
            loader.add_css("video_link", "iframe::attr(src)")

            yield loader.load_item()

    def make_date(self, base, time):
        parsed_time = dateparser.parse(time)

        return base.replace(
            hour=parsed_time.hour,
            minute=parsed_time.minute,
            second=parsed_time.second,
            microsecond=parsed_time.microsecond
        )
