import sqlite3
import os
from os.path import isfile, join


class SqliteDb(object):

    DB_FILE = '../db/wikidata_bot_requests_for_permissions.db'
    DB_SCHEMA_FILE = 'db/schema.ddl'
    DB_MIGRATIONS_DIR = 'db/migrations/'

    @classmethod
    def connect(cls):
        return sqlite3.connect(cls.DB_FILE)

    @classmethod
    def init(cls):
        conn = cls.connect()
        cursor = conn.cursor()

        with open(cls.DB_SCHEMA_FILE, 'r') as file:
            cursor.executescript(file.read())

        cls.migrate()

        conn.commit()
        conn.close()

    @classmethod
    def execute(cls, sql):
        conn = cls.connect()
        cursor = conn.cursor()

        return cursor.execute(sql)

    @classmethod
    def reset(cls):
        os.remove(cls.DB_FILE)
        cls.init()

    @classmethod
    def migrate(cls):
        conn = cls.connect()
        cursor = conn.cursor()

        files = [
            join(cls.DB_MIGRATIONS_DIR, f) for f in os.listdir(cls.DB_MIGRATIONS_DIR)
            if isfile(join(cls.DB_MIGRATIONS_DIR, f))
        ]

        for file in files:
            with open(file, 'r') as f:
                cursor.executescript(f.read())

        conn.commit()
        conn.close()

    @classmethod
    def insert(cls, table, data):
        conn = cls.connect()
        cursor = conn.cursor()

        data = {k: v for k, v in data.items() if v is not None}

        columns = ','.join(data.keys())
        values = tuple(data.values())
        placeholders = ','.join(['?' for _ in range(len(data.keys()))])

        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, columns, placeholders)

        cursor.execute(sql, values)
        conn.commit()

        conn.close()

    @classmethod
    def bulk_insert(cls, table, data):
        conn = cls.connect()
        cursor = conn.cursor()

        values = []
        columns = ','.join(data[0].keys()) if len(data) > 0 else ''
        placeholders = ','.join(['?' for _ in range(len(data[0].keys()))]) if len(data) > 0 else ''

        for instance in data:
            values.append(tuple(instance.values()))

        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, columns, placeholders)

        cursor.execute(sql, values)
        conn.commit()

        conn.close()

    @classmethod
    def find(cls, selector_column_name, from_table_name, where_column_name, where_value):
        conn = cls.connect()
        cursor = conn.cursor()

        sql = "SELECT %s FROM %s WHERE %s = (?)" % (selector_column_name, from_table_name, where_column_name)

        result = [row for row in cursor.execute(sql, (str(where_value),))]

        conn.commit()
        conn.close()

        return result

    @classmethod
    def exists(cls, from_table_name, where_column_name, where_value):
        return len(cls.find('*', from_table_name, where_column_name, where_value)) > 0

    @classmethod
    def drop(cls, table_name):
        conn = cls.connect()
        cursor = conn.cursor()

        sql = "DROP TABLE IF EXISTS %s" % table_name

        cursor.execute(sql)

        conn.commit()
        conn.close()

    @classmethod
    def create(cls, table_name):

        conn = cls.connect()
        cursor = conn.cursor()

        with open("db/%s.ddl" % table_name, 'r') as file:
            cursor.executescript(file.read())

        conn.commit()
        conn.close()