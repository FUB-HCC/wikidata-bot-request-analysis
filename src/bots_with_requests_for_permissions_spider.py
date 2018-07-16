import scrapy
import json
import csv
import os
import yaml

from parser import Striper as striper

with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.load(config_file)


class BotsWithRequestsForPermissionsSpider(scrapy.Spider):

    name = 'bots_with_requests_for_permissions_spider'

    start_urls = json.load(open('data/spiders/requests_for_permissions.json'))['urls']

    custom_settings = {
        'LOG_FILE': config['log'],
        'LOG_LEVEL': config['log_level'],
    }

    # xpath patterns to find the bots name or href the request is for
    XPATH = [
        '//h3/span[@class="mw-headline"]/a/@href',
        '//h3/span[@class="mw-headline"]/strike/a/@href',
        '//h3/span[@class="mw-headline"]/a/text()',
        '//h2/span[@class="mw-headline"]/a/text()',
    ]

    def __init__(self, save_path='data/spiders/bots_with_requests_for_permissions.csv', **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        if os.path.isfile(self.save_path):
            os.remove(self.save_path)

    def parse(self, response):

        bots = []

        for matcher in self.XPATH:
            # find bots name or href
            matches = response.xpath(matcher)
            if len(matches) > 0:
                # extracting bots name or href
                bot = matches[0].extract()
                # strip bots name
                bot = striper.strip(bot, replace_request_number=True)
                bots.append(bot)
                break

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
            writer.writerow(set(bots))
