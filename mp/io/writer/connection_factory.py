class ConnectionFactory:
    @staticmethod
    def instance(db):
        dbtype = db['dbtype']
        if dbtype == 'sqlite':
            return SqliteConnectionFactory(db['url'])
        if dbtype == 'postgres':
            return PostgresqlConnectionFactory(db['url'])
        else:
            raise Exception(f'unsupported db type: {dbtype}')

    def connect(self):
        pass


class SqliteConnectionFactory(ConnectionFactory):
    def __init__(self):
        pass

    def connect(self):
        pass


class PostgresqlConnectionFactory(ConnectionFactory):
    def __init__(self):
        pass

    def connect(self):
        pass
