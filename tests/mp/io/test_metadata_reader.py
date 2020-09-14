from os.path import dirname
from datetime import datetime, timezone

from PIL.TiffImagePlugin import IFDRational

from pytest import raises

from mp.io.metadata_reader import (
    apex_to_aperture,
    apex_to_shutterspeed,
    extract_aperture,
    extract_createdate_exif,
    extract_focal_length,
    extract_gps_coords,
    extract_gps_date,
    extract_gps_datetime,
    extract_gps_degrees,
    extract_gps_time,
    extract_metadata,
    extract_shutter_speed,
    resolve_rational,
)
from mp.model import *
from mp.io.metadata_tags import *
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


def test_extract_metadata_MissingMetadata():
    image_slug = (
        '57f738b8-700f-11e9-90ab-320017981ea0/9d90b8f3-113d-4476-afe8-9fc0ac265850.jpg'
    )
    image_file = f'{CURRENT_DIR}/img/testExtractMetadata_MissingMetadata/IMG_1770.jpg'
    image_key = ImageKey(image_slug)
    with raises(ValueError):
        extract_metadata(image_key, image_file)


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
        TAG_GPSINFO: {
            TAG_GPSINFO_GPSALTITUDE: 0.0,
            TAG_GPSINFO_GPSLATITUDE: (40.0, 43.0, 5.07),
            TAG_GPSINFO_GPSLATITUDEREF: 'N',
            TAG_GPSINFO_GPSLONGITUDE: (73.0, 57.0, 45.41),
            TAG_GPSINFO_GPSLONGITUDEREF: 'W',
            TAG_GPSINFO_GPSDATESTAMP: '2020:01:02',
            TAG_GPSINFO_GPSTIMESTAMP: (3.0, 4.0, 5.0),
        }
    }
    expected = (
        40.718075,
        -73.9626138888889,
        0.0,
        datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )
    actual = extract_gps_coords(md)
    assert expected == actual


def test_extract_gps_coords_flip_coords():
    md = {
        TAG_GPSINFO: {
            TAG_GPSINFO_GPSALTITUDE: 0.0,
            TAG_GPSINFO_GPSLATITUDE: (40.0, 43.0, 5.07),
            TAG_GPSINFO_GPSLATITUDEREF: 'S',
            TAG_GPSINFO_GPSLONGITUDE: (73.0, 57.0, 45.41),
            TAG_GPSINFO_GPSLONGITUDEREF: 'E',
            TAG_GPSINFO_GPSDATESTAMP: '2020:01:02',
            TAG_GPSINFO_GPSTIMESTAMP: (3.0, 4.0, 5.0),
        }
    }
    expected = (
        -40.718075,
        73.9626138888889,
        0.0,
        datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )
    actual = extract_gps_coords(md)
    assert expected == actual


def test_extract_gps_coords():
    md = {
        TAG_GPSINFO: {
            TAG_GPSINFO_GPSALTITUDE: 0.0,
            TAG_GPSINFO_GPSDATESTAMP: '2020:01:02',
            TAG_GPSINFO_GPSTIMESTAMP: (3.0, 4.0, 5.0),
        }
    }
    expected = (None, None, 0.0, datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    actual = extract_gps_coords(md)
    assert expected == actual


def test_extract_focal_length():
    md = {
        TAG_PHOTO_FOCALLENGTHIN35MMFILM: '27',
        TAG_PHOTO_FOCALLENGTH: IFDRational(4440, 1000),
    }
    expected = ('27mm', 4440, 1000)
    actual = extract_focal_length(md)
    assert expected == actual


def test_extract_shutter_speed():
    md = {TAG_PHOTO_SHUTTERSPEEDVALUE: IFDRational(391, 100)}
    expected = ('1/15 sec', 391, 100)
    actual = extract_shutter_speed(md)
    assert expected == actual


def test_extract_aperture():
    md = {TAG_PHOTO_APERTUREVALUE: IFDRational(170, 100)}
    expected = 'f/1.8'
    actual = extract_aperture(md)
    assert expected == actual


def test_extract_createdate_gooddate():
    md = {
        TAG_IMAGE_DATETIME: '2019-02-24T20:51:15',
    }
    expected = datetime(2019, 2, 24, 20, 51, 15)
    actual = extract_createdate_exif(md)
    assert expected == actual


def test_extract_createdate_baddate():
    md = {
        TAG_PHOTO_DATETIMEDIGITIZED: 'bad date',
        TAG_PHOTO_DATETIMEORIGINAL: '2019-02-24T20:51:15',
    }
    expected = None
    actual = extract_createdate_exif(md)
    assert expected == actual


def test_extract_gps_datetime():
    md = {
        TAG_GPSINFO_GPSDATESTAMP: '2019: 02: 25',
        TAG_GPSINFO_GPSTIMESTAMP: (1.0, 51.0, 8.0),
    }
    expected = '2019-02-25T01:51:08+00:00'
    dt = extract_gps_datetime(md)
    actual = dt.isoformat()
    assert expected == actual


def test_extract_gps_date():
    md = {TAG_GPSINFO_GPSDATESTAMP: '2019: 02: 25'}
    expected = '2019:02:25'
    actual = extract_gps_date(md)
    assert expected == actual


def test_extract_gps_time():
    md = {TAG_GPSINFO_GPSTIMESTAMP: (1.0, 51.0, 8)}
    expected = '01:51:08'
    actual = extract_gps_time(md)
    assert expected == actual


def test_extract_gps_degrees():
    md = {'aaa': (73.0, 57.0, 45.41), 'bbb': (40.0, 43.0, 5.07)}
    keys = ['bbb']
    expected = 40.718075
    actual = extract_gps_degrees(md, keys)
    assert expected == actual


def test_extract_gps_degrees_missing():
    md = {'aaa': None, 'bbb': None}
    keys = ['bbb']
    expected = 0
    actual = extract_gps_degrees(md, keys)
    assert expected == actual


def test_resolve_rational():
    undertest = IFDRational(222, 444)
    expected = (222, 444)
    actual = resolve_rational(undertest)
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
