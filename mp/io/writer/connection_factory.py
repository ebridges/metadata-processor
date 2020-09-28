from logging import info, debug
from os import makedirs
from pathlib import Path

import psycopg2
import duckdb

from mp.io.writer import DUCKDB, POSTGRESQL
from mp.io.writer.metadata_sql import create as create_metadata_table


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


class DuckdbConnectionFactory(ConnectionFactory):
    def connect(self):
        dbname = self.dbinfo.get('dbname')
        if dbname and '/' in dbname:  # pragma: no cover
            data_path = Path(dbname).parent
            info(f'Creating parent folders for db file: {data_path}')
            makedirs(data_path, exist_ok=True)

        self.connection = duckdb.connect(self.dbinfo['dbname'])

        debug('Creating table if it does not exist')
        c = self.connection.cursor()
        c.execute(create_metadata_table())

        return self.connection


class PostgresqlConnectionFactory(ConnectionFactory):
    def connect(self):
        self.connection = psycopg2.connect(
            host=self.dbinfo.get('hostname'),
            port=self.dbinfo.get('port'),
            user=self.dbinfo.get('username'),
            password=self.dbinfo.get('password'),
            database=self.dbinfo.get('dbname'),
        )
        return self.connection


SUPPORTED_DBS = {
    POSTGRESQL: PostgresqlConnectionFactory,
    DUCKDB: DuckdbConnectionFactory,
}
