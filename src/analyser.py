import csv
import re
import pandas as pd

from db import SqliteDb as db


class Analyser(object):

    files = [
        'data/parser/users_in_bot_group.csv',
        'data/spiders/bots_with_requests_for_permissions.csv',
        'data/spiders/bots_without_botflag.csv',
        'data/spiders/extension_bots.csv',
        'data/spiders/bots_with_botflag.csv',
    ]

    TIME_RE = re.compile('-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}$')

    SQL_MIN = " ASC LIMIT 1"
    SQL_MAX = " DESC LIMIT 1"

    @classmethod
    def count_bots_in_files(cls):

        for file in cls.files:
            with open(file) as f:
                reader = csv.reader(f)
                for row in reader:
                    print('%s: %s' %(file, len(row)))

    @classmethod
    def init_time_series(cls, from_time, until_time):

        time_series = {}

        from_year, from_month = from_time.split('-')
        until_year, until_month = until_time.split('-')

        years = range(int(from_year), int(until_year) + 1)
        months = range(1, 13)

        for index, year in enumerate(years):

            if index == 0:
                for month in months[(int(from_month) - 1):]:
                    if month < 10:
                        month = "0%s" % str(month)
                    time_series["%s-%s" % (str(year), str(month))] = 0
                continue

            if index == len(years) - 1:
                for month in months[:int(until_month)]:
                    if month < 10:
                        month = "0%s" % str(month)
                    time_series["%s-%s" % (str(year), str(month))] = 0
                continue

            for month in months:
                if month < 10:
                    month = "0%s" % str(month)
                time_series["%s-%s" % (str(year), str(month))] = 0

        return time_series

    @classmethod
    def plot_distribution_over_time(cls, sql):

        earliest_time = None
        result = db.execute(sql + cls.SQL_MIN)

        for item in result:
            earliest_time = re.sub(cls.TIME_RE, '', item[0])

        latest_time = None
        result = db.execute(sql + cls.SQL_MAX)

        for item in result:
            latest_time = re.sub(cls.TIME_RE, '', item[0])

        time_series = cls.init_time_series(earliest_time, latest_time)

        result = db.execute(sql)

        for item in result:
            time = re.sub(cls.TIME_RE, '', item[0])
            time_series[time] += 1

        cls.plot(time_series, 'Date')

    @classmethod
    def plot_distribution(cls, sql):

        min_value = cls.get_min_value(sql)
        max_value = cls.get_max_value(sql)

        distribution = {}
        for i in range(min_value, max_value + 1):
            distribution[i] = 0

        result = db.execute(sql)

        for item in result:
            distribution[item[0]] = item[1]

        cls.plot(distribution, 'Editor count')

    @classmethod
    def get_min_value(cls, sql):

        sql = sql.replace('GROUP', 'ORDER')

        result = db.execute(sql + cls.SQL_MIN)

        for item in result:
            return item[0]

    @classmethod
    def get_max_value(cls, sql):

        sql = sql.replace('GROUP', 'ORDER')

        result = db.execute(sql + cls.SQL_MAX)

        for item in result:
            return item[0]

    @staticmethod
    def plot(distribution, x_label):
        series = pd.Series(distribution, name='DateValue')
        series.index.name = x_label
        series.reset_index()
        series.plot(figsize=(15, 10), kind='bar')