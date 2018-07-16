import scrapy
import os
import csv
import yaml

from parser import Striper as striper

with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.load(config_file)


class ExtensionBotsSpider(scrapy.Spider):

    name = 'extension_bots_spider'

    start_urls = [
        'https://www.wikidata.org/wiki/Category:Extension_bots'
    ]

    custom_settings = {
        'LOG_FILE': config['log'],
        'LOG_LEVEL': config['log_level'],
    }

    def __init__(self, save_path='data/spiders/extension_bots.csv', **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        if os.path.isfile(self.save_path):
            os.remove(self.save_path)

    def parse(self, response):

        # extracting all extension bots
        bots = response.css('.mw-category > .mw-category-group > ul > li > a::text').extract()

        # strip bots name
        bots = striper.bulk_strip(bots)

        # loading already parsed bots
        if os.path.isfile(self.save_path):
            with open(self.save_path) as f:
                reader = csv.reader(f)
                for row in reader:
                    bots += row

        # make sure to have a unique set of bots
        bots = list(set(bots))

        # storing all bots
        with open(self.save_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(bots)

