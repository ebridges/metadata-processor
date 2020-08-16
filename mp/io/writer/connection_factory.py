from logging import info, debug
from os import makedirs
from pathlib import Path

import sqlite3

from mp.io.writer.sql import create, POSTGRESQL, SQLITE


class ConnectionFactory:
    def __init__(self, dbinfo):
        self.dbinfo = dbinfo

    @staticmethod
    def instance(db):
        dbtype = db['dbtype']
        if dbtype not in SUPPORTED_DBS:
            raise Exception(f'unsupported db type: {dbtype}')

        info(f'Creating instance of {dbtype} connection factory.')
        factory = SUPPORTED_DBS[dbtype]
        return factory(db)

    def connect(self):  # pragma: no cover
        pass


class SqliteConnectionFactory(ConnectionFactory):
    def connect(self):
        dbname = self.dbinfo.get('dbname')
        if dbname and '/' in dbname:
            data_path = Path(dbname).parent
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


SUPPORTED_DBS = {
    POSTGRESQL: PostgresqlConnectionFactory,
    SQLITE: SqliteConnectionFactory,
}
