# -*- coding: utf-8 -*-


import calendar
import re

import dateparser
import lxml.html
import scrapy
import scrapy.loader.processors as processors


def clean_text(text):
    text = text.replace("</p>", "\n\n")
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = lxml.html.document_fromstring(text).text_content()
    text = text.strip()

    return text


def parse_date(text):
    return dateparser.parse(
        text,
        languages=["ru"],
        settings={
            "TIMEZONE": "Europe/Moscow",
            'RETURN_AS_TIMEZONE_AWARE': True
        }
    )


def serialize_date(dtime):
    return int(calendar.timegm(dtime.timetuple()))


class NewsItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=processors.MapCompose(clean_text),
        output_processor=processors.TakeFirst()
    )
    date = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, parse_date),
        output_processor=processors.TakeFirst(),
        serializer=serialize_date
    )
    text = scrapy.Field(
        input_processor=processors.MapCompose(clean_text),
        output_processor=processors.TakeFirst()
    )
    text_links = scrapy.Field()
