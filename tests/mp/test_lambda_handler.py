import os
import logging
from copy import deepcopy
from unittest.mock import MagicMock

import sentry_sdk
from pytest import raises

from mp.model.image_key import ImageKey
from mp import lambda_handler
from mp import lambda_common, SOURCE_BUCKET, TRIGGER_ERROR
from mp.io.loader import s3_loader
from mp.util import tools

from tests.mp import (
    apig_event_sample,
    s3_put_single_event_sample,
    s3_put_multiple_event_sample,
    mock_event_keys,
)
from tests.mp.io.writer.mock_metadata_writer import MockDatabaseMetadataWriter

def test_get_event_type_s3():
    expected = 's3'
    actual = lambda_handler.get_event_type(s3_put_single_event_sample)
    assert expected == actual


def test_get_event_type_apig():
    expected = 'api'
    actual = lambda_handler.get_event_type(apig_event_sample)
    assert expected == actual


def test_get_event_type_none():
    actual = lambda_handler.get_event_type(None)
    assert actual is None


def test_get_event_type_empty():
    actual = lambda_handler.get_event_type({})
    assert actual is None


def test_get_event_type_unrecognized():
    actual = lambda_handler.get_event_type({'foo': 'bar'})
    assert actual is None


def test_handler_s3_normal_case(mocker):
    mock_event = s3_put_single_event_sample
    force_update_retval = False
    event_type = 's3'
    mock_env = {TRIGGER_ERROR: True}
    setup_handler(mocker, force_update_retval, event_type)

    lambda_handler.handler(mock_event)

    assert_handler()


def test_handler_apig_normal_case(mocker):
    mock_event = s3_put_single_event_sample
    force_update_retval = False
    event_type = 'api'
    setup_handler(mocker, force_update_retval, event_type)

    lambda_handler.handler(mock_event)

    assert_handler()


def test_handler_s3_trigger_error(mocker):
    mock_event = s3_put_single_event_sample
    force_update_retval = False
    event_type = 's3'
    env = {TRIGGER_ERROR: 'true'}
    setup_handler(mocker, force_update_retval, event_type, mock_env=env)

    with raises(Exception):
        lambda_handler.handler(mock_event)


def test_handler_unrecognized_event_type(mocker):
    mock_event = {}
    force_update_retval = False
    event_type = 'foobar'
    setup_handler(mocker, force_update_retval, event_type)

    with raises(Exception):
        lambda_handler.handler(mock_event)


def test_api_handler_single_normal_case(mocker):
    force_update = False
    exists_in_s3 = True
    exists_in_db = False
    actual_response = _api_handler(mocker, force_update, exists_in_s3, exists_in_db)


def test_api_handler_single_force_update(mocker):
    force_update = True
    exists_in_s3 = True
    exists_in_db = True
    actual_response = _api_handler(mocker, force_update, exists_in_s3, exists_in_db)


def test_api_handler_single_skip_update(mocker):
    force_update = False
    exists_in_s3 = True
    exists_in_db = True
    actual_response = _api_handler(
        mocker, force_update, exists_in_s3, exists_in_db, event_write_cnt=0, sc=204
    )


def test_api_handler_single_image_not_found(mocker):
    force_update = False
    exists_in_s3 = False
    exists_in_db = False
    _api_handler(
        mocker,
        force_update,
        exists_in_s3,
        exists_in_db,
        event_write_cnt=0,
        sc=404,
        mock_env={SOURCE_BUCKET: 'foobar'},
    )


def test_s3_handler_single_normal_case(mocker):
    force_update = False
    exists_in_s3 = True
    exists_in_db = False
    _s3_handler_single(mocker, force_update, exists_in_s3, exists_in_db)


def test_s3_handler_single_exception(mocker):
    force_update = False
    exists_in_s3 = True
    exists_in_db = False
    exception_thrown = ValueError('Boom!')
    _s3_handler_single(mocker, force_update, exists_in_s3, exists_in_db, mock_exception=exception_thrown)


def test_s3_handler_single_force_update(mocker):
    force_update = True
    exists_in_s3 = True
    exists_in_db = True
    _s3_handler_single(mocker, force_update, exists_in_s3, exists_in_db)


def test_s3_handler_single_skip_update(mocker):
    force_update = False
    exists_in_s3 = True
    exists_in_db = True
    _s3_handler_single(
        mocker, force_update, exists_in_s3, exists_in_db, event_write_cnt=0
    )


def test_s3_handler_single_image_not_found(mocker):
    force_update = False
    exists_in_s3 = False
    exists_in_db = False
    _s3_handler_multi(
        mocker,
        force_update,
        exists_in_s3,
        exists_in_db,
        event_write_cnt=0,
        mock_env={SOURCE_BUCKET: 'foobar'},
    )


def test_s3_handler_multiple_normal_case(mocker):
    force_update = False
    exists_in_s3 = True
    exists_in_db = False
    _s3_handler_multi(mocker, force_update, exists_in_s3, exists_in_db)


def test_s3_handler_multiple_force_update(mocker):
    force_update = True
    exists_in_s3 = True
    exists_in_db = True
    _s3_handler_multi(mocker, force_update, exists_in_s3, exists_in_db)


def test_s3_handler_multiple_skip_update(mocker):
    force_update = False
    exists_in_s3 = True
    exists_in_db = True
    _s3_handler_multi(
        mocker, force_update, exists_in_s3, exists_in_db, event_write_cnt=0
    )


def _api_handler(
    mocker,
    force_update,
    exists_in_s3,
    exists_in_db,
    sc=200,
    event=None,
    event_write_cnt=None,
    mock_env={},
):
    if event is not None:
        mock_event = event
    else:
        mock_event = deepcopy(apig_event_sample)
        mock_key = ImageKey(mock_event['path'][1:])
    actual_response = _handler_run(
        mocker,
        lambda_handler.api_handler,
        force_update,
        exists_in_s3,
        exists_in_db,
        mock_event,
        event_write_cnt=event_write_cnt,
        mock_env=mock_env,
    )

    assert actual_response['statusCode'] == sc
    if mock_key:
        assert mock_key.file_path in actual_response['body']


def _s3_handler_multi(
    mocker, force_update, exists_in_s3, exists_in_db, event_write_cnt=None, mock_env={}
):
    mock_events = deepcopy(s3_put_multiple_event_sample)
    event_cnt = len(mock_event_keys)
    _handler_run(
        mocker,
        lambda_handler.s3_handler,
        force_update,
        exists_in_s3,
        exists_in_db,
        mock_events,
        event_cnt,
        event_write_cnt=event_write_cnt,
        mock_env=mock_env,
    )


def _s3_handler_single(
    mocker, force_update, exists_in_s3, exists_in_db, event_write_cnt=None, mock_env={}, mock_exception=None
):
    mock_event = deepcopy(s3_put_single_event_sample)
    _handler_run(
        mocker,
        lambda_handler.s3_handler,
        force_update,
        exists_in_s3,
        exists_in_db,
        mock_event,
        event_write_cnt=event_write_cnt,
        mock_env=mock_env,
        mock_exception=mock_exception,
    )


def _handler_run(
    mocker,
    handler,
    force_update,
    exists_in_s3,
    exists_in_db,
    mock_event,
    event_cnt=1,
    event_write_cnt=None,
    mock_env={},
    mock_exception=None,
):
    if event_write_cnt is None:
        event_write_cnt = event_cnt

    mock_writer = MockDatabaseMetadataWriter(exists_retval=exists_in_db)
    mocker.patch.object(lambda_common, 'init_metadata_writer', MagicMock(return_value=mock_writer))

    mocker.patch.object(s3_loader, 'key_exists', MagicMock(return_value=exists_in_s3))

    if mock_exception:
        mock_write_metadata = MagicMock(side_effect=mock_exception)
        mocker.patch.object(lambda_common, 'init_exception_writer')
        mocker.patch.object(lambda_common, 'write_exception_event')
    else:
        mock_write_metadata = MagicMock()

    mocker.patch.object(lambda_common, 'write_metadata', mock_write_metadata)

    mock_scope = MagicMock()

    if mock_env:
        mocker.patch.dict(os.environ, mock_env, clear=True)

    response = handler(mock_event, mock_scope, force_update=force_update)

    assert mock_scope.set_tag.call_count == 3 * event_cnt
    assert s3_loader.key_exists.call_count == event_cnt
    if exists_in_s3:
        assert lambda_common.init_metadata_writer.call_count == 1
        assert mock_writer.exists_count == event_cnt
        assert lambda_common.write_metadata.call_count == event_write_cnt

    if mock_exception:
        assert lambda_common.init_exception_writer.call_count == 1
        assert lambda_common.write_exception_event.call_count == 1

    return response


def setup_handler(mocker, force_update_retval, event_type, mock_env={}):
    mocker.patch.object(tools, 'configure_logging')
    mocker.patch.object(logging, 'info')
    mocker.patch.object(logging, 'debug')
    mocker.patch.object(
        lambda_common, 'check_force_update', MagicMock(return_value=force_update_retval)
    )
    mocker.patch.object(sentry_sdk, 'configure_scope')
    mocker.patch.dict(os.environ, mock_env)
    mocker.patch.object(
        lambda_handler, 'get_event_type', MagicMock(return_value=event_type)
    )
    mocker.patch.object(lambda_handler, 's3_handler')
    mocker.patch.object(lambda_handler, 'api_handler')


def assert_handler():
    tools.configure_logging.assert_called_once()
    logging.info.assert_called()
    logging.debug.assert_called()
    lambda_common.check_force_update.assert_called_once()
    lambda_handler.get_event_type.assert_called_once()
