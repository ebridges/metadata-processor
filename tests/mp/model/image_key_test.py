from pytest import raises
from mp.model.image_key import parse, ImageKey

uid = '2d249780-7fe9-4c49-aa31-0a30d56afa0f'
iid = '6ee17b58-7008-41e9-a612-320017981ea0'
ext = 'jpg'
under_test = f'{uid}/{iid}.{ext}'


def test_parse_image_key():
    expected = uid, iid, ext
    actual = parse(under_test)
    assert expected == actual


def test_parse_wrongfmt():
    bad_fmt = f'/{under_test}'
    with raises(ValueError):
        parse(bad_fmt)


def test_imagekey_str():
    actual = ImageKey(under_test)
    assert under_test == str(actual)


def test_imagekey_components():
    actual = ImageKey(under_test)
    assert actual.owner_id == uid
    assert actual.image_id == iid
    assert actual.extension == ext
    assert actual.filename == f'{iid}.{ext}'


def test_imagekey_components_wrongfmt():
    bad_fmt = f'/{under_test}'
    with raises(ValueError):
        ImageKey(bad_fmt)
