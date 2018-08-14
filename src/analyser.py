import csv
import re
from datetime import datetime
import itertools

import pandas as pd

from plotly.offline import iplot
from plotly.graph_objs import Bar, Layout, Figure

from db import SqliteDb as db
from helper import print_df, print_names_and_count


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

    MATRIX_QUERIES = [
        {
            'sql': "SELECT DISTINCT bots.name FROM bots WHERE has_botflag = 1 AND redirect_of IS NULL",
            'matrix_keys': [['b_f', 'b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots WHERE has_botflag = 0 AND redirect_of IS NULL",
            'matrix_keys': [['no_b_f', 'no_b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots WHERE is_extension_bot = 1 AND redirect_of IS NULL",
            'matrix_keys': [['ex_b', 'ex_b']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots WHERE groups LIKE '%bot%' AND redirect_of IS NULL",
            'matrix_keys': [['group', 'group']],
        },
        {
            'sql': "SELECT DISTINCT bot_name FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL",
            'matrix_keys': [['request', 'request']],
        },
        {
            'sql': "SELECT DISTINCT bot_name FROM requests_for_permissions  INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL AND is_successful = 1",
            'matrix_keys': [['s_request', 's_request'], ['s_request', 'request']],
        },
        {
            'sql': "SELECT DISTINCT bot_name  FROM requests_for_permissions  INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL AND is_successful = 0",
            'matrix_keys': [['u_request', 'u_request'], ['u_request', 'request']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots WHERE bots.has_botflag = 1 AND bots.is_extension_bot = 1 AND redirect_of IS NULL",
            'matrix_keys': [['ex_b', 'b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots WHERE groups LIKE '%bot%' AND has_botflag = 1 AND redirect_of IS NULL",
            'matrix_keys': [['group', 'b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE bots.has_botflag = 1 AND redirect_of IS NULL",
            'matrix_keys': [['request', 'b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE bots.has_botflag = 1 AND requests_for_permissions.is_successful = 1 AND redirect_of IS NULL",
            'matrix_keys': [['s_request', 'b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE bots.has_botflag = 1 AND requests_for_permissions.is_successful = 0 AND redirect_of IS NULL",
            'matrix_keys': [['u_request', 'b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots WHERE bots.has_botflag = 0 AND bots.is_extension_bot = 1 AND redirect_of IS NULL",
            'matrix_keys': [['ex_b', 'no_b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots WHERE groups LIKE '%bot%' AND has_botflag = 0 AND redirect_of IS NULL",
            'matrix_keys': [['group', 'no_b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE bots.has_botflag = 0 AND redirect_of IS NULL",
            'matrix_keys': [['request', 'no_b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE bots.has_botflag = 0 AND requests_for_permissions.is_successful = 1 AND redirect_of IS NULL",
            'matrix_keys': [['s_request', 'no_b_f']],
        },
        {
            'sql': "SELECT DISTINCT bots.name FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE bots.has_botflag = 0 AND requests_for_permissions.is_successful = 0 AND redirect_of IS NULL",
            'matrix_keys': [['u_request', 'no_b_f']],
        },
        {
            'sql': "SELECT DISTINCT(bots.name) FROM bots WHERE groups LIKE '%bot%'AND is_extension_bot = 1  AND redirect_of IS NULL",
            'matrix_keys': [['group', 'ex_b']],
        },
        {
            'sql': "SELECT DISTINCT(bots.name) FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE is_extension_bot = 1 AND redirect_of IS NULL",
            'matrix_keys': [['request', 'ex_b']],
        },
        {
            'sql': "SELECT DISTINCT(bots.name) FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE is_extension_bot = 1 AND requests_for_permissions.is_successful = 1 AND redirect_of IS NULL",
            'matrix_keys': [['s_request', 'ex_b']],
        },
        {
            'sql': "SELECT DISTINCT(bots.name) FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE is_extension_bot = 1 AND requests_for_permissions.is_successful = 0 AND redirect_of IS NULL",
            'matrix_keys': [['u_request', 'ex_b']],
        },
        {
            'sql': "SELECT DISTINCT(bots.name) FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE groups LIKE '%bot%' AND redirect_of IS NULL",
            'matrix_keys': [['request', 'group']],
        },
        {
            'sql': "SELECT DISTINCT(bots.name) FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE groups LIKE '%bot%' AND requests_for_permissions.is_successful = 1 AND redirect_of IS NULL",
            'matrix_keys': [['s_request', 'group']],
        },
        {
            'sql': "SELECT DISTINCT(bots.name) FROM bots INNER JOIN requests_for_permissions ON requests_for_permissions.bot_name = bots.name WHERE groups LIKE '%bot%' AND requests_for_permissions.is_successful = 0 AND redirect_of IS NULL",
            'matrix_keys': [['u_request', 'group']],
        },
        {
            'sql': "SELECT DISTINCT(bot_name) FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE requests_for_permissions.is_successful = 1 AND bot_name IN (SELECT bot_name FROM requests_for_permissions WHERE requests_for_permissions.is_successful = 0) AND redirect_of IS NULL",
            'matrix_keys': [['u_request', 's_request']],
        },
    ]

    UNIQUE_BOTS_QUERY = "SELECT name FROM bots WHERE redirect_of IS NULL"

    BOTS_WITH_REQUEST_QUERY = "SELECT DISTINCT bot_name FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE bots.redirect_of IS NULL"
    BOTS_WITHOUT_REQUEST_QUERY = "SELECT name, rights FROM bots WHERE name IN (SELECT name FROM bots EXCEPT SELECT DISTINCT bot_name AS name FROM requests_for_permissions) AND redirect_of IS NULL"
    BOTS_WITH_BOT_FLAG_NOT_IN_BOT_GROUP_QUERY = "SELECT name FROM bots WHERE has_botflag = 1 AND groups NOT LIKE '%bot%' AND redirect_of IS NULL"
    BOTS_WITHOUT_BOT_FLAG_IN_BOT_GROUP_QUERY = "SELECT name FROM bots WHERE has_botflag = 0 AND groups LIKE '%bot%' AND redirect_of IS NULL"
    BOTS_WITH_BOT_FLAG_AND_IN_BOT_GROUP_QUERY = "SELECT name FROM bots WHERE has_botflag = 1 AND groups LIKE '%bot%' AND redirect_of IS NULL"

    RIGHTS_OF_BOTS_WITH_REQUEST_QUERY = "SELECT DISTINCT bot_name, rights, bot_has_red_link FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL;"
    RIGHTS_OF_BOTS_WITHOUT_REQUEST_QUERY = "SELECT name, rights FROM bots WHERE name IN (SELECT name FROM bots EXCEPT SELECT DISTINCT(bot_name) AS name FROM requests_for_permissions) AND redirect_of IS NULL"
    RIGHTS_OF_BOTS_WITH_BOT_FLAG_QUERY = "SELECT name, rights FROM bots WHERE has_botflag = 1 AND groups NOT LIKE '%bot%' AND redirect_of IS NULL"
    RIGHTS_OF_BOTS_IN_GROUP_BOT = "SELECT name, rights FROM bots WHERE has_botflag = 0 AND groups LIKE '%bot%' AND redirect_of IS NULL"

    GROUPS_OF_BOTS_WITH_REQUEST_QUERY = "SELECT DISTINCT bot_name, groups, bot_has_red_link FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL"
    GROUPS_OF_BOTS_WITHOUT_REQUEST_QUERY = "SELECT name, groups FROM bots WHERE name IN (SELECT name FROM bots EXCEPT SELECT DISTINCT(bot_name) AS name FROM requests_for_permissions) AND redirect_of IS NULL"

    REQUEST_WITHOUT_CLOSED_AT_QUERY = "SELECT url FROM requests_for_permissions WHERE closed_at = '' OR closed_at IS NULL"
    REQUEST_WITHOUT_EDITOR_COUNT_QUERY = "SELECT url FROM requests_for_permissions WHERE editor_count IS NULL"

    GROUPED_GROUPS_OF_BOTS_WITHOUT_IMPLICIT_GROUPS_QUERY = "SELECT groups, implicitgroups FROM bots WHERE groups NOT NULL AND redirect_of IS NULL"
    GROUPED_GROUPS_OF_BOTS_QUERY = "SELECT groups, COUNT(*) AS count FROM bots WHERE groups NOT NULL AND redirect_of IS NULL GROUP BY groups ORDER BY count DESC"

    EDITOR_COUNT_QUERIES = {
        'none': "SELECT url, editor_count FROM requests_for_permissions WHERE editor_count NOT NULL",
        'successful': "SELECT url, editor_count FROM requests_for_permissions WHERE editor_count NOT NULL AND is_successful = 1",
        'unsuccessful': "SELECT url, editor_count FROM requests_for_permissions WHERE editor_count NOT NULL AND is_successful = 0",
    }

    EDIT_COUNT_WITH_REGISTRATION_DATE_QUERY = "SELECT userid, name, editcount, registration FROM bots WHERE editcount NOT NULL AND registration NOT NULL AND redirect_of IS NULL"

    GENERAL_STATISTICS_ABOUT_REQUESTS_QUERIES = {
        'request': {
            'all': "SELECT COUNT(url) FROM requests_for_permissions",
            'successful': "SELECT COUNT(url) FROM requests_for_permissions WHERE is_successful = 1",
            'unsuccessful': "SELECT COUNT(url) FROM requests_for_permissions WHERE is_successful = 0",
        },
        'bot': {
            'all': "SELECT COUNT (DISTINCT bot_name) FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL",
            'successful': "SELECT COUNT (DISTINCT bot_name) FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL AND is_successful = 1",
            'unsuccessful': "SELECT COUNT (DISTINCT bot_name) FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL AND is_successful = 0",
        }
    }
    
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

        for item in db.execute(sql + cls.SQL_MIN):
            earliest_time = re.sub(cls.TIME_RE, '', item[0])

        latest_time = None

        for item in db.execute(sql + cls.SQL_MAX):
            latest_time = re.sub(cls.TIME_RE, '', item[0])

        time_series = cls.init_time_series(earliest_time, latest_time)

        result = db.execute(sql)

        for item in result:
            time = re.sub(cls.TIME_RE, '', item[0])
            time_series[time] += 1

        cls.plot(time_series, ['date', 'count'])

    @classmethod
    def plot_distribution(cls, sql):

        min_value = cls.get_min_value(sql + ''' ORDER BY editor_count''')
        max_value = cls.get_max_value(sql + ''' ORDER BY editor_count''')

        distribution = {}

        for i in range(min_value, max_value + 1):
            distribution[i] = 0

        for item in db.execute(sql):
            distribution[item[0]] = item[1]

        cls.plot(distribution, ['editor_count', 'count'])

    @classmethod
    def get_min_value(cls, sql):
        return [item[0] for item in db.execute(sql + cls.SQL_MAX)][0]

    @classmethod
    def get_max_value(cls, sql):
        return [item[0] for item in db.execute(sql + cls.SQL_MAX)][0]

    @staticmethod
    def plot(distribution, columns):

        df = pd.DataFrame(columns=columns)
        df[columns[0]] = distribution.keys()
        df[columns[1]] = distribution.values()

        iplot([Bar(
            x=df[columns[0]],
            y=df[columns[1]],
            marker=dict(
                color='rgb(235,173,104)',
                line=dict(
                    color='rgb(185,125,54)',
                    width=1.5),
            ),
            opacity=0.8
        )])

    @classmethod
    def generate_matrix(cls):

        index = ['b_f', 'no_b_f', 'ex_b', 'group', 'request', 's_request', 'u_request']
        df = pd.DataFrame(index=index, columns=index)

        for query in cls.MATRIX_QUERIES:
            bots, count = cls.retrieve_bots(query['sql'])

            for matrix_key in query['matrix_keys']:
                df[matrix_key[0]][matrix_key[1]] = count

        df['no_b_f']['b_f'] = 0

        print(df)

    @classmethod
    def print_matrix_bot_names(cls):

        for query in cls.MATRIX_QUERIES:
            bots, count = cls.retrieve_bots(query['sql'])

            for matrix_key in query['matrix_keys']:
                print('#################### Bots in ', matrix_key[0], ' and ', matrix_key[1],
                      " ####################\n", ', '.join(bots), "\n")

        print("#################### Bots in no_b_f and b_f ####################\n \n")

    @staticmethod
    def retrieve_bots(sql):
        bots = [item[0] for item in db.execute(sql)]
        return bots, len(bots)

    @classmethod
    def print_unique_bots(cls):

        print_names_and_count(
            set([
                item[0]
                for item
                in db.execute(cls.UNIQUE_BOTS_QUERY)
            ]),
            'unique bots'
        )

    @classmethod
    def print_bots_with_request(cls):

        print_names_and_count(
            set([
                item[0]
                for item
                in db.execute(cls.BOTS_WITH_REQUEST_QUERY)
            ]),
            'bots with a request for permission'
        )

    @classmethod
    def print_bots_without_request(cls):

        print_names_and_count(
            set([
                item[0]
                for item
                in db.execute(cls.BOTS_WITHOUT_REQUEST_QUERY)
            ]),
            'bots without a request for permission'
        )

    @classmethod
    def print_rights_of_bots_with_request(cls):

        data = {
            'right': list(itertools.chain.from_iterable(
                [
                    item[1].split(',')
                    for item
                    in db.execute(cls.RIGHTS_OF_BOTS_WITH_REQUEST_QUERY)
                    if item[1] is not None
                ]
            ))
        }

        df = pd.DataFrame(data)
        df = df.groupby(['right']).size().reset_index(name='count')
        df = df.sort_values(by=['count', 'right'], ascending=[False, True])

        print_df(df, ['right', 'count'], ['30', '30'])

    @classmethod
    def print_bots_with_request_without_rights(cls):

        bots_with_red_link = []
        # bots_with_right_and_redlink = []
        bots_without_red_link = []

        for item in db.execute(cls.RIGHTS_OF_BOTS_WITH_REQUEST_QUERY):
            if item[1] is None:
                if item[2] == 1:
                    bots_with_red_link.append(item[0])
                else:
                    bots_without_red_link.append(item[0])
        #    else:
        #        if item[2] == 1:
        #            bots_with_right_and_redlink.append(item[0])

        #print(
        #    "#################### Names of all bots with a request, with rights and a red link: ####################\n",
        #    ', '.join(bots_with_right_and_redlink), "\n")

        print_names_and_count(bots_with_red_link, 'bots with a request, without rights and a red link')
        print_names_and_count(bots_without_red_link, 'bots with a request, without rights and without a red link')

    @classmethod
    def print_rights_of_bots_without_request(cls):

        data = {
            'right': list(itertools.chain.from_iterable(
                [
                    item[1].split(',')
                    for item
                    in db.execute(cls.RIGHTS_OF_BOTS_WITHOUT_REQUEST_QUERY)
                    if item[1] is not None
                ]
            ))
        }

        df = pd.DataFrame(data)
        df = df.groupby(['right']).size().reset_index(name='count')
        df = df.sort_values(by=['count', 'right'], ascending=[False, True])

        print_df(df, ['right', 'count'], ['30', '30'])

    @classmethod
    def print_bots_without_request_without_rights(cls):

        print_names_and_count(
            set([
                item[0]
                for item
                in db.execute(cls.RIGHTS_OF_BOTS_WITHOUT_REQUEST_QUERY)
                if item[1] is None
            ]),
            'bots without a request and without rights'
        )

    @classmethod
    def print_right_differences_for_request(cls):

        with_request_rights = []

        for item in db.execute(cls.RIGHTS_OF_BOTS_WITH_REQUEST_QUERY):
            if item[1] is not None:
                with_request_rights += item[1].split(',')

        with_request_rights = set(with_request_rights)

        without_request_rights = []

        for item in db.execute(cls.RIGHTS_OF_BOTS_WITHOUT_REQUEST_QUERY):
            if item[1] is not None:
                without_request_rights += item[1].split(',')

        without_request_rights = set(without_request_rights)

        print(
            "#################### All rights that bots with a request for permission have but all other bots do not have: ####################\n",
            ', '.join(with_request_rights.difference(without_request_rights)), "\n")
        print(
            "#################### All rights that bots without a request for permission have but all other bots do not have: ####################\n",
            ', '.join(without_request_rights.difference(with_request_rights)), "\n")

    @classmethod
    def print_groups_of_bots_with_request(cls):

        data = {
            'group': list(itertools.chain.from_iterable(
                [
                    item[1].split(',')
                    for item
                    in db.execute(cls.GROUPS_OF_BOTS_WITH_REQUEST_QUERY)
                    if item[1] is not None
                ]
            ))
        }

        df = pd.DataFrame(data)
        df = df.groupby(['group']).size().reset_index(name='count')
        df = df.sort_values(by=['count', 'group'], ascending=[False, True])

        print_df(df, ['group', 'count'], ['30', '30'])

    @classmethod
    def print_bots_with_request_without_groups(cls):

        bots_with_red_link = []
        bots_without_red_link = []

        for item in db.execute(cls.GROUPS_OF_BOTS_WITH_REQUEST_QUERY):
            if item[1] is None:
                if item[2] == 1:
                    bots_with_red_link.append(item[0])
                else:
                    bots_without_red_link.append(item[0])

        print_names_and_count(bots_with_red_link, 'bots with a request, without groups and a red link')
        print_names_and_count(bots_without_red_link, 'bots with a request, without groups and without a red link')

    @classmethod
    def print_groups_of_bots_without_request(cls):

        data = {
            'group': list(itertools.chain.from_iterable(
                [
                    item[1].split(',')
                    for item
                    in db.execute(cls.GROUPS_OF_BOTS_WITHOUT_REQUEST_QUERY)
                    if item[1] is not None
                ]
            ))
        }

        df = pd.DataFrame(data)
        df = df.groupby(['group']).size().reset_index(name='count')
        df = df.sort_values(by=['count', 'group'], ascending=[False, True])

        print_df(df, ['group', 'count'], ['30', '30'])

    @classmethod
    def print_bots_without_request_without_groups(cls):

        print_names_and_count(
            set([
                item[0]
                for item
                in db.execute(cls.GROUPS_OF_BOTS_WITHOUT_REQUEST_QUERY)
                if item[1] is None
            ]),
            'bots without a request and without groups'
        )

    @classmethod
    def print_groups_differences(cls):

        with_request_groups = []

        for item in db.execute(cls.GROUPS_OF_BOTS_WITH_REQUEST_QUERY):
            if item[1] is not None:
                with_request_groups += item[1].split(',')

        with_request_groups = set(with_request_groups)

        without_request_groups = []

        for item in db.execute(cls.GROUPS_OF_BOTS_WITHOUT_REQUEST_QUERY):
            if item[1] is not None:
                without_request_groups += item[1].split(',')

        without_request_groups = set(without_request_groups)
        print(
            "#################### All groups that bots with a request for permission belong to but all other bots do not: ####################\n",
            ', '.join(with_request_groups.difference(without_request_groups)), "\n")
        print(
            "#################### All groups that bots without a request for permission belong to but all other bots do not: ####################\n",
            ', '.join(without_request_groups.difference(with_request_groups)), "\n")

    @classmethod
    def print_bots_with_bot_flag(cls):

        print_names_and_count(
            set([
                item[0]
                for item
                in db.execute(cls.BOTS_WITH_BOT_FLAG_NOT_IN_BOT_GROUP_QUERY)
            ]),
            'unique bots with a bot flag and do not belong to the group bot'
        )

    @classmethod
    def print_bots_in_bot_group(cls):

        print_names_and_count(
            set([
                item[0]
                for item
                in db.execute(cls.BOTS_WITHOUT_BOT_FLAG_IN_BOT_GROUP_QUERY)
            ]),
            'unique bots which belong to the group bot and do not have a bot flag'
        )

    @classmethod
    def print_bots_with_bot_flag_and_in_bot_group(cls):

        print_names_and_count(
            set([
                item[0]
                for item
                in db.execute(cls.BOTS_WITH_BOT_FLAG_AND_IN_BOT_GROUP_QUERY)
            ]),
            'unique bots with a bot flag and which belong to the group bot'
        )

    @classmethod
    def print_rights_of_bot_with_bot_flag(cls):

        data = {
            'right': []
        }

        for item in db.execute(cls.RIGHTS_OF_BOTS_WITH_BOT_FLAG_QUERY):
            if item[1] is not None:
                data['right'] += item[1].split(',')

        df = pd.DataFrame(data)
        df = df.groupby(['right']).size().reset_index(name='count')
        df = df.sort_values(by=['count', 'right'], ascending=[False, True])

        print_df(df, ['right', 'count'], ['30', '30'])

    @classmethod
    def print_rights_of_bot_in_bot_group(cls):

        data = {
            'right': []
        }

        for item in db.execute(cls.RIGHTS_OF_BOTS_IN_GROUP_BOT):
            if item[1] is not None:
                data['right'] += item[1].split(',')

        df = pd.DataFrame(data)
        df = df.groupby(['right']).size().reset_index(name='count')
        df = df.sort_values(by=['count', 'right'], ascending=[False, True])

        print_df(df, ['right', 'count'], ['30', '30'])

    @classmethod
    def print_right_differences_for_bot_flag_and_bot_group(cls):

        with_bot_flag_rights = []

        for item in db.execute(cls.RIGHTS_OF_BOTS_WITH_BOT_FLAG_QUERY):
            if item[1] is not None:
                with_bot_flag_rights += item[1].split(',')

        with_bot_flag_rights = set(with_bot_flag_rights)

        in_bot_group_rights = []

        for item in db.execute(cls.RIGHTS_OF_BOTS_IN_GROUP_BOT):
            if item[1] is not None:
                in_bot_group_rights += item[1].split(',')

        in_bot_group_rights = set(in_bot_group_rights)

        print(
            "#################### All rights that bots with a bot flag have but bots in bot group do not have: ####################\n",
            ', '.join(with_bot_flag_rights.difference(in_bot_group_rights)), "\n")
        print(
            "#################### All rights that bots which belong to the bot group have but bots with a bot flag do not have: ####################\n",
            ', '.join(in_bot_group_rights.difference(with_bot_flag_rights)), "\n")

    @classmethod
    def print_request_for_permission_without_closed_at(cls):

        print_names_and_count(
            [
                item[0]
                for item
                in db.execute(cls.REQUEST_WITHOUT_CLOSED_AT_QUERY)
            ],
            'requests for permissions without closed_at',
            "\n"
        )

    @classmethod
    def print_request_for_permission_without_editor_count(cls):

        print_names_and_count(
            [
                item[0]
                for item
                in db.execute(cls.REQUEST_WITHOUT_EDITOR_COUNT_QUERY)
             ],
            'requests for permissions without editor_count',
            "\n"
        )

    @classmethod
    def plot_general_statistics_about_requests(cls):

        data = {
            'request': {},
            'bot': {}
        }

        for target in cls.GENERAL_STATISTICS_ABOUT_REQUESTS_QUERIES.keys():
            for statistic, query in cls.GENERAL_STATISTICS_ABOUT_REQUESTS_QUERIES[target].items():
                for item in db.execute(query):
                    data[target][statistic] = item[0]

        trace0 = Bar(
            y=list(data['request'].keys()),
            x=list(data['request'].values()),
            name='Requests for Permissions',
            orientation='h',
            marker=dict(
                color='rgb(235,173,104)',
                line=dict(
                    color='rgb(185,125,54)',
                    width=1.5),
            ),
            opacity=0.8
        )
        trace1 = Bar(
            y=list(data['bot'].keys()),
            x=list(data['bot'].values()),
            name='Bots',
            orientation='h',
            marker=dict(
                color='rgb(204,204,204)',
                line=dict(
                    color='rgb(150,150,150)',
                    width=1.5),
            ),
            opacity=0.8
        )

        data = [trace0, trace1]
        layout = Layout(
            xaxis=dict(tickangle=-45),
            barmode='group',
        )

        fig = Figure(data=data, layout=layout)
        iplot(fig, filename='angled-text-bar')

    @classmethod
    def print_edit_count(cls):

        data = {
            'userid': [],
            'bot': [],
            'edit_count': [],
            'registration': []
        }

        for item in db.execute(cls.EDIT_COUNT_WITH_REGISTRATION_DATE_QUERY):
            data['userid'].append(item[0])
            data['bot'].append(item[1])
            data['edit_count'].append(item[2])
            data['registration'].append(str(datetime.strptime(item[3], '%Y-%m-%dT%H:%M:%SZ').date()))

        df = pd.DataFrame(data)
        df = df.sort_values(by=['edit_count', 'bot'])

        print_df(df, ['userid', 'bot', 'edit_count', 'registration'], ['12', '35', '12', '20'])

    @classmethod
    def print_average_edit_count_per_day(cls):

        data = {
            'userid': [],
            'bot': [],
            'edit_count_per_day': [],
            'registration': []
        }

        for item in db.execute(cls.EDIT_COUNT_WITH_REGISTRATION_DATE_QUERY):
            data['userid'].append(item[0])
            data['bot'].append(item[1])

            registration_date = datetime.strptime(item[3], '%Y-%m-%dT%H:%M:%SZ')
            current_date = datetime.now()
            days_since_registration = (current_date - registration_date).days
            edit_count_per_day = int(item[2] / days_since_registration)

            data['edit_count_per_day'].append(edit_count_per_day)
            data['registration'].append(str(registration_date.date()))

        df = pd.DataFrame(data)
        df = df.sort_values(by=['edit_count_per_day', 'bot'])

        print_df(df, ['userid', 'bot', 'edit_count_per_day', 'registration'], ['12', '35', '20', '20'])

    @classmethod
    def print_editor_count(cls, mode='none'):

        data = {
            'url': [],
            'editor_count': []
        }

        for item in db.execute(cls.EDITOR_COUNT_QUERIES[mode]):
            data['url'].append(item[0])
            data['editor_count'].append(item[1])

        df = pd.DataFrame(data)
        df = df.sort_values(by=['editor_count', 'url'])

        print_df(df, ['url', 'editor_count'], ['90', '15'])

    @classmethod
    def plot_bots_groups_distribution(cls):

        data = {
            'groups': [],
            'count': []
        }

        for item in db.execute(cls.GROUPED_GROUPS_OF_BOTS_QUERY):
            groups = item[0].split(',')
            groups.sort()
            data['groups'].append(', '.join(groups))
            data['count'].append(item[1])

        df = pd.DataFrame(data)
        df['%'] = round(df['count'] / df['count'].sum() * 100, 2)

        print_df(df, ['groups', 'count', '%'], ['60', '15', '15'])

    @classmethod
    def plot_bots_groups_without_implicit_groups_distribution(cls):

        data = {
            'groups': []
        }

        for item in db.execute(cls.GROUPED_GROUPS_OF_BOTS_WITHOUT_IMPLICIT_GROUPS_QUERY):
            all_groups = set(item[0].split(','))
            implicit_groups = set(item[1].split(','))
            explicit_groups = all_groups - implicit_groups
            explicit_groups = list(explicit_groups)
            explicit_groups.sort()
            data['groups'].append(', '.join(explicit_groups))

        df = pd.DataFrame(data)
        df = df.groupby(['groups']).size().reset_index(name='count')
        df = df.sort_values(by=['count', 'groups'], ascending=[False, True])
        df['%'] = round(df['count'] / df['count'].sum() * 100, 2)

        print_df(df, ['groups', 'count', '%'], ['40', '15', '15'])
