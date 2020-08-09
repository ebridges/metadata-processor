from uuid import uuid4
from datetime import datetime

from mp.model import *
from mp.util.objects import properties, self_properties


def create_day_id(dt):
    '''converts a datetime object to yyyymmdd:int'''
    if dt:
        date = dt.strftime('%Y%0m%0d')
        return int(date)
    return None


class Metadata:
    '''
    https://mnesarco.github.io/blog/2020/07/23/python-metaprogramming-properties-on-steroids
    '''

    def __init__(self, args):
        _args = dict(Metadata._defaults, **args)
        self_properties(self, scope=_args)

    with properties(locals(), 'meta') as meta:

        @meta.prop(read_only=True)
        def id(self) -> uuid4:
            '''Required: Primary Key'''

        @meta.prop(read_only=True)
        def owner(self) -> uuid4:
            '''Required: Account that owns this image'''

        @meta.prop(read_only=True)
        def file_path(self) -> str:
            '''Required: Path on the filesystem to this image.'''

        @meta.prop(read_only=True)
        def file_size(self) -> int:
            '''Size of the image in bytes.'''

        @meta.prop(read_only=True)
        def create_date(self) -> datetime:
            '''Date & time when image was created, without timezone'''

        @meta.prop(read_only=True)
        def create_day_id(self) -> int:
            '''Id of the create day.'''
            if self._create_date:
                self._create_day_id = create_day_id(self._create_date)

        @meta.prop(read_only=True)
        def mime_type(self) -> str:
            '''Mime type of the image.'''

        @meta.prop(read_only=True)
        def image_width(self) -> int:
            '''Width of the image'''

        @meta.prop(read_only=True)
        def image_height(self) -> int:
            '''Width of the image'''

        @meta.prop(read_only=True)
        def camera_make(self) -> str:
            '''Make of the camera that made this image.'''

        @meta.prop(read_only=True)
        def camera_model(self) -> str:
            '''Model of the camera that made this image.'''

        @meta.prop(read_only=True)
        def aperture(self) -> str:
            '''
            Actual aperture value of the lens when the image was taken, converted from APEX units.
            https://photo.stackexchange.com/a/60950/1789
            '''

        @meta.prop(read_only=True)
        def shutter_speed_numerator(self) -> int:
            '''Numerator of the shutter speed.'''

        @meta.prop(read_only=True)
        def shutter_speed_denominator(self) -> int:
            '''Denominator of the shutter speed.'''

        @meta.prop(read_only=True)
        def shutter_speed(self) -> str:
            '''Shutter speed expressed as a fractional value'''

        @meta.prop(read_only=True)
        def focal_length(self) -> int:
            '''Focal length used by camera when image created.'''

        @meta.prop(read_only=True)
        def focal_length_numerator(self) -> int:
            '''Numerator of the focal length.'''

        @meta.prop(read_only=True)
        def focal_length_denominator(self) -> int:
            '''Denominator of the focal length.'''

        @meta.prop(read_only=True)
        def iso_speed(self) -> int:
            '''ISO Speed of the image's exposure.'''

        @meta.prop(read_only=True)
        def gps_lon(self) -> float:
            '''Longitude of location where image was created.'''

        @meta.prop(read_only=True)
        def gps_lat(self) -> float:
            '''Latitude of location where image was created.'''

        @meta.prop(read_only=True)
        def gps_alt(self) -> float:
            '''Altitude of location where image was created.'''

        @meta.prop(read_only=True)
        def gps_date_time(self) -> datetime:
            '''Date & time (with TZ) at location where image was created.'''

        @meta.prop(read_only=True)
        def artist(self) -> str:
            '''Name of the individual who owns this image.'''

    _defaults = {
        FILE_SIZE: 0,
        CREATE_DATE: None,
        CREATE_DAY_ID: 0,
        MIME_TYPE: 'image/jpeg',
        IMAGE_WIDTH: 0,
        IMAGE_HEIGHT: 0,
        CAMERA_MAKE: None,
        CAMERA_MODEL: None,
        APERTURE: None,
        SHUTTER_SPEED_NUMERATOR: 0,
        SHUTTER_SPEED_DENOMINATOR: None,
        SHUTTER_SPEED: None,
        FOCAL_LENGTH: 0,
        FOCAL_LENGTH_NUMERATOR: 0,
        FOCAL_LENGTH_DENOMINATOR: None,
        ISO_SPEED: None,
        GPS_LON: 0,
        GPS_LAT: 0,
        GPS_ALT: 0,
        GPS_DATE_TIME: None,
        ARTIST: None,
    }

    def __str__(self):
        s = ''
        for k in sorted(dir(self)):
            if not k.startswith('_'):
                v = self.__getattribute__(k)
                s = s + f'{k}={v}\n'
        return s

    def __eq__(self, other):
        if not isinstance(other, Metadata):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return (
            self.id == other.id
            and self.owner == other.owner
            and self.file_path == other.file_path
            and self.file_size == other.file_size
            and self.create_date == other.create_date
            and self.create_day_id == other.create_day_id
            and self.mime_type == other.mime_type
            and self.image_width == other.image_width
            and self.image_height == other.image_height
            and self.camera_make == other.camera_make
            and self.camera_model == other.camera_model
            and self.aperture == other.aperture
            and self.shutter_speed_numerator == other.shutter_speed_numerator
            and self.shutter_speed_denominator == other.shutter_speed_denominator
            and self.shutter_speed == other.shutter_speed
            and self.focal_length == other.focal_length
            and self.focal_length_numerator == other.focal_length_numerator
            and self.focal_length_denominator == other.focal_length_denominator
            and self.iso_speed == other.iso_speed
            and self.gps_lon == other.gps_lon
            and self.gps_lat == other.gps_lat
            and self.gps_alt == other.gps_alt
            and self.gps_date_time == other.gps_date_time
            and self.artist == other.artist
        )
