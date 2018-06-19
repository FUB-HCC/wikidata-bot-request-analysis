import scrapy
import re
import json
import yaml

with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.load(config_file)


class ArchivesSpider(scrapy.Spider):

    name = 'archives_spider'

    start_urls = [
        'https://www.wikidata.org/wiki/Wikidata:Requests_for_permissions/Archive'
    ]

    custom_settings = {
        'LOG_FILE': config['log'],
        'LOG_LEVEL': config['log_level'],
    }

    base_url = 'https://www.wikidata.org'

    # Regex to match all hrefs which link to a bot request for permission archive
    BOT_RE = re.compile('^/wiki/Wikidata:Requests_for_permissions/RfBot/.+$')

    def __init__(self, save_path='data/spiders/archives.json', **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path

    def parse(self, response):

        # extracting all hrefs which link to a request for permission archive
        hrefs = response.css('li > a::attr(href)').extract()

        # filtering all bot request for permission archive hrefs
        hrefs = [href for href in hrefs if self.BOT_RE.match(href) is not None]

        # concatenating hrefs and base url to get the full url
        urls = ["%s%s" % (self.base_url, href) for href in hrefs]

        # save urls in a hash to be able to save it as json
        data = {'urls': urls}

        with open(self.save_path, 'w') as file:
            json.dump(data, file)
