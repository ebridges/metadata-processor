import os
from unittest.mock import MagicMock

import boto3
from pytest import raises

from mp import SOURCE_BUCKET
from mp.io.loader import s3_loader
from tests.mp import mock_event_keys

MOCK_REGION_NAME = 'mock_region_name'
MOCK_BUCKET_NAME = 'mock_bucket_name'


def test_key_exists_true(mocker):
    setup_key_exists(mocker)
    assert s3_loader.key_exists(mock_event_keys[0])


def test_key_exists_false(mocker):
    setup_key_exists(mocker)
    assert not s3_loader.key_exists('/aaa/bbb/ccc')


def test_key_exists_diff_region(mocker):
    s3_lister = setup_key_exists(mocker)
    assert s3_loader.key_exists(mock_event_keys[0], region=MOCK_REGION_NAME)
    boto3.client.assert_called_with('s3', region_name=MOCK_REGION_NAME)
    s3_lister.list_objects_v2.assert_called_with(
        Bucket=MOCK_BUCKET_NAME, MaxKeys=1, Prefix=mock_event_keys[0]
    )


def test_download_file_from_s3_normal_case(mocker):
    s3_object, s3_getter = setup_download_file_from_s3(mocker)
    key = 'mock_key'
    dest = 'mock_dest'
    s3_loader.download_file_from_s3(key, dest)
    boto3.resource.assert_called_once()
    s3_object.Object.assert_called_with(MOCK_BUCKET_NAME, key)
    s3_getter.download_file.assert_called_with(dest)


def test_download_file_from_s3_not_found(mocker):
    s3_object, s3_getter = setup_download_file_from_s3(mocker)
    exception = Exception()
    exception.response = {'Error': {'Code': '404'}}
    s3_getter.download_file.side_effect = exception

    key = 'mock_key'
    dest = 'mock_dest'
    with raises(s3_loader.KeyNotFound):
        s3_loader.download_file_from_s3(key, dest)
    boto3.resource.assert_called_once()
    s3_object.Object.assert_called_with(MOCK_BUCKET_NAME, key)
    s3_getter.download_file.assert_called_with(dest)


def setup_key_exists(mocker):
    mocker.patch.dict(os.environ, {SOURCE_BUCKET: MOCK_BUCKET_NAME})
    s3_lister = MagicMock()
    s3_lister.list_objects_v2 = MagicMock(return_value=mock_event_keys)
    mocker.patch.object(boto3, 'client', MagicMock(return_value=s3_lister))
    return s3_lister


def setup_download_file_from_s3(mocker):
    mocker.patch.dict(os.environ, {SOURCE_BUCKET: MOCK_BUCKET_NAME})
    s3_object = MagicMock()
    s3_getter = MagicMock()
    s3_object.Object = MagicMock(return_value=s3_getter)
    s3_getter.download_file = MagicMock()
    mocker.patch.object(boto3, 'resource', MagicMock(return_value=s3_object))
    return s3_object, s3_getter
