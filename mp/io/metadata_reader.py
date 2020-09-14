from logging import warning, debug
from datetime import timezone
from pathlib import Path
from fractions import Fraction

from PIL.Image import open as pillow_open
from PIL.ExifTags import TAGS
from lxml import etree

from mp.model import *
from mp.io.metadata_tags import *
from mp.model.metadata import Metadata
from mp.model.utils import parse_date


def extract_metadata(image_key, image_file):
    md = {
        IMAGE_ID: image_key.image_id,
        OWNER_ID: image_key.owner_id,
        FILE_PATH: image_key.file_path,
        FILE_SIZE: Path(image_file).stat().st_size,
        MIME_TYPE: image_key.mime_type,
    }

    with pillow_open(image_file) as img:
        dic = img._getexif() or {}
        exif = {TAGS.get(k): v for k, v in dic.items()}

        cd = extract_createdate_exif(exif)
        if not cd:
            warning(f'No create date in EXIF metadata of {image_key}, using XMP.')
            cd = extract_createdate_xmp(img, image_key)
        if not cd:
            raise ValueError(f'unable to read create date from {image_file}')
        debug(f'Found create date {cd} for image {image_key}')
        md[CREATE_DATE] = cd

        md[ARTIST] = resolve_val(exif, [TAG_IMAGE_ARTIST])
        md[CAMERA_MAKE] = resolve_val(exif, [TAG_IMAGE_MAKE])
        md[CAMERA_MODEL] = resolve_val(exif, [TAG_IMAGE_MODEL])
        md[ISO_SPEED] = resolve_val(exif, [TAG_PHOTO_ISOSPEEDRATINGS])

        md[APERTURE] = extract_aperture(exif)

        ss = extract_shutter_speed(exif)
        (md[SHUTTER_SPEED], md[SHUTTER_SPEED_N], md[SHUTTER_SPEED_D]) = ss

        ff = extract_focal_length(exif)
        md[FOCAL_LENGTH], md[FOCAL_LENGTH_N], md[FOCAL_LENGTH_D] = ff

        md[IMAGE_WIDTH], md[IMAGE_HEIGHT] = img.size

        gps = extract_gps_coords(exif)
        md[GPS_LAT], md[GPS_LON], md[GPS_ALT], md[GPS_DATE_TIME] = gps

    debug(f'Metadata for {image_key}: {md}')
    return Metadata(args=md)


def extract_createdate_exif(md):
    keys = [
        TAG_PHOTO_DATETIMEDIGITIZED,
        TAG_PHOTO_DATETIMEORIGINAL,
        TAG_IMAGE_DATETIME,
    ]
    dt = resolve_val(md, keys)
    return parse_date(dt)


def extract_createdate_xmp(image, image_key):
    for segment, content in image.applist:
        try:
            marker, body = content.decode('utf-8').split('\x00', 1)
        except:
            continue
        if segment == 'APP1' and marker == 'http://ns.adobe.com/xap/1.0/':
            try:
                create_date_xpath = '//@xmp:CreateDate'
                xml = etree.fromstring(body)
                date = xml.xpath(
                    '//@xmp:CreateDate',
                    namespaces={'xmp': 'http://ns.adobe.com/xap/1.0/'},
                )
                if date and len(date) > 0:
                    # XMP Create Date includes a TZ, but we remove
                    # it to conform with EXIF create dates, which do
                    # not include it
                    return parse_date(date[0])
            except Exception as e:
                warning(f'Exception with image [{image_key}] parsing XMP XML: {e}')


def extract_focal_length(md):
    f = resolve_val(md, [TAG_PHOTO_FOCALLENGTHIN35MMFILM])
    r = resolve_val(md, [TAG_PHOTO_FOCALLENGTH])
    if f and r:
        return f'{f}mm', r.numerator, r.denominator
    else:
        return (None, None, None)


def extract_shutter_speed(md):
    v = resolve_val(md, [TAG_PHOTO_SHUTTERSPEEDVALUE])
    ss = apex_to_shutterspeed(v)
    if ss and v:
        return f'{ss[0]}/{ss[1]} sec', v.numerator, v.denominator
    else:
        return (None, None, None)


def extract_aperture(md):
    v = resolve_val(md, [TAG_PHOTO_APERTUREVALUE])
    a = apex_to_aperture(v)
    if v:
        return f'f/{a}'


def extract_gps_coords(md):
    gps_md = md.get(TAG_GPSINFO)

    if not gps_md:
        return None, None, None, None

    dt = extract_gps_datetime(gps_md)

    lat = extract_gps_degrees(gps_md, [TAG_GPSINFO_GPSLATITUDE])
    if lat:
        lat_ref = resolve_val(gps_md, [TAG_GPSINFO_GPSLATITUDEREF])
        if lat_ref != 'N':
            lat = 0 - lat

    lon = extract_gps_degrees(gps_md, [TAG_GPSINFO_GPSLONGITUDE])
    if lon:
        lon_ref = resolve_val(gps_md, [TAG_GPSINFO_GPSLONGITUDEREF])
        if lon_ref != 'E':
            lon = 0 - lon

    alt = resolve_val(gps_md, [TAG_GPSINFO_GPSALTITUDE])

    return lat, lon, alt, dt


def extract_gps_degrees(md, keys):
    v = resolve_tuple(md, keys)
    if v:
        return v[0] + (v[1] / 60.0) + (v[2] / 3600.0)


def extract_gps_datetime(md):
    dt = extract_gps_date(md)
    ti = extract_gps_time(md)
    if dt and ti:
        date = f'{dt} {ti}'
        return parse_date(date, tz=timezone.utc)


def extract_gps_date(md):
    v = resolve_val(md, [TAG_GPSINFO_GPSDATESTAMP])
    return v.replace(' ', '') if v else None


def extract_gps_time(md):
    v = resolve_tuple_int(md, [TAG_GPSINFO_GPSTIMESTAMP])
    if v:
        return ':'.join(['%02d' % t for t in v])


def resolve_tuple_int(md, keys):
    v = resolve_tuple(md, keys)
    if v:
        return tuple(map(int, v))


def resolve_tuple(md, keys):
    v = resolve_val(md, keys)
    return v if type(v) in [list, tuple] else None


def resolve_val(md, keys):
    for key in keys:
        if key in md:
            return md[key]


def apex_to_aperture(v):
    return round(pow(2, v / 2), 1) if v else None


def apex_to_shutterspeed(v):
    if v:
        p = round(pow(2, -v), 4)
        f = Fraction(p).limit_denominator(100)
        return (f.numerator, f.denominator)
