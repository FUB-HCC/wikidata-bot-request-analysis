import csv
import re
import pandas as pd
from datetime import datetime

from db import SqliteDb as db
from plotly.offline import iplot
from plotly.graph_objs import Bar, Layout, Figure


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
    BOTS_WITH_BOT_FLAG_NOT_IN_BOT_GROUP = "SELECT name FROM bots WHERE has_botflag = 1 AND groups NOT LIKE '%bot%' AND redirect_of IS NULL"
    BOTS_WITHOUT_BOT_FLAG_IN_BOT_GROUP = "SELECT name FROM bots WHERE has_botflag = 0 AND groups LIKE '%bot%' AND redirect_of IS NULL"
    BOTS_WITH_BOT_FLAG_AND_IN_BOT_GROUP = "SELECT name FROM bots WHERE has_botflag = 1 AND groups LIKE '%bot%' AND redirect_of IS NULL"

    RIGHTS_OF_BOTS_WITH_REQUEST_QUERY = "SELECT DISTINCT bot_name, rights, bot_has_red_link FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL;"
    RIGHTS_OF_BOTS_WITHOUT_REQUEST_QUERY = "SELECT name, rights FROM bots WHERE name IN (SELECT name FROM bots EXCEPT SELECT DISTINCT(bot_name) AS name FROM requests_for_permissions) AND redirect_of IS NULL"
    RIGHTS_OF_BOTS_WITH_BOT_FLAG_QUERY = "SELECT name, rights FROM bots WHERE has_botflag = 1 AND groups NOT LIKE '%bot%' AND redirect_of IS NULL"
    RIGHTS_OF_BOTS_IN_GROUP_BOT = "SELECT name, rights FROM bots WHERE has_botflag = 0 AND groups LIKE '%bot%' AND redirect_of IS NULL"

    GROUPS_OF_BOTS_WITH_REQUEST_QUERY = "SELECT DISTINCT bot_name, groups, bot_has_red_link FROM requests_for_permissions INNER JOIN bots ON bots.name = requests_for_permissions.bot_name WHERE redirect_of IS NULL"
    GROUPS_OF_BOTS_WITHOUT_REQUEST_QUERY = "SELECT name, groups FROM bots WHERE name IN (SELECT name FROM bots EXCEPT SELECT DISTINCT(bot_name) AS name FROM requests_for_permissions) AND redirect_of IS NULL"

    REQUEST_WITHOUT_CLOSED_AT = "SELECT url FROM requests_for_permissions WHERE closed_at = '' OR closed_at IS NULL"
    REQUEST_WITHOUT_EDITOR_COUNT = "SELECT url FROM requests_for_permissions WHERE editor_count IS NULL"

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

        cls.plot(time_series, ['date', 'count'])

    @classmethod
    def plot_distribution(cls, sql):

        min_value = cls.get_min_value(sql + ''' ORDER BY editor_count''')
        max_value = cls.get_max_value(sql + ''' ORDER BY editor_count''')

        distribution = {}
        for i in range(min_value, max_value + 1):
            distribution[i] = 0

        result = db.execute(sql)

        for item in result:
            distribution[item[0]] = item[1]

        cls.plot(distribution, ['editor_count', 'count'])

    @classmethod
    def get_min_value(cls, sql):
        result = db.execute(sql + cls.SQL_MIN)

        for item in result:
            return item[0]

    @classmethod
    def get_max_value(cls, sql):

        result = db.execute(sql + cls.SQL_MAX)

        for item in result:
            return item[0]

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
        result = db.execute(sql)

        bots = []
        for item in result:
            bots.append(item[0])

        return bots, len(bots)

    @classmethod
    def print_unique_bots(cls):
        result = db.execute(cls.UNIQUE_BOTS_QUERY)

        bots = []
        for item in result:
            bots.append(item[0])
        bots = set(bots)

        print("#################### Number of all unique bots: ####################\n", len(bots), "\n")
        print("#################### Names of all unique bots: ####################\n", ', '.join(list(bots)), "\n")

    @classmethod
    def print_bots_with_request(cls):

        result = db.execute(cls.BOTS_WITH_REQUEST_QUERY)

        bots = []
        for item in result:
            bots.append(item[0])
        bots = set(bots)

        print("#################### Number of all unique bots with a request for permission: ####################\n", len(bots), "\n")
        print("#################### Names of all unique bots with a request for permission: ####################\n", ', '.join(list(bots)), "\n")

    @classmethod
    def print_bots_without_request(cls):

        result = db.execute(cls.BOTS_WITHOUT_REQUEST_QUERY)

        bots = []
        for item in result:
            bots.append(item[0])
        bots = set(bots)

        print("#################### Number of all unique bots without a request for permission: ####################\n", len(bots), "\n")
        print("#################### Names of all unique bots without a request for permission: ####################\n", ', '.join(list(bots)), "\n")

    @classmethod
    def print_rights_of_bots_with_request(cls):
        result = db.execute(cls.RIGHTS_OF_BOTS_WITH_REQUEST_QUERY)

        rights_dict = {'rights': []}
        for item in result:
            if item[1] is not None:
                rights_dict['rights'] += item[1].split(',')

        df = pd.DataFrame(rights_dict)
        df = df.groupby(['rights']).size().reset_index(name='counts')
        df = df.sort_values(by=['counts', 'rights'], ascending=[False, True])

        print('|{:^30}|{:^30}|'.format('rights', 'counts'))
        print('|{:_^30}|{:_^30}|'.format('', ''))
        for index, row in df.iterrows():
            print('|{:^30}|{:^30}|'.format(row['rights'], row['counts']))

    @classmethod
    def print_bots_with_request_without_rights(cls):
        result = db.execute(cls.RIGHTS_OF_BOTS_WITH_REQUEST_QUERY)

        bots_with_red_link = []
        # bots_with_right_and_redlink = []
        bots_without_red_link = []
        for item in result:
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

        print("#################### Number of all bots with a request, without rights and a red link: ####################\n",
              len(bots_with_red_link), "\n")
        print("#################### Names of all bots with a request, without rights and a red link: ####################\n",
              ', '.join(bots_with_red_link), "\n")
        print("#################### Number of all bots with a request, without rights and without a red link: ####################\n",
              len(bots_without_red_link), "\n")
        print("#################### Names of all bots with a request, without rights and without a red link: ####################\n",
              ', '.join(bots_without_red_link), "\n")

    @classmethod
    def print_rights_of_bots_without_request(cls):
        result = db.execute(cls.RIGHTS_OF_BOTS_WITHOUT_REQUEST_QUERY)

        rights_dict = {'rights': []}
        for item in result:
            if item[1] is not None:
                rights_dict['rights'] += item[1].split(',')

        df = pd.DataFrame(rights_dict)
        df = df.groupby(['rights']).size().reset_index(name='counts')
        df = df.sort_values(by=['counts', 'rights'], ascending=[False, True])

        print('|{:^30}|{:^30}|'.format('rights', 'counts'))
        print('|{:_^30}|{:_^30}|'.format('', ''))
        for index, row in df.iterrows():
            print('|{:^30}|{:^30}|'.format(row['rights'], row['counts']))

    @classmethod
    def print_bots_without_request_without_rights(cls):
        result = db.execute(cls.RIGHTS_OF_BOTS_WITHOUT_REQUEST_QUERY)

        bots = []
        for item in result:
            if item[1] is None:
                bots.append(item[0])

        print(
            "#################### Number of all bots without a request and without rights: ####################\n",
            len(bots), "\n")
        print(
            "#################### Names of all bots without a request and without rights: ####################\n",
            ', '.join(bots), "\n")

    @classmethod
    def print_right_differences_for_request(cls):
        result = db.execute(cls.RIGHTS_OF_BOTS_WITH_REQUEST_QUERY)

        with_request_rights = []

        for item in result:
            if item[1] is not None:
                with_request_rights += item[1].split(',')

        with_request_rights = set(with_request_rights)

        result = db.execute(cls.RIGHTS_OF_BOTS_WITHOUT_REQUEST_QUERY)

        without_request_rights = []

        for item in result:
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
        result = db.execute(cls.GROUPS_OF_BOTS_WITH_REQUEST_QUERY)

        groups_dict = {'groups': []}
        for item in result:
            if item[1] is not None:
                groups_dict['groups'] += item[1].split(',')

        df = pd.DataFrame(groups_dict)
        df = df.groupby(['groups']).size().reset_index(name='counts')
        df = df.sort_values(by=['counts', 'groups'], ascending=[False, True])

        print('|{:^30}|{:^30}|'.format('groups', 'counts'))
        print('|{:_^30}|{:_^30}|'.format('', ''))
        for index, row in df.iterrows():
            print('|{:^30}|{:^30}|'.format(row['groups'], row['counts']))

    @classmethod
    def print_bots_with_request_without_groups(cls):
        result = db.execute(cls.GROUPS_OF_BOTS_WITH_REQUEST_QUERY)

        bots_with_red_link = []
        bots_without_red_link = []
        for item in result:
            if item[1] is None:
                if item[2] == 1:
                    bots_with_red_link.append(item[0])
                else:
                    bots_without_red_link.append(item[0])

        print(
            "#################### Number of all bots with a request, without groups and a red link: ####################\n",
            len(bots_with_red_link), "\n")
        print(
            "#################### Names of all bots with a request, without groups and a red link: ####################\n",
            ', '.join(bots_with_red_link), "\n")
        print(
            "#################### Number of all bots with a request, without groups and without a red link: ####################\n",
            len(bots_without_red_link), "\n")
        print(
            "#################### Names of all bots with a request, without groups and without a red link: ####################\n",
            ', '.join(bots_without_red_link), "\n")

    @classmethod
    def print_groups_of_bots_without_request(cls):
        result = db.execute(cls.GROUPS_OF_BOTS_WITHOUT_REQUEST_QUERY)

        groups_dict = {'groups': []}
        for item in result:
            if item[1] is not None:
                groups_dict['groups'] += item[1].split(',')

        df = pd.DataFrame(groups_dict)
        df = df.groupby(['groups']).size().reset_index(name='counts')
        df = df.sort_values(by=['counts', 'groups'], ascending=[False, True])

        print('|{:^30}|{:^30}|'.format('groups', 'counts'))
        print('|{:_^30}|{:_^30}|'.format('', ''))
        for index, row in df.iterrows():
            print('|{:^30}|{:^30}|'.format(row['groups'], row['counts']))

    @classmethod
    def print_bots_without_request_without_groups(cls):
        result = db.execute(cls.GROUPS_OF_BOTS_WITHOUT_REQUEST_QUERY)

        bots = []
        for item in result:
            if item[1] is None:
                bots.append(item[0])

        print(
            "#################### Number of all bots without a request and without groups: ####################\n",
            len(bots), "\n")
        print(
            "#################### Names of all bots without a request and without groups: ####################\n",
            ', '.join(bots), "\n")

    @classmethod
    def print_groups_differences(cls):
        result = db.execute(cls.GROUPS_OF_BOTS_WITH_REQUEST_QUERY)

        with_request_groups = []

        for item in result:
            if item[1] is not None:
                with_request_groups += item[1].split(',')

        with_request_groups = set(with_request_groups)

        result = db.execute(cls.GROUPS_OF_BOTS_WITHOUT_REQUEST_QUERY)

        without_request_groups = []

        for item in result:
            if item[0] is not None:
                without_request_groups += item[0].split(',')

        without_request_groups = set(without_request_groups)
        print(
            "#################### All groups that bots with a request for permission belong to but all other bots do not: ####################\n",
            ', '.join(with_request_groups.difference(without_request_groups)), "\n")
        print(
            "#################### All groups that bots without a request for permission belong to but all other bots do not: ####################\n",
            ', '.join(without_request_groups.difference(with_request_groups)), "\n")

    @classmethod
    def print_bots_with_bot_flag(cls):

        result = db.execute(cls.BOTS_WITH_BOT_FLAG_NOT_IN_BOT_GROUP)

        bots = []
        for item in result:
            bots.append(item[0])
        bots = set(bots)

        print("#################### Number of all unique bots with a bot flag: ####################\n",
              len(bots), "\n")
        print("#################### Names of all unique bots with a bot flag: ####################\n",
              ', '.join(list(bots)), "\n")

    @classmethod
    def print_bots_in_bot_group(cls):

        result = db.execute(cls.BOTS_WITHOUT_BOT_FLAG_IN_BOT_GROUP)

        bots = []
        for item in result:
            bots.append(item[0])
        bots = set(bots)

        print("#################### Number of all unique bots which belong to the group bot: ####################\n",
              len(bots), "\n")
        print("#################### Names of all unique bots which belong to the group bot: ####################\n",
              ', '.join(list(bots)), "\n")

    @classmethod
    def print_bots_with_bot_flag_and_in_bot_group(cls):

        result = db.execute(cls.BOTS_WITH_BOT_FLAG_AND_IN_BOT_GROUP)

        bots = []
        for item in result:
            bots.append(item[0])

        bots = set(bots)

        print("#################### Number of all unique bots with a bot flag and which belong to the group bot: ####################\n",
              len(bots), "\n")
        print("#################### Names of all unique bots with a bot flag and which belong to the group bot: ####################\n",
              ', '.join(list(bots)), "\n")

    @classmethod
    def print_rights_of_bot_with_bot_flag(cls):
        result = db.execute(cls.RIGHTS_OF_BOTS_WITH_BOT_FLAG_QUERY)

        rights_dict = {'rights': []}
        for item in result:
            if item[1] is not None:
                rights_dict['rights'] += item[1].split(',')

        df = pd.DataFrame(rights_dict)
        df = df.groupby(['rights']).size().reset_index(name='counts')
        df = df.sort_values(by=['counts', 'rights'], ascending=[False, True])

        print('|{:^30}|{:^30}|'.format('rights', 'counts'))
        print('|{:_^30}|{:_^30}|'.format('', ''))
        for index, row in df.iterrows():
            print('|{:^30}|{:^30}|'.format(row['rights'], row['counts']))

    @classmethod
    def print_rights_of_bot_in_bot_group(cls):
        result = db.execute(cls.RIGHTS_OF_BOTS_IN_GROUP_BOT)

        rights_dict = {'rights': []}
        for item in result:
            if item[1] is not None:
                rights_dict['rights'] += item[1].split(',')

        df = pd.DataFrame(rights_dict)
        df = df.groupby(['rights']).size().reset_index(name='counts')
        df = df.sort_values(by=['counts', 'rights'], ascending=[False, True])

        print('|{:^30}|{:^30}|'.format('rights', 'counts'))
        print('|{:_^30}|{:_^30}|'.format('', ''))
        for index, row in df.iterrows():
            print('|{:^30}|{:^30}|'.format(row['rights'], row['counts']))

    @classmethod
    def print_right_differences_for_bot_flag_and_bot_group(cls):
        result = db.execute(cls.RIGHTS_OF_BOTS_WITH_BOT_FLAG_QUERY)

        with_bot_flag_rights = []

        for item in result:
            if item[1] is not None:
                with_bot_flag_rights += item[1].split(',')

        with_bot_flag_rights = set(with_bot_flag_rights)

        result = db.execute(cls.RIGHTS_OF_BOTS_IN_GROUP_BOT)

        in_bot_group_rights = []

        for item in result:
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

        result = db.execute(cls.REQUEST_WITHOUT_CLOSED_AT)

        requests = []
        for item in result:
            requests.append(item[0])

        print(
            "#################### Number of request for permission without closed_at: ####################\n",
            len(requests), "\n")
        print(
            "#################### Request for permission without closed_at: ####################\n",
            "\n".join(requests), "\n")

    @classmethod
    def print_request_for_permission_without_editor_count(cls):

        result = db.execute(cls.REQUEST_WITHOUT_EDITOR_COUNT)

        requests = []
        for item in result:
            requests.append(item[0])

        print(
            "#################### Number of request for permission without editor_count: ####################\n",
            len(requests), "\n")
        print(
            "#################### Request for permission without editor_count: ####################\n",
            "\n".join(requests), "\n")

    @classmethod
    def plot_general_statistics_about_requests(cls):

        request_stats = {}

        result = db.execute('SELECT COUNT(url) FROM requests_for_permissions')

        for item in result:
            request_stats['all'] = item[0]

        result = db.execute('SELECT COUNT(url) FROM requests_for_permissions WHERE is_successful = 1')

        for item in result:
            request_stats['successful'] = item[0]

        result = db.execute('SELECT COUNT(url) FROM requests_for_permissions WHERE is_successful = 0')

        for item in result:
            request_stats['unsuccessful'] = item[0]

        bot_stats = {}

        result = db.execute('SELECT COUNT (DISTINCT bot_name) FROM requests_for_permissions')

        for item in result:
            bot_stats['all'] = item[0]

        result = db.execute('SELECT COUNT (DISTINCT bot_name) FROM requests_for_permissions WHERE is_successful = 1')

        for item in result:
            bot_stats['successful'] = item[0]

        result = db.execute('SELECT COUNT (DISTINCT bot_name) FROM requests_for_permissions WHERE is_successful = 0')

        for item in result:
            bot_stats['unsuccessful'] = item[0]

        trace0 = Bar(
            y=['all', 'successful', 'unsuccessful'],
            x=list(request_stats.values()),
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
            y=['all', 'successful', 'unsuccessful'],
            x=list(bot_stats.values()),
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
        result = db.execute('SELECT userid, name, editcount, registration FROM bots WHERE editcount NOT NULL')

        edit_count_dict = {'userid': [], 'bots': [], 'edit_count': [], 'registration': []}

        for item in result:
            edit_count_dict['userid'].append(item[0])
            edit_count_dict['bots'].append(item[1])
            edit_count_dict['edit_count'].append(item[2])
            edit_count_dict['registration'].append(str(datetime.strptime(item[3], '%Y-%m-%dT%H:%M:%SZ').date()))

        df = pd.DataFrame(edit_count_dict)
        df = df.sort_values(by=['edit_count', 'bots'])

        print('|{:^25}|{:^25}|{:^25}|{:^25}|'.format('userid', 'bots', 'edit_count', 'registration'))
        print('|{:_^25}|{:_^25}|{:_^25}|{:_^25}|'.format('', '', '', ''))
        for index, row in df.iterrows():
            print('|{:^25}|{:^25}|{:^25}|{:^25}|'.format(row['userid'], row['bots'], row['edit_count'], row['registration']))


    @classmethod
    def print_average_edit_count_per_day(cls):
        result = db.execute('SELECT userid, name, editcount, registration FROM bots WHERE editcount NOT NULL AND registration NOT NULL')

        average_edit_count_dict = {'userid': [], 'bots': [], 'average_edit_count_per_day': [], 'registration': []}

        for item in result:
            average_edit_count_dict['userid'].append(item[0])
            average_edit_count_dict['bots'].append(item[1])

            registration_date = datetime.strptime(item[3], '%Y-%m-%dT%H:%M:%SZ')
            current_date = datetime.now()
            days_since_registration = (current_date - registration_date).days
            average_edit_count_per_day = int(item[2] / days_since_registration)

            average_edit_count_dict['average_edit_count_per_day'].append(average_edit_count_per_day)
            average_edit_count_dict['registration'].append(str(registration_date.date()))

        df = pd.DataFrame(average_edit_count_dict)
        df = df.sort_values(by=['average_edit_count_per_day', 'bots'])

        print('|{:^25}|{:^25}|{:^25}|{:^25}|'.format('userid', 'bots', 'avg_edit_count_per_day', 'registration'))
        print('|{:_^25}|{:_^25}|{:_^25}|{:_^25}|'.format('', '', '', ''))
        for index, row in df.iterrows():
            print('|{:^25}|{:^25}|{:^25}|{:^25}|'.format(row['userid'], row['bots'], row['average_edit_count_per_day'], row['registration']))

    @classmethod
    def print_editor_count(cls, mode=None):

        sql = 'SELECT url, editor_count FROM requests_for_permissions WHERE editor_count NOT NULL'

        if mode == 'successful':
            sql += ' AND is_successful = 1'
        elif mode == 'unsuccessful':
            sql += ' AND is_successful = 0'

        result = db.execute(sql)

        editor_count_dict = {'url': [], 'editor_count': []}

        for item in result:
            editor_count_dict['url'].append(item[0])
            editor_count_dict['editor_count'].append(item[1])

        df = pd.DataFrame(editor_count_dict)
        df = df.sort_values(by=['editor_count', 'url'])

        print('|{:^90}|{:^15}|'.format('url', 'editor_count'))
        print('|{:_^90}|{:_^15}|'.format('', ''))
        for index, row in df.iterrows():
            print('|{:^90}|{:^15}|'.format(row['url'], row['editor_count']))

    @classmethod
    def plot_bots_group_destribution(cls):

        result = db.execute('SELECT groups, COUNT(*) FROM bots WHERE groups NOT NULL GROUP BY groups')

        data = {'groups': [], 'count': []}

        for item in result:
            data['groups'].append(item[0])
            data['count'].append(item[1])

        top_labels = data['groups']

        colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
                  'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
                  'rgba(190, 192, 213, 1)', 'rgba(38, 24, 74, 0.8)',
                  'rgba(71, 58, 131, 0.8)',
                  'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)',
                  'rgba(190, 192, 213, 1)', 'rgba(190, 192, 213, 1)']

        x_data = [data['count']]

        y_data = ['groups']

        traces = []

        for i in range(0, len(x_data[0])):
            #print(i)
            for xd, yd in zip(x_data, y_data):
                #print(xd)
                traces.append(Bar(
                    x=[xd[i]],
                    y=[yd],
                    orientation='h',
                    marker=dict(
                        color=colors[i],
                        line=dict(
                            color='rgb(248, 248, 249)',
                            width=1)
                    )
                ))

        layout = Layout(
            xaxis=dict(
                showgrid=False,
                showline=False,
                showticklabels=False,
                zeroline=False,
                domain=[0.15, 1]
            ),
            yaxis=dict(
                showgrid=False,
                showline=False,
                showticklabels=False,
                zeroline=False,
            ),
            barmode='stack',
            paper_bgcolor='rgb(225, 225, 225)',
            plot_bgcolor='rgb(225, 225, 225)',
            margin=dict(
                l=120,
                r=10,
                t=140,
                b=80
            ),
            showlegend=False,
        )

        annotations = []

        for yd, xd in zip(y_data, x_data):
            # labeling the y-axis
            annotations.append(dict(xref='paper', yref='y',
                                    x=0.14, y=yd,
                                    xanchor='right',
                                    text=str(yd),
                                    font=dict(family='Arial', size=14,
                                              color='rgb(67, 67, 67)'),
                                    showarrow=False, align='right'))
            # labeling the first percentage of each bar (x_axis)
            annotations.append(dict(xref='x', yref='y',
                                    x=int(xd[0]) / 474, y=yd,
                                    text=str(xd[0]) + '%',
                                    font=dict(family='Arial', size=14,
                                              color='rgb(248, 248, 255)'),
                                    showarrow=False))
            # labeling the first Likert scale (on the top)
            if yd == y_data[-1]:
                annotations.append(dict(xref='x', yref='paper',
                                        x=int(xd[0]) / 474, y=1.1,
                                        text=top_labels[0],
                                        font=dict(family='Arial', size=14,
                                                  color='rgb(67, 67, 67)'),
                                        showarrow=False))
            space = xd[0]
            for i in range(1, len(xd)):
                # labeling the rest of percentages for each bar (x_axis)
                annotations.append(dict(xref='x', yref='y',
                                        x=space + (int(xd[i]) / 474), y=yd,
                                        text=str(xd[i]) + '%',
                                        font=dict(family='Arial', size=14,
                                                  color='rgb(248, 248, 255)'),
                                        showarrow=False))
                # labeling the Likert scale
                if yd == y_data[-1]:
                    annotations.append(dict(xref='x', yref='paper',
                                            x=space + (xd[i] / 474), y=1.1,
                                            text=top_labels[i],
                                            font=dict(family='Arial', size=14,
                                                      color='rgb(67, 67, 67)'),
                                            showarrow=False))
                space += xd[i]

        layout['annotations'] = annotations

        fig = Figure(data=traces, layout=layout)
        iplot(fig, filename='bar-colorscale')
