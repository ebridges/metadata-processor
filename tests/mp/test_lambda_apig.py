import logging
import os
from copy import deepcopy
from unittest.mock import patch, MagicMock

import boto3
import sentry_sdk

from mp import SOURCE_BUCKET, DEFAULT_REGION, MONITORING_DSN
from mp.lambda_apig import api_handler
from mp import lambda_common
from mp.model.image_key import ImageKey
from mp.util import tools
from mp.io.loader import s3_loader

from tests.mp import mock_event_keys, apig_event_sample


MOCK_BUCKET = 'mock_bucket_name'


def test_api_handler_normal_case(mocker):
    mock_event, mock_s3, mock_writer, mock_sentry_scope = setup_mocks(mocker)
    mock_key = ImageKey(mock_event['path'][1:])

    actual_response = api_handler(mock_event)

    logging.info.assert_called_once()
    logging.debug.assert_called_once()
    tools.configure_logging.assert_called_once()
    sentry_sdk.configure_scope.assert_called_once()
    assert_sentry_scope(mock_sentry_scope, mock_event, mock_key)
    boto3.resource.assert_called_with('s3', region_name=DEFAULT_REGION)
    mock_s3.list_objects_v2.assert_called_with(
        Bucket=MOCK_BUCKET, MaxKeys=1, Prefix=mock_key.file_path
    )
    mock_writer.__enter__.assert_called_once()
    mock_writer.exists.assert_called_with(mock_key.file_path)
    lambda_common.write_metadata.assert_called_with(mock_writer, mock_key)
    mock_writer.__exit__.assert_called_once()

    assert actual_response['statusCode'] == 200
    assert mock_key.file_path in actual_response['body']


def test_api_handler_force_update(mocker):
    mock_event, mock_s3, mock_writer, mock_sentry_scope = setup_mocks(
        mocker, writer_exists_retval=True, force_update_retval=True
    )
    mock_key = ImageKey(mock_event['path'][1:])

    actual_response = api_handler(mock_event)

    logging.info.assert_called_once()
    logging.debug.assert_called_once()
    tools.configure_logging.assert_called_once()
    sentry_sdk.configure_scope.assert_called_once()
    assert_sentry_scope(mock_sentry_scope, mock_event, mock_key)
    boto3.resource.assert_called_with('s3', region_name=DEFAULT_REGION)
    mock_s3.list_objects_v2.assert_called_with(
        Bucket=MOCK_BUCKET, MaxKeys=1, Prefix=mock_key.file_path
    )
    mock_writer.__enter__.assert_called_once()
    mock_writer.exists.assert_called_with(mock_key.file_path)
    lambda_common.write_metadata.assert_called_with(mock_writer, mock_key)
    mock_writer.__exit__.assert_called_once()

    assert actual_response['statusCode'] == 200
    assert mock_key.file_path in actual_response['body']


def test_api_handler_skip_force_update(mocker):
    mock_event, mock_s3, mock_writer, mock_sentry_scope = setup_mocks(
        mocker, writer_exists_retval=True, force_update_retval=False
    )
    mock_key = ImageKey(mock_event['path'][1:])

    actual_response = api_handler(mock_event)

    logging.info.assert_called_once()
    logging.debug.assert_called_once()
    tools.configure_logging.assert_called_once()
    sentry_sdk.configure_scope.assert_called_once()
    assert_sentry_scope(mock_sentry_scope, mock_event, mock_key)
    boto3.resource.assert_called_with('s3', region_name=DEFAULT_REGION)
    mock_s3.list_objects_v2.assert_called_with(
        Bucket=MOCK_BUCKET, MaxKeys=1, Prefix=mock_key.file_path
    )
    mock_writer.__enter__.assert_called_once()
    mock_writer.exists.assert_called_with(mock_key.file_path)
    lambda_common.write_metadata.assert_not_called()
    mock_writer.__exit__.assert_called_once()

    assert actual_response['statusCode'] == 204
    assert mock_key.file_path in actual_response['body']
    assert 'not processed' in actual_response['body']


def test_api_handler_malformed_event(mocker):
    mock_event, mock_s3, mock_writer, mock_sentry_scope = setup_mocks(mocker)
    mock_key = ImageKey(mock_event['path'][1:])

    mock_event['path'] = '/abc/abc/abc'

    actual_response = api_handler(mock_event)

    tools.configure_logging.assert_called_once()
    logging.info.assert_called_once()
    logging.debug.assert_called_once()
    sentry_sdk.configure_scope.assert_not_called()
    boto3.resource.assert_not_called()
    mock_s3.list_objects_v2.assert_not_called()
    mock_writer.__enter__.assert_not_called()
    mock_writer.exists.assert_not_called()
    lambda_common.write_metadata.assert_not_called()
    mock_writer.__exit__.assert_not_called()

    assert actual_response['statusCode'] == 404
    assert 'not found' in actual_response['body']


def assert_sentry_scope(scope, event, key):
    scope.__enter__.assert_called_once()
    scope.__enter__().set_extra.assert_called_with('processor_event', event)
    scope.__enter__().set_tag.call_count == 4
    scope.__exit__.assert_called_once()


def setup_mocks(mocker, writer_exists_retval=False, force_update_retval=False):
    mock_s3 = MagicMock()
    # used by s3_loader.key_exists:
    mock_s3.list_objects_v2 = MagicMock(return_value=mock_event_keys)

    mock_writer = MagicMock()
    mock_writer.exists = MagicMock(return_value=writer_exists_retval)

    mock_sentry_scope = MagicMock()

    mocker.patch.object(lambda_common, 'write_metadata', MagicMock())
    mocker.patch.object(
        lambda_common, 'init_writer', MagicMock(return_value=mock_writer)
    )
    mocker.patch.object(
        lambda_common, 'check_force_update', MagicMock(return_value=force_update_retval)
    )
    mocker.patch.object(boto3, 'resource', MagicMock(return_value=mock_s3))
    mocker.patch.object(tools, 'configure_logging')
    mocker.patch.object(
        sentry_sdk, 'configure_scope', MagicMock(return_value=mock_sentry_scope)
    )
    mocker.patch.object(logging, 'debug')
    mocker.patch.object(logging, 'info')

    mock_env = {SOURCE_BUCKET: MOCK_BUCKET}
    mocker.patch.dict(os.environ, mock_env)

    mock_event = deepcopy(apig_event_sample)

    return mock_event, mock_s3, mock_writer, mock_sentry_scope
