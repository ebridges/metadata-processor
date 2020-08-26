import os
from copy import deepcopy

from pytest import raises

from mp import SOURCE_BUCKET, TRIGGER_ERROR
from mp.lambda_s3 import s3_handler

from tests.mp import (
    s3_put_single_event_sample,
    s3_put_multiple_event_sample,
    mock_event_keys,
    setup_mocks,
    assert_mocks,
)


def test_s3_loader_normal_case_single(mocker):
    setup_mocks(mocker, mock_env={SOURCE_BUCKET: 'foobar'})
    mock_event = deepcopy(s3_put_single_event_sample)

    s3_handler(mock_event)

    assert_mocks()


def test_s3_loader_normal_case_multiple(mocker):
    setup_mocks(mocker, mock_env={SOURCE_BUCKET: 'foobar'})
    mock_events = deepcopy(s3_put_multiple_event_sample)

    s3_handler(mock_events)

    assert_mocks(event_write_count=len(mock_event_keys))


def test_s3_loader_force_update(mocker):
    setup_mocks(
        mocker,
        writer_exists_retval=True,
        force_update_retval=True,
        mock_env={SOURCE_BUCKET: 'foobar'},
    )
    mock_event = deepcopy(s3_put_single_event_sample)

    s3_handler(mock_event)

    assert_mocks()


def test_s3_loader_skip_force_update(mocker):
    setup_mocks(
        mocker,
        writer_exists_retval=True,
        force_update_retval=False,
        mock_env={SOURCE_BUCKET: 'foobar'},
    )
    mock_event = deepcopy(s3_put_single_event_sample)

    s3_handler(mock_event)

    assert_mocks(
        event_write_count=0, init_writer_call_count=0, force_update_call_count=1
    )


def test_trigger_error(mocker):
    mock_scope = setup_mocks(mocker, mock_env={TRIGGER_ERROR: 'foobar'})
    mock_event = deepcopy(s3_put_single_event_sample)

    with raises(Exception):
        s3_handler(mock_event)

    assert_mocks(
        event_write_count=0, init_writer_call_count=0, force_update_call_count=0
    )
