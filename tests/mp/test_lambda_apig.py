import os
from copy import deepcopy

from mp import SOURCE_BUCKET, DEFAULT_REGION, MONITORING_DSN
from mp.lambda_apig import api_handler
from mp import lambda_common
from mp.model.image_key import ImageKey
from mp.util import tools
from mp.io.loader import s3_loader

from tests.mp import (
    MOCK_BUCKET,
    mock_event_keys,
    apig_event_sample,
    setup_mocks,
    assert_mocks,
)


def test_api_handler_normal_case(mocker):
    setup_mocks(mocker, mock_env={SOURCE_BUCKET: MOCK_BUCKET})
    mock_event = deepcopy(apig_event_sample)
    mock_key = ImageKey(mock_event['path'][1:])

    actual_response = api_handler(mock_event)

    assert_mocks()

    assert actual_response['statusCode'] == 200
    assert mock_key.file_path in actual_response['body']


def test_api_handler_force_update(mocker):
    setup_mocks(
        mocker,
        writer_exists_retval=True,
        force_update_retval=True,
        mock_env={SOURCE_BUCKET: MOCK_BUCKET},
    )
    mock_event = deepcopy(apig_event_sample)
    mock_key = ImageKey(mock_event['path'][1:])

    actual_response = api_handler(mock_event)

    assert_mocks()

    assert actual_response['statusCode'] == 200
    assert mock_key.file_path in actual_response['body']


def test_api_handler_skip_force_update(mocker):
    setup_mocks(
        mocker,
        writer_exists_retval=True,
        force_update_retval=False,
        mock_env={SOURCE_BUCKET: MOCK_BUCKET},
    )
    mock_event = deepcopy(apig_event_sample)
    mock_key = ImageKey(mock_event['path'][1:])

    actual_response = api_handler(mock_event)

    assert_mocks(event_write_count=0)

    assert actual_response['statusCode'] == 204
    assert mock_key.file_path in actual_response['body']
    assert 'not processed' in actual_response['body']


def test_api_handler_malformed_event(mocker):
    setup_mocks(mocker)
    mock_event = deepcopy(apig_event_sample)
    mock_key = ImageKey(mock_event['path'][1:])

    mock_event['path'] = '/abc/abc/abc'

    actual_response = api_handler(mock_event)

    assert_mocks(
        event_write_count=0, init_writer_call_count=0, force_update_call_count=0
    )

    assert actual_response['statusCode'] == 404
    assert 'not found' in actual_response['body']
