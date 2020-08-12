from datetime import datetime
from json import dumps
from uuid import UUID


def csv_formatter(metadata):
    if metadata and len(metadata.dict()) > 0:
        d = metadata.dict()
        keys = sorted(d.keys())
        s = ','.join(keys) + '\n'
        for k in keys:
            v = str(d[k]) if d[k] is not None else ''
            s = s + v + ','
        return s[:-1] + '\n'
    else:
        return ''


def text_formatter(metadata):
    if metadata:
        d = metadata.dict()
        s = ''
        for k in sorted(d.keys()):
            s = s + f'{k}={d[k]}\n'
        return s
    else:
        return None


def json_formatter(metadata):
    def converter(o):
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()

    if metadata:
        return dumps(metadata.dict(), indent=4, default=converter)


formatters = {
    'csv': csv_formatter,
    'text': text_formatter,
    'json': json_formatter,
}
