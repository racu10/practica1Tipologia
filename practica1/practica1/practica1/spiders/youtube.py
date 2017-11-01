# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request, FormRequest
from scrapy.contrib.loader import ItemLoader


class YoutubeSpider(scrapy.Spider):
    name = 'youtube'
    start_urls = ['https://www.youtube.com/results?search_query=']

    def __init__(self):
        self.textToSearch = "#cocacola"
        self.collectedData = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url + str(self.unifyUrlText(self.textToSearch)),
                          encoding='utf-8',
                          callback=self.search,
                          errback=self.errbackSearch)

    def search(self, respone):
        mainStructure = respone.xpath('//div[contains(@class, "yt-lockup-content")]')
        for main in mainStructure:
            url = main.xpath('h3/a/@href').extract_first()
            title = main.xpath('h3/a/@title').extract_first()
            dataSessionlink = main.xpath('h3/a/@data-sessionlink').extract_first()
            duration = main.xpath('h3/span/text()').extract_first().split(' ')[-1].replace('.', '')
            info = main.xpath('div/ul[contains(@class, "yt-lockup-meta-info")]/li/text()').extract()
            creation = info[0] if len(info) > 1 else None
            views = info[1] if len(info) > 1 else None
            description = ''.join(main.xpath('div[contains(@dir, "ltr")]/descendant::text()').extract())

            allInfoYoutube = dict()
            allInfoYoutube['url'] = url
            allInfoYoutube['title'] = title
            allInfoYoutube['dataSessionlink'] = dataSessionlink
            allInfoYoutube['duration'] = duration
            allInfoYoutube['creation'] = creation
            allInfoYoutube['views'] = views
            allInfoYoutube['description'] = description
            self.collectedData.append(allInfoYoutube)
        print(len(self.collectedData))
        print(self.collectedData)
        return

    def errbackSearch(self, failure):
        return

    '''
    Funciones
    '''

    def unifyUrlText(self, text):
        return text \
            .replace("%", "%25") \
            .replace("/", "%2F") \
            .replace("*", "%2A") \
            .replace("+", "%2B") \
            .replace("$", "%24") \
            .replace("&", "%26") \
            .replace("(", "%28") \
            .replace(")", "%29") \
            .replace("=", "%3D") \
            .replace("'", "%27") \
            .replace("?", "%3F") \
            .replace("^", "%5E") \
            .replace(":", "%3A") \
            .replace(";", "%3B") \
            .replace("{", "%7B") \
            .replace("}", "%7D") \
            .replace("[", "%5B") \
            .replace("]", "%5D") \
            .replace("#", "%23") \
            .replace(" ", "+")
