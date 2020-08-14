from io import StringIO
from tempfile import NamedTemporaryFile
from unittest.mock import patch
from assertpy import assert_that, contents_of

from mp.io.writer.metadata_writer import (
    MetadataWriter,
    DatabaseMetadataWriter,
    FilehandleMetadataWriter,
)
from tests.mp.io.writer.mock_metadata_formatter import mock_formatter
from tests.mp.model.mock_metadata import MockMetadata


def test_stdout_metadatawriter(capsys):
    mock_data = {'foo': 'bar'}
    mock_metadata = MockMetadata(args=mock_data)
    expected = str(mock_data)
    with patch('sys.stdout', new=StringIO()) as mock_stdout:
        under_test = StdoutMetadataWriter(mock_stdout, mock_formatter)
        under_test.write(mock_metadata)
        actual = mock_stdout.getvalue()
        assert expected == actual


def test_file_metadatawriter():
    mock_data = {'foo': 'bar'}
    mock_metadata = MockMetadata(args=mock_data)
    expected_data = str(mock_data)
    with NamedTemporaryFile() as expected, NamedTemporaryFile() as actual:
        expected.write(expected_data.encode())
        under_test = FileMetadataWriter(actual.name, mock_formatter)
        under_test.write(mock_metadata)
        actual_contents = contents_of(actual.name)
        assert_that(actual_contents).contains(expected_data)
