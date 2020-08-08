from datetime import datetime

from mp.model.metadata import Metadata, create_day_id


def test_create_day_id_normal_case():
    moment = datetime.strptime('2020/01/01 12:34:56', '%Y/%m/%d %H:%M:%S')
    expected = 20200101
    actual = create_day_id(moment)
    assert expected == actual


def test_create_day_id_midnight():
    moment = datetime.strptime('2020/01/01 00:00:00', '%Y/%m/%d %H:%M:%S')
    expected = 20200101
    actual = create_day_id(moment)
    assert expected == actual


def test_create_day_id_before_midnight():
    moment = datetime.strptime('2020/01/01 23:59:59', '%Y/%m/%d %H:%M:%S')
    expected = 20200101
    actual = create_day_id(moment)
    assert expected == actual


def test_metadata_default():
    actual = Metadata(args={})
    assert actual.artist == Metadata._defaults['artist']


def test_metadata_override():
    actual = Metadata(args={'artist': 'foobar'})
    assert actual.artist == 'foobar'
