from datetime import datetime
from json import dumps
from uuid import UUID


def csv_formatter(data):
    if data and len(data) > 0:
        keys = sorted(data.keys())
        s = ','.join(keys) + '\n'
        for k in keys:
            v = str(data[k]) if data[k] is not None else ''
            s = s + v + ','
        return s[:-1] + '\n'
    else:
        return ''


def txt_formatter(data):
    if data:
        s = ''
        for k in sorted(data.keys()):
            s = s + f'{k}={data[k]}\n'
        return s
    else:
        return None


def json_formatter(data):
    def converter(o):
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()

    if metadata:
        return dumps(data, indent=4, default=converter)


formatters = {
    'csv': csv_formatter,
    'txt': txt_formatter,
    'json': json_formatter,
}
