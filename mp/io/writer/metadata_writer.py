from logging import info, debug, warning
from sys import stdout

from mp.io.writer.connection_factory import ConnectionFactory
from mp.io.writer.sql import insert, exists, update, delete
from mp.model import FILE_PATH, IMAGE_ID


class MetadataWriter(object):  # pragma: no cover
    def write(self, metadata):
        pass


class FilehandleMetadataWriter(MetadataWriter):
    def __init__(self, output, formatter):
        if output:
            self.output = output
            self.formatter = formatter

    def __enter__(self):  # pragma: no cover
        debug('FilehandleMetadataWriter: entering context')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # pragma: no cover
        debug('FilehandleMetadataWriter: exiting context')
        self.output.flush()
        if not self.output == stdout:
            self.output.close()

    def write(self, metadata):
        self.output.write(self.formatter(metadata))
        self.output.flush()
        return None


class DatabaseMetadataWriter(MetadataWriter):  # pragma: no cover
    def __init__(self, connection_factory):
        self.connection_factory = connection_factory
        self.type = self.connection_factory.dbinfo['dbtype']

    def __enter__(self):
        cf = self.connection_factory
        self.connection = cf.connect()
        self.cursor = self.connection.cursor()
        debug('Database cursor connected.')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        if exc_val is not None:
            warning(f'exception {exc_type} when closing db handle: {exc_val}')
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
        debug('Database connection closed.')

    def write(self, metadata):
        if self.exists(metadata.file_path):
            info(f'file_path {metadata.file_path} already exists in db, updating it.')
            return self.update(metadata)
        else:
            info(f'inserting new file_path {metadata.file_path}.')
            return self.insert(metadata)

    def exists(self, path):
        debug('executing "exists"')
        r = self._exec(exists(self.type), {FILE_PATH: path})
        return True if r and r == 1 else False

    def insert(self, metadata):
        debug('executing "insert"')
        return self._exec(insert(self.type), metadata.dict())

    def update(self, metadata):
        debug('executing "update"')
        return self._exec(update(self.type), metadata.dict())

    def delete(self, image_key):
        debug('executing "delete"')
        return self._exec(delete(self.type), {IMAGE_ID: image_key.image_id()})

    def _exec(self, statement, params):
        debug(f'executing [{statement}] with [{params}]')
        self.cursor.execute(statement, params)
        r = self.cursor.fetchone()
        debug(f'statement exec returned: {r}')
        return r[0] if r and len(r) > 0 else None
