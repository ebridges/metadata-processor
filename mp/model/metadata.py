from uuid import uuid4
from datetime import datetime

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
      Actual aperture value of the lens when the image was taken, in APEX units.
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
        'file_size': 0,
        'create_date': None,
        'create_day_id': 0,
        'mime_type': 'image/jpeg',
        'image_width': 0,
        'image_height': 0,
        'camera_make': None,
        'camera_model': None,
        'aperture': None,
        'shutter_speed_numerator': 0,
        'shutter_speed_denominator': None,
        'shutter_speed': None,
        'focal_length_numerator': 0,
        'focal_length_denominator': None,
        'iso_speed': None,
        'gps_lon': 0,
        'gps_lat': 0,
        'gps_alt': 0,
        'gps_date_time': None,
        'artist': None,
    }

    def __str__(self):
        s = ''
        for k in sorted(dir(self)):
            if not k.startswith('_'):
                v = self.__getattribute__(k)
                s = s + f'{k}={v}\n'
        return s


if __name__ == '__main__':
    args = dict()
    args['create_date'] = datetime.now()
    args['create_day_id'] = create_day_id(args['create_date'])
    md = Metadata(args=args)
    print(md.create_date)
    print(md.create_day_id)
    print(md.mime_type)
    print(md.artist)
    print(str(md))
