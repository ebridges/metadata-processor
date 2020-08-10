from sys import stdout


class MetadataWriter(object):
    def __init__(self, output):
        if output:
            self.output = output

    @staticmethod
    def instance(t):
        if t == 'stdout':
            return StdoutMetadataWriter(stdout)
        if t == 'database':
            return DatabaseMetadataWriter(t)
        else:
            return FileMetadataWriter(t)

    def write(self, metadata):
        pass


class StdoutMetadataWriter(MetadataWriter):
    def write(self, metadata):
        self.output.write(str(metadata))


class FileMetadataWriter(MetadataWriter):
    def __init__(self, filename):
        self._filename = filename

    def write(self, metadata):
        with open(self._filename, 'w') as file:
            file.write(str(metadata))
