import subprocess
import yaml
import logging

from db import SqliteDb as db
from parser import BotsGroupParser as bp
from parser import BotsTableCreator as bc

with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.load(config_file)
    logging.basicConfig(filename=config['log'], level=logging.DEBUG)

spiders = [
    'archives_spider',
    'request_for_permission_spider',
    'requests_for_permissions_spider',
    'bots_with_botflag_spider',
    'extension_bots_spider',
    'bots_without_botflag_spider',
    'bots_with_requests_for_permissions_spider',
]

db.reset()

# run all spiders
for spider in spiders:
    subprocess.call(['scrapy', 'runspider', "src/%s.py" % spider])

bp.parse()
bc.create()

db.migrate()
