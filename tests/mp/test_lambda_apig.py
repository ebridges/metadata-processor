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

# mock_info
# mock debug
# mock configure_logging
# mock init_monitoring
# mock configure_scope
#      _enter_
#      _exit_
#      scope.set_tag
#      scope.set_extra
# mock environ.get
# mock extract_image_key_from_apig_event
# mock check_force_update
# mock key_exists
# mock init_writer
#      _enter_
#      _exit_
#      writer.exists
# mock write_metadata
# mock generate_json_respone

mock_s3 = MagicMock()
mock_s3.list_objects_v2 = MagicMock(return_value=[])

mock_bucket = 'mock_bucket_name'


def test_api_handler(mocker):
    mocker.patch('mp.lambda_common.generate_json_response')
    mocker.patch.object(boto3, 'resource', MagicMock(return_value=mock_s3))
    mocker.patch('mp.io.loader.s3_loader.key_exists')
    mocker.patch('mp.util.tools.configure_logging')
    mocker.patch.object(sentry_sdk, 'init')
    mocker.patch.object(logging, 'debug')
    mocker.patch.object(logging, 'info')

    mock_env = {
        SOURCE_BUCKET: mock_bucket,
        # MONITORING_DSN: None
    }
    mocker.patch.dict(os.environ, mock_env)

    mock_event = deepcopy(apig_event_sample)
    mock_context = {}
    mock_key = ImageKey(mock_event_keys[0])

    actual_response = api_handler(mock_event, mock_context)

    # logging.info.assert_called_once()
    # logging.debug.assert_called_once()
    # tools.configure_logging.assert_called_once()
    # s3_loader.key_exists.assert_called_with(mock_key.file_path)
    # boto3.resource.assert_called_with('s3', region_name=DEFAULT_REGION)
    # mock_s3.list_objects_v2.assert_called_with(Bucket=mock_bucket, MaxKeys=1, Prefix=mock_key.file_path)


# def mock_configure_scope(enter_retval=None, exit_retval=True):
#     cs = Mock()
#     if not enter_retval:
#         enter_retval = cs
#     cs.__enter__ = Mock(return_value=enter_retval)
#     cs.__exit__ = Mock(return_value=exit_retval)
#     cs.set_tag = Mock()
#     cs.set_extra = Mock()
#     return cs
