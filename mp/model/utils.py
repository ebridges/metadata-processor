from datetime import datetime


def parse_date(d, tz=None):
    '''Try a bunch of formats until we succeed in parsing the date, else return None'''
    date_patterns = [
        '%Y: %m: %d %H: %M: %S',  # bug in pyexiv2 renders in this format
        '%Y:%m:%d %H:%M:%S',
        '%Y:%m:%d %H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y.%m.%d %H:%M:%S',
        '%Y.%m.%d %H:%M',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M%z',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d',
        '%Y-%m',
        '%Y%m%d',
        '%Y',
    ]
    if d:
        for dp in date_patterns:
            try:
                dt = datetime.strptime(d, dp)
                # when tz is None, force to tz unaware
                return dt.replace(tzinfo=tz)
            except ValueError:
                pass
