from datetime import timezone
from pathlib import Path
from fractions import Fraction

from pyexiv2 import Image, set_log_level

from mp.model import *
from mp.io.metadata_tags import *
from mp.model.metadata import Metadata
from mp.model.utils import parse_date

log_levels = {
    'debug': 0,
    'info': 1,
    'warn': 2,
    'error': 3,
    'mute': 4,
}


def extract_metadata(image_key, image_file, verbose=False):
    log_level = 'debug' if verbose else 'warn'
    md = {
        IMAGE_ID: image_key.image_id,
        OWNER_ID: image_key.owner_id,
        FILE_PATH: image_key.file_path,
        FILE_SIZE: Path(image_file).stat().st_size,
        MIME_TYPE: image_key.mime_type,
    }
    with Image(image_file) as img:
        set_log_level(log_levels[log_level])
        exif = img.read_exif()

        cd = extract_createdate_exif(exif)
        if not cd:
            xmp = img.read_xmp()
            cd = extract_createdate_xmp(xmp)
        if not cd:
            raise ValueError(f'unable to read create date from {image_file}')
        md[CREATE_DATE] = cd

        md[ARTIST] = resolve_str(exif, [TAG_IMAGE_ARTIST])
        md[CAMERA_MAKE] = resolve_str(exif, [TAG_IMAGE_MAKE])
        md[CAMERA_MODEL] = resolve_str(exif, [TAG_IMAGE_MODEL])
        md[ISO_SPEED] = resolve_int(exif, [TAG_PHOTO_ISOSPEEDRATINGS])

        md[APERTURE] = extract_aperture(exif)

        ss = extract_shutter_speed(exif)
        (md[SHUTTER_SPEED], md[SHUTTER_SPEED_N], md[SHUTTER_SPEED_D]) = ss

        ff = extract_focal_length(exif)
        md[FOCAL_LENGTH], md[FOCAL_LENGTH_N], md[FOCAL_LENGTH_D] = ff

        dd = extract_dimensions(exif)
        md[IMAGE_WIDTH], md[IMAGE_HEIGHT] = dd

        gps = extract_gps_coords(exif)
        md[GPS_LAT], md[GPS_LON], md[GPS_ALT] = gps

        md[GPS_DATE_TIME] = extract_gps_datetime(exif)

    return Metadata(args=md)


def extract_gps_coords(md):
    lat = extract_gps_degrees(md, [TAG_GPSINFO_GPSLATITUDE])
    lat_ref = resolve_str(md, [TAG_GPSINFO_GPSLATITUDEREF])
    if lat_ref != 'N':
        lat = 0 - lat

    lon = extract_gps_degrees(md, [TAG_GPSINFO_GPSLONGITUDE])
    lon_ref = resolve_str(md, [TAG_GPSINFO_GPSLONGITUDEREF])
    if lon_ref != 'E':
        lon = 0 - lon

    r = resolve_rational(resolve_str(md, [TAG_GPSINFO_GPSALTITUDE]))
    alt = rational_to_float(r, 2)

    return lat, lon, alt


def extract_focal_length(md):
    f = resolve_str(md, [TAG_PHOTO_FOCALLENGTHIN35MMFILM])
    fl = resolve_str(md, [TAG_PHOTO_FOCALLENGTH])
    r = resolve_rational(fl)
    if f and r:
        return (f'{f}mm',) + r
    else:
        return (None, None, None)


def extract_shutter_speed(md):
    v = resolve_str(md, [TAG_PHOTO_SHUTTERSPEEDVALUE])
    r = resolve_rational(v)
    f = rational_to_float(r)
    ss = apex_to_shutterspeed(f)
    if ss and r:
        return f'{ss[0]}/{ss[1]} sec', r[0], r[1]
    else:
        return (None, None, None)


def extract_aperture(md):
    v = resolve_str(md, [TAG_PHOTO_APERTUREVALUE])
    r = resolve_rational(v)
    f = rational_to_float(r)
    a = apex_to_aperture(f)
    return f'f/{a}'


def extract_dimensions(md):
    w_keys = [
        TAG_IMAGE_IMAGEWIDTH,
        TAG_PHOTO_PIXELXDIMENSION,
    ]
    width = resolve_int(md, w_keys)
    h_keys = [
        TAG_IMAGE_IMAGELENGTH,
        TAG_PHOTO_PIXELYDIMENSION,
    ]
    height = resolve_int(md, h_keys)
    return width, height


def extract_createdate_exif(md):
    keys = [
        TAG_PHOTO_DATETIMEDIGITIZED,
        TAG_PHOTO_DATETIMEORIGINAL,
        TAG_IMAGE_DATETIME,
    ]
    dt = resolve_str(md, keys)
    return parse_date(dt)


def extract_createdate_xmp(md):
    keys = [
        'Xmp.xmp.CreateDate',
    ]
    dt = resolve_str(md, keys)

    # XMP Create Date includes a TZ, but we remove
    # it to conform with EXIF create dates, which do
    # not include it
    return parse_date(dt)


def extract_gps_datetime(md):
    dt = extract_gps_date(md)
    ti = extract_gps_time(md)
    date = f'{dt} {ti}'
    return parse_date(date, tz=timezone.utc)


def extract_gps_date(md):
    v = resolve_str(md, [TAG_GPSINFO_GPSDATESTAMP])
    return v.replace(' ', '') if v else None


def extract_gps_time(md):
    v = resolve_str(md, [TAG_GPSINFO_GPSTIMESTAMP])
    if v:
        time = []
        for vv in v.split(' '):
            f = rational_to_float(resolve_rational(vv), 0)
            time.append(f) if f else None
        return ':'.join(['%02d' % t for t in time])


def extract_gps_degrees(md, keys):
    v = resolve_str(md, keys)
    dms = []
    if v:
        for vv in v.split(' '):
            f = rational_to_float(resolve_rational(vv), 10)
            dms.append(f)
        return dms[0] + (dms[1] / 60.0) + (dms[2] / 3600.0)
    else:
        return 0


def resolve_str(md, keys):
    '''Pulls the first value in md that matches a one of the given keys'''
    for key in keys:
        if key in md and md.get(key):
            return md[key]


def resolve_int(md, keys):
    v = resolve_str(md, keys)
    return int(v) if v else None


def resolve_rational(v):
    return tuple([int(vv) for vv in v.split('/')]) if v else (None, None)


def apex_to_aperture(v):
    return round(pow(2, v / 2), 1) if v else None


def apex_to_shutterspeed(v):
    if v:
        p = round(pow(2, -v), 4)
        f = Fraction(p).limit_denominator(100)
        return (f.numerator, f.denominator)


def rational_to_float(v, p=1):
    if any(map(lambda x: x is None, v)):
        return None
    if not v[1]:
        return 0
    return round(v[0] / v[1], p)
