from copy import deepcopy

from pytest import raises

from mp.model.image_key import ImageKey
from mp.lambda_common import (
    extract_image_keys_from_s3_event,
    extract_image_key_from_apig_event,
    check_force_update,
)

from tests.mp import (
    mock_event_keys,
    s3_put_multiple_event_sample,
    s3_put_single_event_sample,
    apig_event_sample,
)


def test_check_force_update_true():
    mock_event = deepcopy(apig_event_sample)

    mock_event['queryStringParameters'] = 'update=true'
    assert check_force_update(mock_event) == True

    mock_event['queryStringParameters'] = 'update'
    assert check_force_update(mock_event) == True


def test_check_force_update_missing_param():
    mock_event = deepcopy(apig_event_sample)
    assert check_force_update(mock_event) == False


def test_check_force_update_malformed():
    mock_event = deepcopy(apig_event_sample)
    mock_event['queryStringParameters'] = 'xxxxxx'
    assert check_force_update(mock_event) == False


def test_extract_image_key_from_apig_event():
    expected_key = mock_event_keys[0]
    actual_key = extract_image_key_from_apig_event(apig_event_sample)
    assert expected_key == actual_key.file_path


def test_extract_image_key_from_empty_path():
    actual_key = extract_image_key_from_apig_event({'path': None})
    assert actual_key is None


def test_extract_image_key_from_empty_event():
    actual_key = extract_image_key_from_apig_event({})
    assert actual_key is None


def test_extract_image_key_from_none_path():
    actual_key = extract_image_key_from_apig_event(None)
    assert actual_key is None


def test_extract_multiple_image_keys_from_s3_event():
    expected_keys = [ImageKey(path=p) for p in mock_event_keys]
    expected_event = s3_put_multiple_event_sample
    actual_keys = extract_image_keys_from_s3_event(expected_event)
    assert all(elem in expected_keys for elem in actual_keys)


def test_extract_single_image_key_from_s3_event():
    expected_keys = [ImageKey(path=mock_event_keys[0])]
    expected_event = s3_put_single_event_sample
    actual_keys = extract_image_keys_from_s3_event(expected_event)
    assert all(elem in expected_keys for elem in actual_keys)


def test_zero_records_s3_event():
    actual_keys = extract_image_keys_from_s3_event({'Records': []})
    assert len(actual_keys) == 0

    actual_keys = extract_image_keys_from_s3_event({'Records': [{'s3': {}}]})
    assert len(actual_keys) == 0

    actual_keys = extract_image_keys_from_s3_event(
        {'Records': [{'s3': {'object': {}}}]}
    )
    assert len(actual_keys) == 0

    actual_keys = extract_image_keys_from_s3_event(
        {'Records': [{'s3': {'object': {'key': None}}}]}
    )
    assert len(actual_keys) == 0


def test_empty_s3_event():
    with raises(KeyError):
        extract_image_keys_from_s3_event({})


def test_none_s3_event():
    with raises(TypeError):
        extract_image_keys_from_s3_event(None)
