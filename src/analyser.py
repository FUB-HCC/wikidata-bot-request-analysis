import csv


class Analyser(object):

    files = [
        'data/parser/users_in_bot_group.csv',
        'data/spiders/bots_with_requests_for_permissions.csv',
        'data/spiders/bots_without_botflag.csv',
        'data/spiders/extension_bots.csv',
        'data/spiders/bots_with_botflag.csv',
    ]

    @classmethod
    def count_bots_in_files(cls):

        for file in cls.files:
            with open(file) as f:
                reader = csv.reader(f)
                for row in reader:
                    print('%s: %s' %(file, len(row)))