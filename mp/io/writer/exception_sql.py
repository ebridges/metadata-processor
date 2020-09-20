from logging import debug

from mp.io.writer import POSTGRESQL, SQLITE


def create():
    column_decls = ', '.join([f'{k} {v}' for k, v in _sql_types.items()])
    return f'''
        create table if not exists processor_log (
            id uuid primary key,
            owner uuid not null,
            file_path varchar not null,
            error_code varchar not null,
            message varchar not null,
            reason varchar,
            original_file_path varchar
        )
    '''


def insert(dbtype=POSTGRESQL):
    debug(f'building processor log insert statement for {dbtype}')
    if dbtype == POSTGRESQL:
        return f'''
        insert into processor_log
            id,
            owner,
            file_path,
            error_code,
            message,
            reason,
            original_file_path
        values
            %(id)s,
            %(owner)s,
            %(file_path)s,
            %(error_code)s,
            %(message)s,
            %(reason)s,
            %(original_file_path)s
        '''
    elif dbtype == SQLITE:
        return f'''
        insert into processor_log
            id,
            owner,
            file_path,
            error_code,
            message,
            reason,
            original_file_path
        values
            :id,
            :owner,
            :file_path,
            :error_code,
            :message,
            :reason,
            :original_file_path
        '''
    else:
        raise ValueError(f'unrecognized database type: [{dbtype}]')
