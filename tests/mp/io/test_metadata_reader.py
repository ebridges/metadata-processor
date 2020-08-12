from os.path import dirname
from datetime import datetime

from mp.io.metadata_reader import (
    apex_to_aperture,
    apex_to_shutterspeed,
    extract_aperture,
    extract_createdate_exif,
    extract_dimensions,
    extract_focal_length,
    extract_gps_coords,
    extract_gps_date,
    extract_gps_datetime,
    extract_gps_degrees,
    extract_gps_time,
    extract_metadata,
    extract_shutter_speed,
    rational_to_float,
    resolve_int,
    resolve_rational,
    resolve_str,
)
from mp.model import *
from mp.model.metadata import Metadata, create_day_id
from mp.model.image_key import ImageKey

CURRENT_DIR = dirname(__file__)


def test_extract_metadata():
    image_slug = (
        '2d249780-7fe9-4c49-aa31-0a30d56afa0f/13e16670-7010-11e9-b5c4-320017981ea0.jpg'
    )
    image_file = f'{CURRENT_DIR}/img/testExtractMetadata/20190224T205115.jpg'
    image_key = ImageKey(image_slug)

    create_date = datetime.fromisoformat('2019-02-24T20:51:15')
    create_date.replace(tzinfo=None)
    create_date_utc = datetime.fromisoformat('2019-02-25T01:51:08+00:00')

    expected = Metadata(
        args={
            IMAGE_ID: image_key.image_id,
            OWNER_ID: image_key.owner_id,
            FILE_PATH: image_key.file_path,
            FILE_SIZE: 3954388,
            CREATE_DATE: create_date,
            CREATE_DAY_ID: create_day_id(create_date),
            IMAGE_WIDTH: 4032,
            IMAGE_HEIGHT: 3024,
            CAMERA_MAKE: 'Google',
            CAMERA_MODEL: 'Pixel 3',
            APERTURE: 'f/1.8',
            SHUTTER_SPEED_N: 391,
            SHUTTER_SPEED_D: 100,
            SHUTTER_SPEED: '1/15 sec',
            FOCAL_LENGTH: '27mm',
            FOCAL_LENGTH_N: 4440,
            FOCAL_LENGTH_D: 1000,
            ISO_SPEED: 1514,
            GPS_LON: -73.9626138888889,
            GPS_LAT: 40.718075,
            GPS_ALT: 0.0,
            GPS_DATE_TIME: create_date_utc,
        }
    )

    actual = extract_metadata(image_key, image_file)

    assert expected == actual


def test_extract_metadata_CreateDateFromXmp():
    image_slug = (
        '57f738b8-700f-11e9-90ab-320017981ea0/9d90b8f3-113d-4476-afe8-9fc0ac265850.jpg'
    )
    image_file = f'{CURRENT_DIR}/img/testExtractMetadata_CreateDateFromXmp/9d90b8f3-113d-4476-afe8-9fc0ac265850.jpg'
    image_key = ImageKey(image_slug)
    expected = '2016-02-22T20:57:08'
    actual = extract_metadata(image_key, image_file)
    assert expected == actual.create_date.isoformat()


def test_extract_gps_coords():
    md = {
        'Exif.GPSInfo.GPSAltitude': '0/1000',
        'Exif.GPSInfo.GPSLatitude': '40/1 43/1 507/100',
        'Exif.GPSInfo.GPSLatitudeRef': 'N',
        'Exif.GPSInfo.GPSLongitude': '73/1 57/1 4541/100',
        'Exif.GPSInfo.GPSLongitudeRef': 'W',
    }
    expected = (40.718075, -73.9626138888889, 0.0)
    actual = extract_gps_coords(md)
    assert expected == actual


def test_extract_focal_length():
    md = {
        'Exif.Photo.FocalLengthIn35mmFilm': '27',
        'Exif.Photo.FocalLength': '4440/1000',
    }
    expected = ('27mm', 4440, 1000)
    actual = extract_focal_length(md)
    assert expected == actual


def test_extract_shutter_speed():
    md = {'Exif.Photo.ShutterSpeedValue': '391/100'}
    expected = ('1/15 sec', 391, 100)
    actual = extract_shutter_speed(md)
    assert expected == actual


def test_extract_aperture():
    md = {'Exif.Photo.ApertureValue': '170/100'}
    expected = 'f/1.8'
    actual = extract_aperture(md)
    assert expected == actual


def test_extract_dimensions():
    md = {
        'Exif.Image.ImageWidth': '123',
        'Exif.Image.ImageLength': '456',
    }
    expected = (123, 456)
    actual = extract_dimensions(md)
    assert expected == actual


def test_extract_dimensions_alt1():
    md = {
        'Exif.Photo.PixelXDimension': '123',
        'Exif.Photo.PixelYDimension': '456',
    }
    expected = (123, 456)
    actual = extract_dimensions(md)
    assert expected == actual


def test_extract_dimensions_alt2():
    md = {
        'Exif.Photo.PixelXDimension': '123',
        'Exif.Image.ImageLength': '456',
    }
    expected = (123, 456)
    actual = extract_dimensions(md)
    assert expected == actual


def test_extract_createdate_gooddate():
    md = {
        'Exif.Image.DateTime': '2019-02-24T20:51:15',
    }
    expected = datetime(2019, 2, 24, 20, 51, 15)
    actual = extract_createdate_exif(md)
    assert expected == actual


def test_extract_createdate_baddate():
    md = {
        'Exif.Photo.DateTimeDigitized': 'bad date',
        'Exif.Photo.DateTimeOriginal': '2019-02-24T20:51:15',
    }
    expected = None
    actual = extract_createdate_exif(md)
    assert expected == actual


def test_extract_gps_datetime():
    md = {
        'Exif.GPSInfo.GPSDateStamp': '2019: 02: 25',
        'Exif.GPSInfo.GPSTimeStamp': '1/1 51/1 8/1',
    }
    expected = '2019-02-25T01:51:08+00:00'
    dt = extract_gps_datetime(md)
    actual = dt.isoformat()
    assert expected == actual


def test_extract_gps_date():
    md = {'Exif.GPSInfo.GPSDateStamp': '2019: 02: 25'}
    expected = '2019:02:25'
    actual = extract_gps_date(md)
    assert expected == actual


def test_extract_gps_time():
    md = {'Exif.GPSInfo.GPSTimeStamp': '1/1 51/1 8/1'}
    expected = '01:51:08'
    actual = extract_gps_time(md)
    assert expected == actual


def test_extract_gps_degrees():
    md = {'aaa': '73/1 57/1 4541/100', 'bbb': '40/1 43/1 507/100'}
    keys = ['bbb']
    expected = 40.718075
    actual = extract_gps_degrees(md, keys)
    assert expected == actual


def test_resolve_str():
    md = {'aaa': '111', 'bbb': '222'}
    keys = ['bbb']
    expected = '222'
    actual = resolve_str(md, keys)
    assert expected == actual


def test_rational_to_float():
    undertest = (2, 3)
    expected = 0.67
    actual = rational_to_float(undertest, p=2)
    assert expected == actual


def test_rational_to_float_zero_denominator():
    undertest = (2, 0)
    expected = 0
    actual = rational_to_float(undertest)
    assert expected == actual


def test_rational_to_float_none_denominator():
    undertest = (2, None)
    actual = rational_to_float(undertest)
    assert actual is None


def test_resolve_rational():
    undertest = '222/444'
    expected = (222, 444)
    actual = resolve_rational(undertest)
    assert expected == actual


def test_resolve_int():
    md = {'aaa': '111', 'bbb': '222'}
    keys = ['bbb']
    expected = 222
    actual = resolve_int(md, keys)
    assert expected == actual


def test_apex_to_aperture():
    apex_val = 170 / 100
    expected = 1.8
    actual = apex_to_aperture(apex_val)
    assert expected == actual


def test_apex_to_shutterspeed():
    apex_val = 391 / 100
    expected = (1, 15)
    actual = apex_to_shutterspeed(apex_val)
    assert expected == actual
