from pytest import raises
from mp.io.writer.connection_factory import (
    ConnectionFactory,
    SqliteConnectionFactory,
    PostgresqlConnectionFactory,
)


def test_instanceof_sqlite():
    db = {'dbtype': 'sqlite', 'url': 'foobar'}
    under_test = ConnectionFactory.instance(db)
    assert isinstance(under_test, SqliteConnectionFactory)
    assert under_test.dbinfo == db
    assert under_test.connect() is None


def test_instanceof_postgres():
    db = {'dbtype': 'postgres', 'url': 'foobar'}
    under_test = ConnectionFactory.instance(db)
    assert isinstance(under_test, PostgresqlConnectionFactory)
    assert under_test.dbinfo == db
    assert under_test.connect() is None


def test_instanceof_unknown():
    with raises(Exception):
        db = {'dbtype': 'junk', 'url': 'foobar'}
        under_test = ConnectionFactory.instance(db)
