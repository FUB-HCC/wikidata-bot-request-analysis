import scrapy
import os
import csv

from parser import BotStriper as bs

class WikidataExtensionBotsSpider(scrapy.Spider):

    name = 'wikidata_extension_bots_spider'

    start_urls = [
        'https://www.wikidata.org/wiki/Category:Extension_bots'
    ]

    def __init__(self, save_path='data/spiders/extension_bots.csv', **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        if os.path.isfile(self.save_path):
            os.remove(self.save_path)

    def parse(self, response):

        # extracting all extension bots
        bots = response.css('.mw-category > .mw-category-group > ul > li > a::text').extract()

        # strip bots name
        bots = bs.strip(bots)

        # loading already parsed bots
        if os.path.isfile(self.save_path):
            with open(self.save_path) as f:
                reader = csv.reader(f)
                for row in reader:
                    bots += row

        # storing all bots
        with open(self.save_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(bots)

