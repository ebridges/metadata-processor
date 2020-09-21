from logging import info, debug
from types import ModuleType

table_name = 'media_item'

_columns = [
    getattr(model, item)
    for item in sorted(dir(model))
    if not item.startswith('__') and not isinstance(getattr(model, item), ModuleType)
]

from mp.io.writer import DUCKDB, POSTGRESQL

_sql_types = {
    model.IMAGE_ID: 'uuid primary key',
    model.FILE_PATH: 'varchar unique not null',
    model.MIME_TYPE: 'varchar not null',
    model.OWNER_ID: 'uuid not null',
    model.APERTURE: 'varchar',
    model.CAMERA_MAKE: 'varchar',
    model.CAMERA_MODEL: 'varchar',
    model.CREATE_DATE: 'timestamp without time zone not null',
    model.CREATE_DAY_ID: 'integer not null',
    model.FILE_SIZE: 'bigint',
    model.FOCAL_LENGTH: 'varchar',
    model.FOCAL_LENGTH_N: 'integer',
    model.FOCAL_LENGTH_D: 'integer',
    model.GPS_ALT: 'double precision',
    model.GPS_DATE_TIME: 'timestamp with time zone',
    model.GPS_LAT: 'double precision',
    model.GPS_LON: 'double precision',
    model.ARTIST: 'varchar',
    model.SHUTTER_SPEED: 'varchar',
    model.IMAGE_HEIGHT: 'integer',
    model.IMAGE_WIDTH: 'integer',
    model.ISO_SPEED: 'integer',
    model.SHUTTER_SPEED_D: 'integer',
    model.SHUTTER_SPEED_N: 'integer',
}


def create(dbtype=DUCKDB):
    if dbtype == DUCKDB:
        # some data types not yet supported by duckdb
        _sql_types[model.IMAGE_ID] = 'varchar primary key'
        _sql_types[model.OWNER_ID] = 'varchar not null'
        _sql_types[model.GPS_DATE_TIME] = 'timestamp'
    column_decls = ', '.join([f'{k} {v}' for k, v in _sql_types.items()])
    return f'create table if not exists {table_name} ({column_decls})'


def insert():
    debug(f'building insert statement')
    cols = ', '.join(_columns)
    vals = ('?, ' * len(_columns)).rstrip().rstrip(',')
    return f'insert into {table_name} ({cols}) values ({vals}) returning id'


def update():
    debug(f'building update statement')
    update_pairs = ', '.join([f'{c} = ?' for c in _columns if not c == model.IMAGE_ID])
    return f'update {table_name} set {update_pairs} where {model.IMAGE_ID} = ? returning id'


def delete():
    debug(f'building delete statement')
    return f'delete from {table_name} where {model.IMAGE_ID} = ? returning id'


def exists():
    debug(f'building exists statement')
    return f'select 1 from {table_name} where {model.FILE_PATH} = ?'
