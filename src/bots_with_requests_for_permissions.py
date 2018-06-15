import scrapy
import json
import csv
import os
import re

from parser import BotStriper as bs


class WikidataBotsWithRequestsForPermissionsSpider(scrapy.Spider):

    name = 'wikidata_bots_with_requests_for_permissions_spider'

    start_urls = json.load(open('data/spiders/requests_for_permissions.json'))['urls']

    # xpath patterns to find the bots name or href the request is for
    xpath = [
        '//h3/span[@class="mw-headline"]/a/@href',
        '//h3/span[@class="mw-headline"]/strike/a/@href',
        '//h3/span[@class="mw-headline"]/a/text()',
        '//h2/span[@class="mw-headline"]/a/text()',
    ]

    # pattern to replace the request number if given to only get the bot name or href
    request_number_re = re.compile('\s[0-9]+$')

    def __init__(self, save_path='data/spiders/bots_with_requests_for_permissions.csv', **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        if os.path.isfile(self.save_path):
            os.remove(self.save_path)

    def parse(self, response):

        bots = []

        for matcher in self.xpath:
            # find bots name or href
            matches = response.xpath(matcher)
            if len(matches) > 0:
                # extracting bots name or href
                bot = matches[0].extract()
                # strip bots name
                bots = bs.strip(bots, replace_request_number=True)
                bots.append(bot)
                break

        # loading already parsed bots
        if os.path.isfile(self.save_path):
            with open(self.save_path) as f:
                reader = csv.reader(f)
                for row in reader:
                    bots += row

        # storing all bots
        with open(self.save_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(set(bots))
