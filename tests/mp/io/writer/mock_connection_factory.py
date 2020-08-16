from mp.io.writer.connection_factory import ConnectionFactory


class MockCursor:
    def __init__(self):
        self.close_count = 0

    def close(self):
        self.close_count = self.close_count + 1


class MockConnection:
    def __init__(self):
        self.close_count = 0
        self.cursor_count = 0
        self.commit_count = 0
        self.rollback_count = 0
        self.mock_cursor = MockCursor()

    def close(self):
        self.close_count = self.close_count + 1

    def cursor(self):
        self.cursor_count = self.cursor_count + 1
        return self.mock_cursor

    def commit(self):
        self.commit_count = self.commit_count + 1

    def rollback(self):
        self.rollback_count = self.rollback_count + 1


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
