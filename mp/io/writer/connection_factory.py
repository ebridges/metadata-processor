class ConnectionFactory:
    def __init__(self, dbinfo):
        self.dbinfo = dbinfo

    @staticmethod
    def instance(db):
        dbtype = db['dbtype']
        if dbtype == 'sqlite':
            return SqliteConnectionFactory(db)
        if dbtype == 'postgres':
            return PostgresqlConnectionFactory(db)
        else:
            raise Exception(f'unsupported db type: {dbtype}')

    def connect(self):
        pass


class SqliteConnectionFactory(ConnectionFactory):
    def connect(self):
        pass


class PostgresqlConnectionFactory(ConnectionFactory):
    def connect(self):
        pass
