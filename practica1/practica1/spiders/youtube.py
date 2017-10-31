# -*- coding: utf-8 -*-
import scrapy


class YoutubeSpider(scrapy.Spider):
    name = "youtube"
    allowed_domains = ["youtube.es"]
    start_urls = ['http://youtube.es/']

    def parse(self, response):
        pass
