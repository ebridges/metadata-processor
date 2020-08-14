from mp.io.writer.connection_factory import ConnectionFactory


class MetadataWriter(object):
    def write(self, metadata):
        pass


class FilehandleMetadataWriter(MetadataWriter):
    def __init__(self, output, formatter):
        if output:
            self.output = output
            self.formatter = formatter

    def write(self, metadata):
        self.output.write(self.formatter(metadata))


class DatabaseMetadataWriter(MetadataWriter):  # pragma: no cover
    def __init__(self, connection_factory):
        self.connection_factory = connection_factory

    def __enter__(self):
        self.connection = self.connection_factory.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def exists(self, path):
        pass

    def write(self, metadata):
        # not yet implemented
        pass
