import scrapy
import os
import json
import re
import yaml

with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.load(config_file)


class RequestsForPermissionsSpider(scrapy.Spider):

    name = 'requests_for_permissions_spider'

    base_url = 'https://www.wikidata.org'

    start_urls = json.load(open('data/spiders/archives.json'))['urls']

    custom_settings = {
        'LOG_FILE': config['log'],
        'LOG_LEVEL': config['log_level'],
    }

    RED_LINK_RE = re.compile('.*redlink=1$')

    def __init__(self, save_path='data/spiders/requests_for_permissions.json', **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path
        if os.path.isfile(self.save_path):
            os.remove(self.save_path)

    def parse(self, response):

        if os.path.isfile(self.save_path):
            with open(self.save_path) as file:
                data = json.load(file)

        else:
            data = {
                'urls': [],
                'successful_requests': {},
                'unsuccessful_requests': {}
            }

        if response.url == 'www.wikidata.org/wiki/Category:Archived_requests_for_permissions':
            return

        if self.RED_LINK_RE.match(response.url) is not None:
            return

        for key in data.keys():
            for li in response.xpath("//h1/span[@id='%s']/../following::ul[1]/li" % key.capitalize()):
                url = "%s%s" % (self.base_url, li.css('li > a::attr(href)').extract()[0])

                if 'wiki/Category:Archived_requests_for_permissions' in url or self.RED_LINK_RE.match(url) is not None:
                    continue

                if url not in data['urls']:
                    data['urls'].append(url)

                if url in data[key]:
                    data[key][url]['archive_url'].append(response.url)
                else:
                    data[key][url] = {
                        'comment': li.css('li::text').extract()[0] if len(li.css('li::text').extract()) > 0 else '',
                        'archive_url': [response.url]
                    }

        with open(self.save_path, 'w') as file:
            json.dump(data, file)
