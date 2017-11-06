# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
from scrapy.selector import Selector
import csv
from scrapy.http import HtmlResponse
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

class YoutubeSpider(scrapy.Spider):
    name = 'youtube'
    start_urls = ['https://www.youtube.com/results?search_query=']

    def __init__(self):
        self.textToSearch = "#cocacola"
        self.page = 1
        self.uuid = 1
        self.collectedData = []
        self.getLikes = True
        dispatcher.connect(self.end, signals.spider_closed)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url + str(self.unifyUrlText(self.textToSearch)),
                          encoding='utf-8',
                          callback=self.search,
                          errback=self.errbackSearch)

    def search(self, response):
        if not 'No more results' in response.body_as_unicode():
            mainStructure = Selector(response=response).xpath('//div[contains(@class, "yt-lockup-content")]')
            for main in mainStructure:
                url = main.xpath('h3/a/@href').extract_first()
                title = main.xpath('h3/a/@title').extract_first()
                dataSessionlink = main.xpath('h3/a/@data-sessionlink').extract_first()
                duration = main.xpath('h3/span/text()').extract_first().split(' ')[-1].replace('.', '')
                info = main.xpath('div/ul[contains(@class, "yt-lockup-meta-info")]/li/text()').extract()
                creation = info[0] if len(info) > 1 else ''
                views = info[1] if len(info) > 1 else ''
                description = ''.join(main.xpath('div[contains(@dir, "ltr")]/descendant::text()').extract())
                channelLink = main.xpath('div/a/@href').extract_first()
                imgVideo = Selector(response=response).xpath('a[contains(@href, "' + url + '")]').extract()

                allInfoYoutube = dict()
                allInfoYoutube['uuid'] = str(self.uuid)
                self.uuid += 1
                allInfoYoutube['url'] = url.encode('utf-8').strip() if url is not None else ''
                allInfoYoutube['title'] = title.encode('utf-8').strip() if title is not None else ''
                allInfoYoutube['dataSessionlink'] = dataSessionlink.encode(
                    'utf-8').strip() if dataSessionlink is not None else ''
                allInfoYoutube['duration'] = duration.encode('utf-8').strip() if duration is not None else ''
                allInfoYoutube['creation'] = creation.encode('utf-8').strip() if creation is not None else ''
                allInfoYoutube['views'] = views.encode('utf-8').strip() if views is not None else ''
                allInfoYoutube['description'] = description.encode('utf-8').strip() if description is not None else ''
                allInfoYoutube['channel'] = channelLink.encode('utf-8').strip() if channelLink is not None else ''
                self.collectedData.append(allInfoYoutube)
            self.page += 1
            url = 'https://www.youtube.com/results?search_query=' + str(
                self.unifyUrlText(self.textToSearch)) + '&page=' + str(self.page)
            yield Request(url=url,
                          encoding='utf-8',
                          callback=self.search,
                          errback=self.errbackSearch)
        else:
            if self.getLikes:
                for info in self.collectedData:
                    uuid = info.get('uuid')
                    yield Request(url='https://www.youtube.com' + str(info.get('url', '')),
                                  encoding='utf-8',
                                  meta={'uuid':str(uuid),
                                        },
                                  callback=self.getLikesAndDislikes,
                                  errback=self.errbackSearch)

    def getLikesAndDislikes(self, response):
        uuid = response.meta['uuid']
        data = [data for data in self.collectedData if data.get('uuid') == uuid][0]
        likes = response.xpath('//div[contains(@class, "video-extras-sparkbar-likes")]/@style').extract_first()
        dislikes = response.xpath('//div[contains(@class, "video-extras-sparkbar-dislikes")]/@style').extract_first()
        likesNum = response.xpath('//span[contains(@class, "yt-uix-clickcard")]/*/span[contains(@class, "yt-uix-button-content")]').extract()
        data['plikes'] = None if likes is None else likes.split(':')[1].split('%')[0] if ':' in likes and '%' in likes else None
        data['pdislikes'] = None if dislikes is None else dislikes.split(':')[1].split('%')[0] if ':' in dislikes and '%' in dislikes else None
        if len(likesNum) > 4:
            likesNum, dislikesNum = likesNum[1], likesNum[3]
            likesNum = HtmlResponse(url='', body=likesNum, encoding='utf-8')
            likesNum = likesNum.xpath('//span/text()').extract_first()
            dislikesNum = HtmlResponse(url='', body=dislikesNum, encoding='utf-8')
            dislikesNum = dislikesNum.xpath('//span/text()').extract_first()
            data['likes'] = likesNum
            data['dislikes'] = dislikesNum
        else:
            likesNum, dislikesNum = None, None
            data['likes'] = likesNum
            data['dislikes'] = dislikesNum

    def errbackSearch(self, failure):
        return

    def end(self):
        self.toCSV(self.collectedData, 'cocacola')

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

    def toCSV(self, lst, nameFile):
        keys = lst[0].keys()
        with open(nameFile + '.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(lst)
