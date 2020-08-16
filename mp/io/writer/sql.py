from logging import info, debug
from mp import model
from types import ModuleType

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


def insert(dbtype='postgres'):
    debug(f'building insert statement for {dbtype}')
    column_list = ', '.join(_columns)
    if dbtype == 'postgres':
        value_list = ', '.join([f'%({item})s' for item in _columns])
    elif dbtype == 'sqlite':
        value_list = ', '.join([f':{item}' for item in _columns])
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')

    return f'insert into {table_name} ({column_list}) values ({value_list})'


def update(dbtype='postgres'):
    debug(f'building update statement for {dbtype}')
    placeholder = '%s' if dbtype == 'postgres' else '?'
    cols = [c for c in _columns if not c == model.IMAGE_ID]
    if dbtype == 'postgres':
        update_pairs = ', '.join([f'{item} = %({item})s' for item in cols])
        image_id_placeholder = f'%({model.IMAGE_ID})s'
    elif dbtype == 'sqlite':
        update_pairs = ', '.join([f'{item} = :{item}' for item in cols])
        image_id_placeholder = f':{model.IMAGE_ID}'
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')
    return f'update {table_name} set {update_pairs} where {model.IMAGE_ID} = {image_id_placeholder}'


def delete(dbtype='postgres'):
    debug(f'building delete statement for {dbtype}')
    if dbtype == 'postgres':
        image_id_placeholder = f'%({model.IMAGE_ID})s'
    elif dbtype == 'sqlite':
        image_id_placeholder = f':{model.IMAGE_ID}'
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')

    return f'delete from {table_name} where {model.IMAGE_ID} = {image_id_placeholder}'


def exists(dbtype='postgres'):
    debug(f'building exists statement for {dbtype}')
    if dbtype == 'postgres':
        path_placeholder = f'%({model.FILE_PATH})s'
    elif dbtype == 'sqlite':
        path_placeholder = f':{model.FILE_PATH}'
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')

    return f'select 1 from {table_name} where {model.FILE_PATH} = {path_placeholder}'
