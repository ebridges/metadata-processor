from sys import stdout


class MetadataWriter(object):
    def __init__(self, output, formatter):
        if output:
            self.output = output
            self.formatter = formatter

    @staticmethod
    def instance(t, f):
        if t == 'stdout':
            return StdoutMetadataWriter(stdout, f)
        if t == 'database':
            return DatabaseMetadataWriter(t, f)
        else:
            return FileMetadataWriter(t, f)

    def write(self, metadata):
        pass


class StdoutMetadataWriter(MetadataWriter):
    def write(self, metadata):
        self.output.write(self.formatter(metadata))


class FileMetadataWriter(MetadataWriter):
    def write(self, metadata):
        with open(self.output, 'w') as file:
            file.write(self.formatter(metadata))
