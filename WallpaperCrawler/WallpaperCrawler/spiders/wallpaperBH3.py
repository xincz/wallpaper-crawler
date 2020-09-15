# coding: utf-8

import re
import json
from urllib import parse

import scrapy
import requests
from scrapy import Request

from WallpaperCrawler.utils.common import get_md5
from WallpaperCrawler.items import WallpaperItem


class WallpaperCrawler(scrapy.Spider):
    name = 'wallpaperBH3'
    allowed_domains = ['www.bh3.com']
    start_urls = ['https://www.bh3.com/wallpapers']

    def parse(self, response):
        yield Request(url=parse.urljoin(response.url, '/content/bh3Cn/getContentList?pageSize=1000&pageNum=1&channelId=177'),
                      callback=self.parse_all)

        # image_nodes = response.xpath('//*[@class="paper-item"]')
        # for node in image_nodes:
        #     image_url = node.xpath('a/@href').extract_first()
        #     image_name = node.xpath('div/text()').extract_first()
        #     re_com = re.compile('.*?([\u4E00-\u9FA5]+)', re.S)
        #     image_name = re_com.findall(image_name)[0]
        #
        #     # Create items
        #     wallpaper_item = WallpaperItem()
        #     wallpaper_item['image_name'] = image_name
        #     wallpaper_item['image_url'] = []
        #     if image_url:
        #         wallpaper_item['image_url'] = [image_url]
        #
        #     yield wallpaper_item

    def parse_all(self, response):
        wallpaper_list = json.loads(response.text)['data']['list']

        for elt in wallpaper_list:
            image_url = elt['ext'][0]['value'][0]['url']
            image_name = elt['ext'][1]['value']
            match_obj = re.match('.*?([\u4E00-\u9FA5]+)', image_name)
            if match_obj:
                image_name = match_obj.group(1)

            # Create items
            wallpaper_item = WallpaperItem()
            wallpaper_item['image_name'] = image_name
            wallpaper_item['image_url'] = [image_url]
            wallpaper_item["image_id"] = get_md5(wallpaper_item["image_url"][0])

            yield wallpaper_item
