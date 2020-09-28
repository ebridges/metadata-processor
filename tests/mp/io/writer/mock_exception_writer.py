from uuid import uuid4

from mp.io.writer.exception_writer import DatabaseExceptionEventWriter


class MockDatabaseExceptionEventWriter(DatabaseExceptionEventWriter):
    def __init__(self, insert_retval=uuid4()):
        self.enter_count = 0
        self.exit_count = 0
        self.insert_count = 0
        self.insert_retval = insert_retval

    def __enter__(self):
        self.enter_count = self.enter_count + 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_count = self.exit_count + 1

    def insert(self, metadata):
        self.insert_count = self.insert_count + 1
        return self.insert_retval
