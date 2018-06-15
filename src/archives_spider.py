import scrapy
import re
import json


class WikidataArchivesSpider(scrapy.Spider):

    name = 'wikidata_archives_spider'

    start_urls = ['https://www.wikidata.org/wiki/Wikidata:Requests_for_permissions/Archive']

    base_url = 'https://www.wikidata.org'

    # Regex to match all hrefs which link to a bot request for permission archive
    bot_re = re.compile('^/wiki/Wikidata:Requests_for_permissions/RfBot/.+$')

    def __init__(self, save_path='data/spiders/archives.json', **kwargs):
        super().__init__(**kwargs)
        self.save_path = save_path

    def parse(self, response):

        # extracting all hrefs which link to a request for permission archive
        hrefs = response.css('li > a::attr(href)').extract()

        # filtering all bot request for permission archive hrefs
        hrefs = [href for href in hrefs if self.bot_re.match(href) is not None]

        # concatenating hrefs and base url to get the full url
        urls = ["%s%s" % (WikidataArchivesSpider.base_url, href) for href in hrefs]

        # save urls in a hash to be able to save it as json
        data = {'urls': urls}

        with open(self.save_path, 'w') as file:
            json.dump(data, file)
