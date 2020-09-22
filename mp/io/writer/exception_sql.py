from logging import debug


def create():
    debug(f'building processor log create table statement')
    return f'''
    create table if not exists processor_log (
        id varchar primary key,
        owner varchar not null,
        file_path varchar not null,
        error_code varchar not null,
        message varchar not null,
        reason varchar,
        original_file_path varchar
    )
    '''


def insert():
    debug(f'building processor log insert statement')
    return f'''
    insert into processor_log
        id,
        owner,
        file_path,
        error_code,
        message,
        reason,
        original_file_path
    values ?, ?, ?, ?, ?, ?, ?
    '''
