from logging import info, debug, error
from sys import stdout

from mp.io.writer.connection_factory import ConnectionFactory


class MetadataWriter(object):  # pragma: no cover
    def write(self, metadata):
        pass


class FilehandleMetadataWriter(MetadataWriter):
    def __init__(self, output, formatter):
        if output:
            self.output = output
            self.formatter = formatter

    def __enter__(self):
        debug('FilehandleMetadataWriter: entering context')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        debug('FilehandleMetadataWriter: exiting context')
        self.output.flush()
        if not self.output == stdout:
            info('not closing output because it is stdout')
            self.output.close()
        if exc_val is not None:
            error(f'exception {exc_type} when closing file handle: {exc_val}\n{exc_tb}')

    def write(self, metadata):
        self.output.write(self.formatter(metadata))
        self.output.flush()


class DatabaseMetadataWriter(MetadataWriter):  # pragma: no cover
    def __init__(self, connection_factory):
        self.connection_factory = connection_factory

    def __enter__(self):
        cf = self.connection_factory
        self.connection = cf.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        if exc_val is not None:
            error(f'exception {exc_type} when closing db handle: {exc_val}\n{exc_tb}')

    def write(self, metadata):
        if self.exists(metadata.file_path):
            info(f'file_path {metadata.file_path} already exists in db, updating it.')
            self.update(metadata)
            return metadata.id
        else:
            info(f'inserting new file_path {metadata.file_path}.')
            id = self.insert(metadata)
            return id

    def exists(self, path):
        pass

    def insert(self, metadata):
        pass

    def update(self, metadata):
        pass

    def delete(self, image_key):
        pass
