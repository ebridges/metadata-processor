from logging import info, debug
from mp import model
from types import ModuleType

POSTGRESQL = 'postgresql'
SQLITE = 'sqlite'

table_name = 'media_item'

_columns = [
    getattr(model, item)
    for item in sorted(dir(model))
    if not item.startswith('__') and not isinstance(getattr(model, item), ModuleType)
]

_sql_types = {
    model.IMAGE_ID: 'uuid',
    model.FILE_PATH: 'varchar',
    model.MIME_TYPE: 'varchar',
    model.OWNER_ID: 'uuid',
    model.APERTURE: 'varchar',
    model.CAMERA_MAKE: 'varchar',
    model.CAMERA_MODEL: 'varchar',
    model.CREATE_DATE: 'timestamp without time zone',
    model.CREATE_DAY_ID: 'integer',
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


def create():
    column_decls = ', '.join([f'{k} {v}' for k, v in _sql_types.items()])
    return f'create table if not exists {table_name} ({column_decls})'


def insert(dbtype=POSTGRESQL):
    debug(f'building insert statement for {dbtype}')
    column_list = ', '.join(_columns)
    if dbtype == POSTGRESQL:
        value_list = ', '.join([f'%({item})s' for item in _columns])
        return f'insert into {table_name} ({column_list}) values ({value_list}) returning id'
    elif dbtype == SQLITE:
        value_list = ', '.join([f':{item}' for item in _columns])
        return f'insert into {table_name} ({column_list}) values ({value_list})'
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')


def update(dbtype=POSTGRESQL):
    debug(f'building update statement for {dbtype}')
    placeholder = '%s' if dbtype == POSTGRESQL else '?'
    cols = [c for c in _columns if not c == model.IMAGE_ID]
    if dbtype == POSTGRESQL:
        update_pairs = ', '.join([f'{item} = %({item})s' for item in cols])
        id_placeholder = f'%({model.IMAGE_ID})s'
        return f'update {table_name} set {update_pairs} where {model.IMAGE_ID} = {id_placeholder} returning id'
    elif dbtype == SQLITE:
        update_pairs = ', '.join([f'{item} = :{item}' for item in cols])
        id_placeholder = f':{model.IMAGE_ID}'
        return f'update {table_name} set {update_pairs} where {model.IMAGE_ID} = {id_placeholder}'
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')


def delete(dbtype=POSTGRESQL):
    debug(f'building delete statement for {dbtype}')
    if dbtype == POSTGRESQL:
        id_placeholder = f'%({model.IMAGE_ID})s'
        return f'delete from {table_name} where {model.IMAGE_ID} = {id_placeholder} returning id'
    elif dbtype == SQLITE:
        id_placeholder = f':{model.IMAGE_ID}'
        return f'delete from {table_name} where {model.IMAGE_ID} = {id_placeholder}'
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')


def exists(dbtype=POSTGRESQL):
    debug(f'building exists statement for {dbtype}')
    if dbtype == POSTGRESQL:
        path_placeholder = f'%({model.FILE_PATH})s'
    elif dbtype == SQLITE:
        path_placeholder = f':{model.FILE_PATH}'
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')

    return f'select 1 from {table_name} where {model.FILE_PATH} = {path_placeholder}'
