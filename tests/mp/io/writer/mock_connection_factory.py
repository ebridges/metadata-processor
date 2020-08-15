from mp.io.writer.connection_factory import ConnectionFactory


class MockConnection:
    def __init__(self):
        self.close_count = 0

    def close(self):
        self.close_count = self.close_count + 1


class MockConnectionFactory(ConnectionFactory):
    def __init__(self, dbinfo):
        ConnectionFactory.__init__(self, dbinfo)
        self.connect_count = 0

    @staticmethod
    def instance(db):
        return MockConnectionFactory(db)

    def connect(self):
        self.connect_count = self.connect_count + 1
        return MockConnection()
