from sys import stdout
from logging import debug, warning

from mp.io.writer.formatter import csv_formatter

from mp.io.writer.exception_sql import insert


class ExceptionEventWriter(object):  # pragma: no cover
    def write(self, event):
        pass


class StdoutExceptionEventWriter(ExceptionEventWriter):
    def __init__(self, output=stdout, formatter=csv_formatter):
        if output:
            self.output = output
            self.formatter = formatter

    def __enter__(self):  # pragma: no cover
        debug('StdoutExceptionEventWriter: entering context')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # pragma: no cover
        debug('StdoutExceptionEventWriter: exiting context')
        self.output.flush()

    def write(self, metadata):
        self.output.write(self.formatter(metadata))
        self.output.flush()
        return None


class DatabaseExceptionEventWriter(ExceptionEventWriter):  # pragma: no cover
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

    def write(self, event):
        debug(f'writing event {event}')
        return self.insert(event)

    def insert(self, event):
        return self._exec(insert(self.type), event)

    def _exec(self, statement, params):
        debug(f'executing [{statement}] with [{params}]')
        self.cursor.execute(statement, params)
        r = self.cursor.fetchone()
        debug(f'statement exec returned: {r}')
        return r[0] if r and len(r) > 0 else None
