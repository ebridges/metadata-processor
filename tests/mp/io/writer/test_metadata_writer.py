from io import StringIO
from tempfile import NamedTemporaryFile
from uuid import uuid4

from pytest import raises
from unittest.mock import patch
from assertpy import assert_that, contents_of

from mp.io.writer.metadata_writer import (
    MetadataWriter,
    DatabaseMetadataWriter,
    FilehandleMetadataWriter,
)
from mp.io.writer import POSTGRESQL, DUCKDB
from tests.mp.io.writer.mock_metadata_formatter import mock_formatter
from tests.mp.model.mock_metadata import MockMetadata
from tests.mp.io.writer.mock_metadata_writer import MockDatabaseMetadataWriter
from tests.mp.io.writer.mock_connection_factory import MockConnectionFactory


def test_stdout_metadatawriter():
    mock_data = {'foo': 'bar'}
    mock_metadata = MockMetadata(args=mock_data)
    expected = str(mock_data)
    with patch('sys.stdout', new=StringIO()) as mock_stdout:
        under_test = FilehandleMetadataWriter(mock_stdout, mock_formatter)
        under_test.write(mock_metadata)
        actual = mock_stdout.getvalue()
        assert expected == actual
        assert mock_stdout == under_test.output
        assert mock_formatter == under_test.formatter


def test_file_metadatawriter():
    mock_data = {'foo': 'bar'}
    mock_metadata = MockMetadata(args=mock_data)
    expected_data = str(mock_data)
    with NamedTemporaryFile() as expected, NamedTemporaryFile(mode='w') as actual:
        expected.write(expected_data.encode())
        under_test = FilehandleMetadataWriter(actual.file, mock_formatter)
        under_test.write(mock_metadata)
        actual_contents = contents_of(actual.name)
        assert_that(actual_contents).contains(expected_data)
        assert actual.file == under_test.output
        assert mock_formatter == under_test.formatter


def test_db_metadatawriter_init_duckdb():
    connection_factory = MockConnectionFactory.instance(
        db={'dbtype': DUCKDB, 'url': 'foobar'}
    )
    under_test = DatabaseMetadataWriter(connection_factory)
    assert under_test.connection_factory is not None
    assert under_test.type == DUCKDB


def test_db_metadatawriter_init_random():
    connection_factory = MockConnectionFactory.instance(
        db={'dbtype': 'junk', 'url': 'foobar'}
    )
    under_test = DatabaseMetadataWriter(connection_factory)
    assert under_test.connection_factory is not None
    assert under_test.type == 'junk'


def test_db_metadatawriter_write():
    expected = uuid4()
    metadata = {'id': expected}
    connection_factory = MockConnectionFactory.instance(
        db={'dbtype': 'junk', 'url': 'foobar'}
    )

    def mock_write(self, metadata):
        assert metadata is not None
        assert metadata.id is not None
        return metadata.id

    with patch.object(DatabaseMetadataWriter, 'write', new=mock_write):
        with DatabaseMetadataWriter(connection_factory) as under_test:
            assert under_test is not None
            md = MockMetadata(args=metadata)
            mock_connection = under_test.connection
            actual = under_test.write(md)
    assert mock_connection is not None
    assert mock_connection.mock_cursor is not None
    assert connection_factory.connect_count == 1
    assert mock_connection.cursor_count == 1
    assert mock_connection.close_count == 1
    assert mock_connection.mock_cursor.close_count == 1
    assert mock_connection.commit_count == 1
    assert mock_connection.rollback_count == 0
    assert expected == actual


def test_db_metadatawriter_write_fail():
    metadata = {'id': uuid4()}
    connection_factory = MockConnectionFactory.instance(
        db={'dbtype': 'junk', 'url': 'foobar'}
    )

    def mock_write(self, metadata):
        assert metadata is not None
        assert metadata.id is not None
        raise Exception('error')

    with patch.object(DatabaseMetadataWriter, 'write', new=mock_write):
        with raises(Exception):
            with DatabaseMetadataWriter(connection_factory) as under_test:
                assert under_test is not None
                md = MockMetadata(args=metadata)
                mock_connection = under_test.connection
                under_test.write(md)
    assert mock_connection is not None
    assert mock_connection.mock_cursor is not None
    assert connection_factory.connect_count == 1
    assert mock_connection.cursor_count == 1
    assert mock_connection.close_count == 1
    assert mock_connection.mock_cursor.close_count == 1
    assert mock_connection.commit_count == 0
    assert mock_connection.rollback_count == 1


def test_db_metadatawriter_write_update():
    expected = uuid4()
    expected_path = '/foo/bar'
    metadata = {'id': expected, 'file_path': expected_path}
    with MockDatabaseMetadataWriter(update_retval=expected) as under_test:
        md = MockMetadata(args=metadata)
        actual = under_test.write(md)
    assert under_test.enter_count == 1
    assert under_test.exists_count == 1
    assert under_test.update_count == 1
    assert under_test.insert_count == 0
    assert under_test.delete_count == 0
    assert under_test.exit_count == 1
    assert actual == expected


def test_db_metadatawriter_write_insert():
    expected = uuid4()
    metadata = {}
    with MockDatabaseMetadataWriter(
        exists_retval=False, insert_retval=expected
    ) as under_test:
        md = MockMetadata(args=metadata)
        actual = under_test.write(md)
    assert under_test.enter_count == 1
    assert under_test.exists_count == 1
    assert under_test.update_count == 0
    assert under_test.insert_count == 1
    assert under_test.delete_count == 0
    assert under_test.exit_count == 1
    assert actual == expected
