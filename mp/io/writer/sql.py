from mp import model
from mp.model import *

__sql_types = {
    IMAGE_ID: 'uuid',
    FILE_PATH: 'varchar',
    MIME_TYPE: 'varchar',
    OWNER_ID: 'uuid',
    APERTURE: 'varchar',
    CAMERA_MAKE: 'varchar',
    CAMERA_MODEL: 'varchar',
    CREATE_DATE: 'timestamp without time zone',
    CREATE_DAY_ID: 'integer',
    FILE_SIZE: 'bigint',
    FOCAL_LENGTH: 'varchar',
    FOCAL_LENGTH_N: 'integer',
    FOCAL_LENGTH_D: 'integer',
    GPS_ALT: 'double precision',
    GPS_DATE_TIME: 'timestamp with time zone',
    GPS_LAT: 'double precision',
    GPS_LON: 'double precision',
    ARTIST: 'varchar',
    SHUTTER_SPEED: 'varchar',
    IMAGE_HEIGHT: 'integer',
    IMAGE_WIDTH: 'integer',
    ISO_SPEED: 'integer',
    SHUTTER_SPEED_D: 'integer',
    SHUTTER_SPEED_N: 'integer',
}

table_name = 'media_item'

_columns = [
    getattr(model, item) for item in sorted(dir(model)) if not item.startswith('__')
]
_values = [f'%({item})s' for item in _columns]

column_list = ', '.join(_columns)
value_list = ', '.join(_values)
insert = f'insert into {table_name} ({column_list}) values ({value_list})'

update_pairs = ', '.join(
    [
        f'{pair[0]} = {pair[1]}'
        for pair in zip(
            [c for c in _columns if not c == IMAGE_ID],
            [v for v in _values if not v == '%({IMAGE_ID})s'],
        )
    ]
)
update = f'update {table_name} set {update_pairs} where {IMAGE_ID} = %({IMAGE_ID})s'

delete = f'delete from {table_name} where {FILE_PATH} = %({FILE_PATH})s'

exists = f'select 1 from {table_name} where {FILE_PATH} = %({FILE_PATH})s'
