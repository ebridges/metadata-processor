from io import StringIO
from uuid import uuid4

from unittest.mock import patch
from pytest import raises

from mp.io.writer import POSTGRESQL, DUCKDB
from mp.io.writer.exception_writer import (
    StdoutExceptionEventWriter,
    DatabaseExceptionEventWriter,
)

from tests.mp.io.writer.mock_connection_factory import MockConnectionFactory
from tests.mp.io.writer.mock_exception_writer import MockDatabaseExceptionEventWriter


def test_stdout_exceptionwriter():
    mock_data = {'AAA': 'aaa', 'BBB': 'bbb', 'CCC': 'ccc'}
    expected = 'AAA,BBB,CCC\naaa,bbb,ccc\n'
    with patch('sys.stdout', new=StringIO()) as mock_stdout:
        under_test = StdoutExceptionEventWriter(output=mock_stdout)
        under_test.write(mock_data)
        actual = mock_stdout.getvalue()
        assert expected == actual
        assert mock_stdout == under_test.output


def test_db_exceptionwriter_init_duckdb():
    connection_factory = MockConnectionFactory.instance(
        db={'dbtype': DUCKDB, 'url': 'foobar'}
    )
    under_test = DatabaseExceptionEventWriter(connection_factory)
    assert under_test.connection_factory is not None
    assert under_test.type == DUCKDB


def test_db_exceptionwriter_init_random():
    connection_factory = MockConnectionFactory.instance(
        db={'dbtype': 'junk', 'url': 'foobar'}
    )
    under_test = DatabaseExceptionEventWriter(connection_factory)
    assert under_test.connection_factory is not None
    assert under_test.type == 'junk'


def test_db_exceptionwriter_write():
    expected = uuid4()
    data = {'id': expected}
    connection_factory = MockConnectionFactory.instance(
        db={'dbtype': 'junk', 'url': 'foobar'}
    )

    def mock_write(self, data):
        assert data is not None
        assert data['id'] is not None
        return data['id']

    with patch.object(DatabaseExceptionEventWriter, 'write', new=mock_write):
        with DatabaseExceptionEventWriter(connection_factory) as under_test:
            assert under_test is not None
            mock_connection = under_test.connection
            actual = under_test.write(data)
    assert mock_connection is not None
    assert mock_connection.mock_cursor is not None
    assert connection_factory.connect_count == 1
    assert mock_connection.cursor_count == 1
    assert mock_connection.close_count == 1
    assert mock_connection.mock_cursor.close_count == 1
    assert mock_connection.commit_count == 1
    assert mock_connection.rollback_count == 0
    assert expected == actual


def test_db_exceptionwriter_write_fail():
    data = {'id': uuid4()}
    connection_factory = MockConnectionFactory.instance(
        db={'dbtype': 'junk', 'url': 'foobar'}
    )

    def mock_write(self, data):
        assert data is not None
        assert data['id'] is not None
        raise Exception('error')

    with patch.object(DatabaseExceptionEventWriter, 'write', new=mock_write):
        with raises(Exception):
            with DatabaseExceptionEventWriter(connection_factory) as under_test:
                assert under_test is not None
                mock_connection = under_test.connection
                under_test.write(data)
    assert mock_connection is not None
    assert mock_connection.mock_cursor is not None
    assert connection_factory.connect_count == 1
    assert mock_connection.cursor_count == 1
    assert mock_connection.close_count == 1
    assert mock_connection.mock_cursor.close_count == 1
    assert mock_connection.commit_count == 0
    assert mock_connection.rollback_count == 1


def test_db_exceptionwriter_write_insert():
    expected = uuid4()
    data = {}
    with MockDatabaseExceptionEventWriter(insert_retval=expected) as under_test:
        actual = under_test.write(data)
    assert under_test.enter_count == 1
    assert under_test.insert_count == 1
    assert under_test.exit_count == 1
    assert actual == expected
