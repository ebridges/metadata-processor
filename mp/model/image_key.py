from re import match, IGNORECASE
from uuid import uuid4

V4_UUID = '[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[89AB][0-9A-F]{3}-[0-9A-F]{12}'
EXT = '[a-z]{3,4}'
IMAGE_KEY_PATTERN = f'^(?P<uid>{V4_UUID})/(?P<iid>{V4_UUID}).(?P<ext>{EXT})$'


MIME_TYPES = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
}


def parse(path):
    m = match(IMAGE_KEY_PATTERN, path, IGNORECASE)
    if m:
        uid = m.group('uid')
        iid = m.group('iid')
        ext = m.group('ext')
        return uid, iid, ext
    else:
        raise ValueError(f'image key in unexpected format: {path}')


class ImageKey:
    def __init__(self, path):
        (self._owner_id, self._image_id, self._extension) = parse(path)
        self._filename = f'{self.image_id}.{self.extension}'

    @property
    def owner_id(self) -> uuid4:
        return self._owner_id

    @property
    def image_id(self) -> uuid4:
        return self._image_id

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def file_path(self) -> str:
        return f'{self._owner_id}/{self._filename}'

    @property
    def mime_type(self) -> str:
        mt = MIME_TYPES.get(self.extension)
        if not mt:
            raise ValueError(f'unsupported file extension: {self.extension}')
        return mt

    def __str__(self):
        return self.file_path
