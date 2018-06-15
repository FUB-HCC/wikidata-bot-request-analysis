import subprocess

from db import SqliteDb as db
from parser import BotsGroupParser as bp
from parser import BotsTableCreator as bc

spiders = [
    'archives_spider',
    'request_for_permission_spider',
    'requests_for_permissions_spider',
    'bots_with_botflag',
    'extension_bots'
    'bots_without_botflag',
    'bots_with_request_for_permissions',
]

db.reset()

# run all spiders
for spider in spiders:
    subprocess.call(['scrapy', 'runspieder', "src/%s.py" % spider])

bp.parse()
bc.create()

db.migrate()
