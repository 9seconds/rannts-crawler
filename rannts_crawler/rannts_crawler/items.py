# -*- coding: utf-8 -*-


import calendar
import re
import urlparse

import dateparser
import lxml.html
import scrapy
import scrapy.loader.processors as processors


def strip(text):
    return text.strip()


def clean_text(text):
    text = text.replace("</p>", "\n\n")
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = lxml.html.document_fromstring(text).text_content()

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


def parse_number(text):
    return int(text.replace("#", ""))


def serialize_date(dtime):
    return int(calendar.timegm(dtime.timetuple()))


def split_location(location):
    return location.split("@", 1)[0]


def extract_name(text):
    return "(".join(text.split("(")[:-1])


def extract_company(text):
    matcher = re.search(r"\(([^\)]*)\)$", text)
    if matcher:
        return matcher.group(1)


def extract_youtube_url(url):
    path = urlparse.urlparse(url).path
    code = path.rsplit("/", 1)
    if len(code) > 1:
        return "https://www.youtube.com/watch?v={0}".format(code[-1])


class NewsItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, strip),
        output_processor=processors.TakeFirst()
    )
    date = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, parse_date),
        output_processor=processors.TakeFirst(),
        serializer=serialize_date
    )
    text = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, strip),
        output_processor=processors.TakeFirst()
    )
    text_links = scrapy.Field()


class MeetupsItem(scrapy.Item):
    number = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, parse_number),
        output_processor=processors.TakeFirst()
    )
    date = scrapy.Field(
        input_processor=processors.MapCompose(
            clean_text, split_location, parse_date),
        output_processor=processors.TakeFirst(),
        serializer=serialize_date
    )
    place = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, strip),
        output_processor=processors.TakeFirst()
    )
    place_link = scrapy.Field(output_processor=processors.TakeFirst())
    description = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, strip),
        output_processor=processors.TakeFirst()
    )
    description_links = scrapy.Field()
    talks = scrapy.Field()


class TalksItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, strip),
        output_processor=processors.TakeFirst()
    )
    speaker = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, extract_name, strip),
        output_processor=processors.TakeFirst()
    )
    company = scrapy.Field(
        input_processor=processors.MapCompose(
            clean_text, extract_company, strip),
        output_processor=processors.TakeFirst()
    )
    date = scrapy.Field(
        output_processor=processors.TakeFirst(),
        serializer=serialize_date
    )
    slides_link = scrapy.Field(output_processor=processors.TakeFirst())
    description = scrapy.Field(
        input_processor=processors.MapCompose(clean_text, strip),
        output_processor=processors.TakeFirst()
    )
    description_links = scrapy.Field()
    video_link = scrapy.Field(
        input_processor=processors.MapCompose(extract_youtube_url),
        output_processor=processors.TakeFirst()
    )
