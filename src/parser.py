import datetime
import os
import csv
import re

from api import MediaWikiAPI
from db import SqliteDb as db


class BotStriper(object):

    # pattern to replace the request number
    REQUEST_NUMBER_RE = re.compile('\s[0-9]+$')

    # pattern to identify a red link
    RED_LINK_RE = re.compile('.*redlink=1$')

    @classmethod
    def bulk_strip(cls, bots, replace_request_number=False):
        return [cls.strip(bot, replace_request_number) for bot in bots]

    @classmethod
    def strip(cls, bot, replace_request_number=False):

        if bot is None:
            return None

        if cls.RED_LINK_RE.match(bot):
            bot = bot.replace('/w/index.php?title=User:', '')
            bot = bot.replace('&action=edit&redlink=1', '')

        bot = bot.replace('/wiki/', '')
        bot = bot.replace('User:', '')
        bot = bot.replace('_', ' ')

        if replace_request_number:
            bot = re.sub(cls.REQUEST_NUMBER_RE, '', bot)

        return bot


class BotsGroupParser(object):

    SAVE_PATH = 'data/parser/users_in_bot_group.csv'

    @classmethod
    def parse(cls):

        response = MediaWikiAPI.allusers()

        while len(response['query']['allusers']) > 0:

            bots = []

            for bot in response['query']['allusers']:
                bots.append(bot['name'])

            bots = BotStriper.bulk_strip(bots)

            if os.path.isfile(cls.SAVE_PATH):
                with open(cls.SAVE_PATH) as f:
                    reader = csv.reader(f)
                    for row in reader:
                        bots += row

            with open(cls.SAVE_PATH, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(set(bots))

            if 'query-continue' not in response:
                break

            response = MediaWikiAPI.allusers(augroup='bot', aufrom=response['query-continue']['allusers']['aufrom'])


class BotsTableCreator(object):

    FILES = [
        'data/parser/users_in_bot_group.csv',
        'data/spiders/bots_with_requests_for_permissions.csv',
        'data/spiders/bots_without_botflag.csv',
        'data/spiders/extension_bots.csv',
        'data/spiders/bots_with_botflag.csv',
    ]

    @classmethod
    def create(cls):

        bots_with_botflag = []
        bots_without_botflag = []
        extension_bots = []
        bots = []

        for file in cls.FILES:
            with open(file) as f:
                reader = csv.reader(f)
                bots += [row for row in reader][0]

        with open('data/spiders/bots_with_botflag.csv') as f:
            reader = csv.reader(f)
            bots_with_botflag += [row for row in reader][0]

        with open('data/spiders/bots_without_botflag.csv') as f:
            reader = csv.reader(f)
            bots_without_botflag += [row for row in reader][0]

        with open('data/spiders/extension_bots.csv') as f:
            reader = csv.reader(f)
            extension_bots += [row for row in reader][0]

        bots = set(bots)

        batches = [list(bots)[i*50:(i+1)*50] for i in range(int(len(bots) / 50) + 1)]

        for batch in batches:

            for bot in MediaWikiAPI.users(batch)['query']['users']:

                if db.exists('bots', 'name', bot['name']):
                    continue

                bot['retrieved_at'] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                bot['has_botflag'] = 1 if bot['name'] in bots_with_botflag else 0 if bot['name'] in bots_without_botflag else None
                bot['is_extension_bot'] = 1 if bot['name'] in extension_bots else 0

                if 'invalid' in bot or 'missing' in bot:
                    bot = {
                        'name': bot['name'],
                        'retrieved_at': bot['retrieved_at'],
                        'has_botflag': bot['has_botflag'],
                        'is_extension_bot': bot['is_extension_bot']
                    }
                    db.insert('bots', bot)
                    continue

                bot.pop('blockinfo', None)

                bot['groups'] = ','.join(bot['groups'])
                bot['implicitgroups'] = ','.join(bot['implicitgroups'])
                bot['rights'] = ','.join(bot['rights'])
                bot['blockid'] = bot['blockid'] if 'blockid' in bot else None
                bot['blockedby'] = bot['blockedby'] if 'blockedby' in bot else None
                bot['blockedbyid'] = bot['blockedbyid'] if 'blockedbyid' in bot else None
                bot['blockedtimestamp'] = bot['blockedtimestamp'] if 'blockedtimestamp' in bot else None
                bot['blockreason'] = bot['blockreason'] if 'blockreason' in bot else None
                bot['blockexpiry'] = bot['blockexpiry'] if 'blockexpiry' in bot else None

                db.insert('bots', bot)

# BotsTableCreator.create()