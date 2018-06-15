import scrapy
import json
import datetime
import re

from db import SqliteDb as db
from api import MediaWikiAPI
from parser import BotStriper as bs


class WikidataRequestForPermissionSpider(scrapy.Spider):

    name = 'wikidata_request_for_permission_spider'
    base_url = 'www.wikidata.org'
    json_data = json.load(open('data/spiders/requests_for_permissions.json'))
    start_urls = json_data['urls']  # json.load(open('data/spiders/requests_for_permissions.json'))['urls']

    xpath = {
        'symbols': {
            'comment': '//img[@src="//upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Pictogram_voting_comment.svg/15px-Pictogram_voting_comment.svg.png"]',
            'question': '//img[@src="//upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Pictogram_voting_question.svg/15px-Pictogram_voting_question.svg.png"]',
            'oppose': '//img[@src="//upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Symbol_oppose_vote.svg/15px-Symbol_oppose_vote.svg.png"]',
            'answer': '//img[@src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Symbol_reply.svg/15px-Symbol_reply.svg.png"]',
            'support': '//img[@src="//upload.wikimedia.org/wikipedia/commons/thumb/9/94/Symbol_support_vote.svg/15px-Symbol_support_vote.svg.png"]',
        },
        'closed_at': [
            '(//p/i[text()="The following discussion is closed. "]/../following::dl[1]/dd/dl/dd/text())[last()]',
            '(//i[text()="A summary of the conclusions reached follows."]/../following::dl[1]/dd/text())[last()]',
        ],
        'bot': [
            '//h3/span[@class="mw-headline"]/a/@href',
            '//h3/span[@class="mw-headline"]/strike/a/@href',
            '//h3/span[@class="mw-headline"]/a/text()',
            '//h2/span[@class="mw-headline"]/a/text()',
        ],
        'bot_name': [
            '//h3/span[@class="mw-headline"]/a/@href',
            '//h3/span[@class="mw-headline"]/strike/a/@href',
            '//h3/span[@class="mw-headline"]/a/text()',
            '//h2/span[@class="mw-headline"]/a/text()',
        ],
        'summary': [
            '//p/i[text()="The following discussion is closed. "]/../following::dl[1]/dd/dl/dd',
            '//i[text()="A summary of the conclusions reached follows."]/../following::dl[1]/dd',
        ],
        'operator': [
            '//b[text()="Operator:"]/following::a/@href',
            '//b[text()="Operators:"]/following::a/@href',
            '//b[text()="Оператор/Operator:"]/following::a/@href',
            '//dd[text()="Operator:"]/a/@href',
            '//dd[text()="Operator: "]/a/@href',
            '//dd[text()="Operator "]/a/@href',
            '//li[text()="Operator: "]/a/@href',
            '//li[text()="Bot owner: "]/span/a/@href',
        ],
        'task': [
            '//b[text()="Task/s:"]/..',
            '//dd[text()="Task/s:"]/..',
        ],
        'code': [
            '//b[text()="Code:"]/..',
        ],
        'function': [
            '//b[text()="Function details:"]/..',
        ],
    }

    red_link = re.compile('.*redlink=1$')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.reset()

    def parse(self, response):

        data = {
            'bot': None,
            'bot_name': None,
            'operator': None,
            'task': None,
            'code': None,
            'function': None,
            'closed_at': None,
            'summary': None,
        }

        for key in data.keys():
            for matcher in self.xpath[key]:
                matches = response.xpath(matcher)
                if len(matches) > 0:
                    data[key] = matches[0].extract()
                    break

        for key in ['bot', 'operator']:
            if data[key] is not None:
                data[key] = self.get_url(data[key])

        if data['bot_name'] is not None:
            data['bot_name'] = bs.stripe([data['bot_name']], replace_request_number=True)[0]

        if data['closed_at'] is not None:
            data['closed_at'] = re.sub(r'[()]\s?', '', data['closed_at']).replace(' UTC', '').replace('] ', '').lstrip()
            try:
                data['closed_at'] = datetime.datetime.strptime(data['closed_at'], '%H:%M, %d %B %Y')
            except:
                pass

        data = {**data, **{
            'url': response.url.replace('https://', ''),
            'is_successful': 1 if response.url in self.json_data['successful_requests'] else 0,
            'html': response.css('div#bodyContent').extract_first(),
            'retrieved_at': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            'archive_comment': self.json_data['successful_requests'][response.url]['comment'] if response.url in self.json_data['successful_requests'] else self.json_data['unsuccessful_requests'][response.url]['comment']
        }}

        if not data['archive_comment']:
            data['archive_comment'] = None

        response = MediaWikiAPI.revisions([data['url'].replace('www.wikidata.org/wiki/', '')])

        data = {**data, **{
            'revision_count': len(response['query']['pages'][0]['revisions']),
            'editor_count': len(set([rev['user'] for rev in response['query']['pages'][0]['revisions']])),
            'first_edit': response['query']['pages'][0]['revisions'][-1]['timestamp'],
            'last_edit': response['query']['pages'][0]['revisions'][0]['timestamp'],
        }}

        for key, symbol in self.xpath['symbols'].items():
            data[key + '_symbol_count'] = len(response.xpath(symbol))

        db.insert('requests_for_permissions', data)

    @classmethod
    def get_url(cls, name):

        if name is None:
            return None

        if cls.red_link.match(name):
            return cls.base_url + name

        if 'https://' not in name:
            if '/wiki/User:' not in name:
                name = '/wiki/User:' + name
            name = cls.base_url + name
        else:
            name = name.replace('https://', 'www.')

        return name
