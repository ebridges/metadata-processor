from uuid import uuid4
from mp.io.writer.metadata_writer import DatabaseMetadataWriter


class MockDatabaseMetadataWriter(DatabaseMetadataWriter):
    def __init__(
        self,
        exists_retval=True,
        insert_retval=uuid4(),
        update_retval=uuid4(),
        delete_retval=1,
        side_effects={}
    ):
        self.enter_count = 0
        self.exit_count = 0
        self.exists_count = 0
        self.exists_retval = exists_retval
        self.insert_count = 0
        self.insert_retval = insert_retval
        self.update_count = 0
        self.update_retval = update_retval
        self.delete_count = 0
        self.delete_retval = delete_retval
        self.side_effects = side_effects

    def __enter__(self):
        self.enter_count = self.enter_count + 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_count = self.exit_count + 1

    def exists(self, path):
        self.exists_count = self.exists_count + 1
        if 'exists' in self.side_effects:
            raise self.side_effects['exists']
        return self.exists_retval

    def insert(self, metadata):
        self.insert_count = self.insert_count + 1
        if 'insert' in self.side_effects:
            raise self.side_effects['insert']
        return self.insert_retval

    def update(self, metadata):
        self.update_count = self.update_count + 1
        if 'update' in self.side_effects:
            raise self.side_effects['update']
        return self.update_retval

    def delete(self, image_key):
        self.delete_count = self.delete_count + 1
        if 'delete' in self.side_effects:
            raise self.side_effects['delete']
        return self.delete_retval
