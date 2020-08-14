from datetime import datetime
from uuid import uuid4

from mp.model.metadata import Metadata
from mp.io.writer import metadata_formatter
from mp.io.writer.metadata_formatter import (
    csv_formatter,
    txt_formatter,
    json_formatter,
    formatters,
)


def test_json_formatter_none():
    md = None
    expected = None
    actual = json_formatter(md)
    assert expected == actual


def test_json_formatter_with_conversions():
    uuid = uuid4()
    now = datetime.now()

    expected_id = str(uuid)
    expected_date = now.isoformat()
    expected_date_id = int(now.strftime('%Y%0m%0d'))

    md = Metadata(args={'id': uuid, 'create_date': now})
    expected = '''{
    "id": "%s",
    "owner": null,
    "file_path": null,
    "file_size": 0,
    "create_date": "%s",
    "create_day_id": %d,
    "mime_type": "image/jpeg",
    "image_width": 0,
    "image_height": 0,
    "camera_make": null,
    "camera_model": null,
    "aperture": null,
    "shutter_speed_numerator": 0,
    "shutter_speed_denominator": null,
    "shutter_speed": null,
    "focal_length": 0,
    "focal_length_numerator": 0,
    "focal_length_denominator": null,
    "iso_speed": null,
    "gps_lon": 0,
    "gps_lat": 0,
    "gps_alt": 0,
    "gps_date_time": null,
    "artist": null
}''' % (
        expected_id,
        expected_date,
        expected_date_id,
    )
    actual = json_formatter(md)
    assert expected == actual


def test_json_formatter_no_keys():
    md = Metadata(args={})
    expected = '''{
    "id": null,
    "owner": null,
    "file_path": null,
    "file_size": 0,
    "create_date": null,
    "create_day_id": 0,
    "mime_type": "image/jpeg",
    "image_width": 0,
    "image_height": 0,
    "camera_make": null,
    "camera_model": null,
    "aperture": null,
    "shutter_speed_numerator": 0,
    "shutter_speed_denominator": null,
    "shutter_speed": null,
    "focal_length": 0,
    "focal_length_numerator": 0,
    "focal_length_denominator": null,
    "iso_speed": null,
    "gps_lon": 0,
    "gps_lat": 0,
    "gps_alt": 0,
    "gps_date_time": null,
    "artist": null
}'''
    actual = json_formatter(md)
    assert expected == actual


def test_json_formatter_one_key():
    md = Metadata(args={'owner': 'bbb'})
    expected = '''{
    "id": null,
    "owner": "bbb",
    "file_path": null,
    "file_size": 0,
    "create_date": null,
    "create_day_id": 0,
    "mime_type": "image/jpeg",
    "image_width": 0,
    "image_height": 0,
    "camera_make": null,
    "camera_model": null,
    "aperture": null,
    "shutter_speed_numerator": 0,
    "shutter_speed_denominator": null,
    "shutter_speed": null,
    "focal_length": 0,
    "focal_length_numerator": 0,
    "focal_length_denominator": null,
    "iso_speed": null,
    "gps_lon": 0,
    "gps_lat": 0,
    "gps_alt": 0,
    "gps_date_time": null,
    "artist": null
}'''
    actual = json_formatter(md)
    assert expected == actual


def test_json_formatter_two_keys():
    md = Metadata(args={'owner': 'bbb', 'artist': 'yyy'})
    expected = '''{
    "id": null,
    "owner": "bbb",
    "file_path": null,
    "file_size": 0,
    "create_date": null,
    "create_day_id": 0,
    "mime_type": "image/jpeg",
    "image_width": 0,
    "image_height": 0,
    "camera_make": null,
    "camera_model": null,
    "aperture": null,
    "shutter_speed_numerator": 0,
    "shutter_speed_denominator": null,
    "shutter_speed": null,
    "focal_length": 0,
    "focal_length_numerator": 0,
    "focal_length_denominator": null,
    "iso_speed": null,
    "gps_lon": 0,
    "gps_lat": 0,
    "gps_alt": 0,
    "gps_date_time": null,
    "artist": "yyy"
}'''
    actual = json_formatter(md)
    assert expected == actual


def test_json_formatter_one_key_none_val():
    md = Metadata(args={'owner': None})
    expected = '''{
    "id": null,
    "owner": null,
    "file_path": null,
    "file_size": 0,
    "create_date": null,
    "create_day_id": 0,
    "mime_type": "image/jpeg",
    "image_width": 0,
    "image_height": 0,
    "camera_make": null,
    "camera_model": null,
    "aperture": null,
    "shutter_speed_numerator": 0,
    "shutter_speed_denominator": null,
    "shutter_speed": null,
    "focal_length": 0,
    "focal_length_numerator": 0,
    "focal_length_denominator": null,
    "iso_speed": null,
    "gps_lon": 0,
    "gps_lat": 0,
    "gps_alt": 0,
    "gps_date_time": null,
    "artist": null
}'''
    actual = json_formatter(md)
    assert expected == actual


def test_json_formatter_two_keys_empty_vals():
    md = Metadata(args={'owner': '', 'artist': None})
    expected = '''{
    "id": null,
    "owner": "",
    "file_path": null,
    "file_size": 0,
    "create_date": null,
    "create_day_id": 0,
    "mime_type": "image/jpeg",
    "image_width": 0,
    "image_height": 0,
    "camera_make": null,
    "camera_model": null,
    "aperture": null,
    "shutter_speed_numerator": 0,
    "shutter_speed_denominator": null,
    "shutter_speed": null,
    "focal_length": 0,
    "focal_length_numerator": 0,
    "focal_length_denominator": null,
    "iso_speed": null,
    "gps_lon": 0,
    "gps_lat": 0,
    "gps_alt": 0,
    "gps_date_time": null,
    "artist": null
}'''
    actual = json_formatter(md)
    assert expected == actual


def test_csv_formatter_none():
    md = None
    expected = ''
    actual = csv_formatter(md)
    assert expected == actual


def test_csv_formatter_no_keys():
    md = Metadata(args={})
    expected = '''aperture,artist,camera_make,camera_model,create_date,create_day_id,file_path,file_size,focal_length,focal_length_denominator,focal_length_numerator,gps_alt,gps_date_time,gps_lat,gps_lon,id,image_height,image_width,iso_speed,mime_type,owner,shutter_speed,shutter_speed_denominator,shutter_speed_numerator
,,,,,0,,0,0,,0,0,,0,0,,0,0,,image/jpeg,,,,0
'''
    actual = csv_formatter(md)
    assert expected == actual


def test_csv_formatter_one_key():
    md = Metadata(args={'owner': 'bbb'})
    expected = '''aperture,artist,camera_make,camera_model,create_date,create_day_id,file_path,file_size,focal_length,focal_length_denominator,focal_length_numerator,gps_alt,gps_date_time,gps_lat,gps_lon,id,image_height,image_width,iso_speed,mime_type,owner,shutter_speed,shutter_speed_denominator,shutter_speed_numerator
,,,,,0,,0,0,,0,0,,0,0,,0,0,,image/jpeg,bbb,,,0
'''
    actual = csv_formatter(md)
    assert expected == actual


def test_csv_formatter_two_keys():
    md = Metadata(args={'owner': 'bbb', 'artist': 'yyy'})
    expected = '''aperture,artist,camera_make,camera_model,create_date,create_day_id,file_path,file_size,focal_length,focal_length_denominator,focal_length_numerator,gps_alt,gps_date_time,gps_lat,gps_lon,id,image_height,image_width,iso_speed,mime_type,owner,shutter_speed,shutter_speed_denominator,shutter_speed_numerator
,yyy,,,,0,,0,0,,0,0,,0,0,,0,0,,image/jpeg,bbb,,,0
'''
    actual = csv_formatter(md)
    assert expected == actual


def test_csv_formatter_one_key_none_val():
    md = Metadata(args={'owner': None})
    expected = '''aperture,artist,camera_make,camera_model,create_date,create_day_id,file_path,file_size,focal_length,focal_length_denominator,focal_length_numerator,gps_alt,gps_date_time,gps_lat,gps_lon,id,image_height,image_width,iso_speed,mime_type,owner,shutter_speed,shutter_speed_denominator,shutter_speed_numerator
,,,,,0,,0,0,,0,0,,0,0,,0,0,,image/jpeg,,,,0
'''
    actual = csv_formatter(md)
    assert expected == actual


def test_csv_formatter_two_keys_empty_vals():
    md = Metadata(args={'owner': '', 'artist': None})
    expected = '''aperture,artist,camera_make,camera_model,create_date,create_day_id,file_path,file_size,focal_length,focal_length_denominator,focal_length_numerator,gps_alt,gps_date_time,gps_lat,gps_lon,id,image_height,image_width,iso_speed,mime_type,owner,shutter_speed,shutter_speed_denominator,shutter_speed_numerator
,,,,,0,,0,0,,0,0,,0,0,,0,0,,image/jpeg,,,,0
'''
    actual = csv_formatter(md)
    assert expected == actual


def test_text_formatter_none():
    md = None
    expected = None
    actual = txt_formatter(md)
    assert expected == actual


def test_text_formatter_no_keys():
    md = Metadata(args={})
    expected = '''aperture=None
artist=None
camera_make=None
camera_model=None
create_date=None
create_day_id=0
file_path=None
file_size=0
focal_length=0
focal_length_denominator=None
focal_length_numerator=0
gps_alt=0
gps_date_time=None
gps_lat=0
gps_lon=0
id=None
image_height=0
image_width=0
iso_speed=None
mime_type=image/jpeg
owner=None
shutter_speed=None
shutter_speed_denominator=None
shutter_speed_numerator=0
'''
    actual = txt_formatter(md)
    assert expected == actual


def test_text_formatter_one_key():
    md = Metadata(args={'owner': 'bbb'})
    expected = '''aperture=None
artist=None
camera_make=None
camera_model=None
create_date=None
create_day_id=0
file_path=None
file_size=0
focal_length=0
focal_length_denominator=None
focal_length_numerator=0
gps_alt=0
gps_date_time=None
gps_lat=0
gps_lon=0
id=None
image_height=0
image_width=0
iso_speed=None
mime_type=image/jpeg
owner=bbb
shutter_speed=None
shutter_speed_denominator=None
shutter_speed_numerator=0
'''
    actual = txt_formatter(md)
    assert expected == actual


def test_text_formatter_two_keys():
    md = Metadata(args={'owner': 'bbb', 'artist': 'yyy'})
    expected = '''aperture=None
artist=yyy
camera_make=None
camera_model=None
create_date=None
create_day_id=0
file_path=None
file_size=0
focal_length=0
focal_length_denominator=None
focal_length_numerator=0
gps_alt=0
gps_date_time=None
gps_lat=0
gps_lon=0
id=None
image_height=0
image_width=0
iso_speed=None
mime_type=image/jpeg
owner=bbb
shutter_speed=None
shutter_speed_denominator=None
shutter_speed_numerator=0
'''
    actual = txt_formatter(md)
    assert expected == actual


def test_text_formatter_one_key_none_val():
    md = Metadata(args={'owner': None})
    expected = '''aperture=None
artist=None
camera_make=None
camera_model=None
create_date=None
create_day_id=0
file_path=None
file_size=0
focal_length=0
focal_length_denominator=None
focal_length_numerator=0
gps_alt=0
gps_date_time=None
gps_lat=0
gps_lon=0
id=None
image_height=0
image_width=0
iso_speed=None
mime_type=image/jpeg
owner=None
shutter_speed=None
shutter_speed_denominator=None
shutter_speed_numerator=0
'''
    actual = txt_formatter(md)
    assert expected == actual


def test_text_formatter_two_keys_empty_vals():
    md = Metadata(args={'owner': '', 'artist': None})
    expected = '''aperture=None
artist=None
camera_make=None
camera_model=None
create_date=None
create_day_id=0
file_path=None
file_size=0
focal_length=0
focal_length_denominator=None
focal_length_numerator=0
gps_alt=0
gps_date_time=None
gps_lat=0
gps_lon=0
id=None
image_height=0
image_width=0
iso_speed=None
mime_type=image/jpeg
owner=
shutter_speed=None
shutter_speed_denominator=None
shutter_speed_numerator=0
'''
    actual = txt_formatter(md)
    assert expected == actual


def test_formatter_lookup():
    '''
    Assert that there is a formatter function for each declared format type.
    '''
    for k in formatters:
        assert formatters[k] == getattr(metadata_formatter, f'{k}_formatter')
