from sys import platform
from pytest import raises, mark
from mp.io.writer.connection_factory import (
    ConnectionFactory,
    SqliteConnectionFactory,
    PostgresqlConnectionFactory,
)
from mp.io.writer.sql import POSTGRESQL, SQLITE


def test_instanceof_sqlite():
    db = {'dbtype': SQLITE, 'url': 'foobar', 'dbname': 'junkdb'}
    under_test = ConnectionFactory.instance(db)
    assert isinstance(under_test, SqliteConnectionFactory)
    assert under_test.dbinfo == db
    assert under_test.connect() is not None


@mark.skipif(
    'linux' in platform, reason='Skip running on CI where PG is not installed.'
)
def test_instanceof_postgres():
    db = {'dbtype': POSTGRESQL, 'url': f'{POSTGRESQL}:postgres', 'dbname': 'postgres'}
    under_test = ConnectionFactory.instance(db)
    assert isinstance(under_test, PostgresqlConnectionFactory)
    assert under_test.dbinfo == db
    assert under_test.connect() is not None


def test_instanceof_unknown():
    with raises(Exception):
        db = {'dbtype': 'junk', 'url': 'foobar'}
        under_test = ConnectionFactory.instance(db)
