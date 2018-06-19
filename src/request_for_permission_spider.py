import scrapy
import json
import datetime
import re
import yaml

from db import SqliteDb as db
from api import MediaWikiAPI
from parser import BotStriper as bs

with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.load(config_file)


class RequestForPermissionSpider(scrapy.Spider):

    name = 'request_for_permission_spider'

    base_url = 'www.wikidata.org'

    json_data = json.load(open('data/spiders/requests_for_permissions.json'))

    start_urls = json_data['urls']  # json.load(open('data/spiders/requests_for_permissions.json'))['urls']

    custom_settings = {
        'LOG_FILE': config['log'],
        'LOG_LEVEL': config['log_level'],
    }

    XPATH = {
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

    # pattern to identify a red link
    RED_LINK_RE = re.compile('.*redlink=1$')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.reset()

    def parse(self, response):

        api_response = MediaWikiAPI.revisions([response.url.replace('https://www.wikidata.org/wiki/', '')])

        bot = self.get_bot(response)

        data = {
            'url': response.url.replace('https://', ''),
            'bot': bot,
            'bot_name': self.get_bot_name(response),
            'bot_has_red_link': 1 if self.RED_LINK_RE.match(bot) else 0,
            'operator': self.get_operator(response),
            'is_successful': 1 if response.url in self.json_data['successful_requests'] else 0,
            'first_edit': self.get_first_edit(api_response),
            'last_edit': self.get_last_edit(api_response),
            'closed_at': self.get_closed_at(response),
            'revision_count': self.get_revision_count(api_response),
            'editor_count': self.get_editor_count(api_response),
            'html': response.css('div#bodyContent').extract_first(),
            'task': None,
            'code': None,
            'function': None,
            'archive_comment': self.get_archive_comment(response.url),
            'summary': None,
            'retrieved_at': datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }

        for key in ['task', 'code', 'function', 'summary']:
            data[key] = self.xpath(key, response)

        for key, symbol in self.XPATH['symbols'].items():
            data[key + '_symbol_count'] = len(response.xpath(symbol))

        db.insert('requests_for_permissions', data)

    def get_bot(self, response):

        bot = self.xpath('bot', response)
        bot = self.get_url(bot)

        return bot

    def get_bot_name(self, response):

        bot_name = self.xpath('bot_name', response)
        bot_name = bs.strip(bot_name, replace_request_number=True)

        return bot_name

    def get_operator(self, response):

        operator = self.xpath('operator', response)
        operator = self.get_url(operator)

        return operator

    def get_first_edit(self, api_response):

        if 'revisions' not in api_response['query']['pages'][0]:
            return None

        return api_response['query']['pages'][0]['revisions'][-1]['timestamp']

    def get_last_edit(self, api_response):

        if 'revisions' not in api_response['query']['pages'][0]:
            return None

        return api_response['query']['pages'][0]['revisions'][0]['timestamp']

    def get_closed_at(self, response):

        closed_at = self.xpath('closed_at', response)

        if closed_at is None:
            return None

        closed_at = re.sub(r'[()]\s?', '', closed_at)
        closed_at = closed_at.replace(' UTC', '')
        closed_at = closed_at.replace('] ', '')
        closed_at = closed_at.lstrip()

        try:
            closed_at = datetime.datetime.strptime(closed_at, '%H:%M, %d %B %Y')
        except:
            pass

        return closed_at

    def get_revision_count(self, api_response):

        if 'revisions' not in api_response['query']['pages'][0]:
            return None

        return len(api_response['query']['pages'][0]['revisions'])

    def get_archive_comment(self, url):
        if url in self.json_data['successful_requests']:
            comment = self.json_data['successful_requests'][url]['comment']
        else:
            comment = self.json_data['unsuccessful_requests'][url]['comment']

        if not comment:
            comment = None

        return comment

    def get_editor_count(self, api_response):

        editors = []

        if 'revisions' not in api_response['query']['pages'][0]:
            return None

        for revision in api_response['query']['pages'][0]['revisions']:
            if 'user' in revision:
                editors.append(revision['user'])
            elif 'userhidden' in revision:
                editors.append('hiddenuser')
            else:
                raise Exception('Unknown key in revision (neither user nor userhidden is available)')

        return len(set(editors))

    def get_url(self, user):

        if user is None:
            return None

        if self.RED_LINK_RE.match(user):
            return self.base_url + user

        if 'https://' not in user:
            if '/wiki/User:' not in user:
                user = '/wiki/User:' + user
            user = self.base_url + user
        else:
            user = user.replace('https://', 'www.')

        return user

    def xpath(self, key, response):

        result = None

        for matcher in self.XPATH[key]:
            matches = response.xpath(matcher)
            if len(matches) > 0:
                result = matches[0].extract()
                break

        return result
