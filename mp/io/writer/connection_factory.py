from logging import info, debug
from os import makedirs
from pathlib import Path

import sqlite3

from mp.io.writer.sql import create


class ConnectionFactory:
    def __init__(self, dbinfo):
        self.dbinfo = dbinfo

    @staticmethod
    def instance(db):
        dbtype = db['dbtype']
        info(f'Creating instance of {dbtype} connection factory.')
        if dbtype == 'sqlite':
            return SqliteConnectionFactory(db)
        if dbtype == 'postgres':
            return PostgresqlConnectionFactory(db)
        else:
            raise Exception(f'unsupported db type: {dbtype}')

    def connect(self):  # pragma: no cover
        pass


class SqliteConnectionFactory(ConnectionFactory):
    def connect(self):
        if '/' in self.dbinfo['dbname']:
            data_path = Path(self.dbinfo['dbname']).parent
            info(f'Creating parent folders for db file: {data_path}')
            makedirs(data_path, exist_ok=True)

        self.connection = sqlite3.connect(self.dbinfo['dbname'])

        debug('Creating table if it does not exist')
        c = self.connection.cursor()
        c.execute(create())

        return self.connection


class PostgresqlConnectionFactory(ConnectionFactory):
    def connect(self):
        pass
