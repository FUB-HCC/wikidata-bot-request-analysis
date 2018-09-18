# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:////Users/admin/Git/wikidata-bot-request-analysis/db/wikidata_bot_requests_for_permissions.db')
Session = sessionmaker(bind=engine)

Base = declarative_base()