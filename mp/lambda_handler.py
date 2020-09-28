import logging
import os
import sys

import sentry_sdk

from mp import version, TRIGGER_ERROR, SOURCE_BUCKET
from mp.io.loader import s3_loader
from mp import lambda_common
from mp.util import tools

lambda_common.init_monitoring()


def handler(event, context={}):
    tools.configure_logging()
    logging.info(f'mp v{version}')
    logging.debug(event)

    force_update = lambda_common.check_force_update(event)

    with sentry_sdk.configure_scope() as scope:
        logging.info(f'Scope {scope} configured.')
        scope.set_extra('processor_event', event)
        scope.set_tag('force_update', force_update)
    
        if os.environ.get(TRIGGER_ERROR):
            scope.set_tag(TRIGGER_ERROR, os.environ.get(TRIGGER_ERROR))
            raise Exception('test event')

        event_type = get_event_type(event)

        logging.info(f'handling event of type {event_type}')
        if event_type == 's3':
            return s3_handler(event, scope, context, force_update)

        elif event_type == 'api':
            return api_handler(event, scope, context, force_update)

        else:
            raise Exception('unrecognized event')


def get_event_type(event):
    if not event:
        return None
    if event.get('path'):
        return 'api'
    if event.get('Records'):
        return 's3'


def s3_handler(event, scope, context={}, force_update=False):
    logging.debug('s3_handler called.')
    keys = lambda_common.extract_image_keys_from_s3_event(event)

    writer = lambda_common.init_metadata_writer()
    x_cnt = 0
    for key in keys:
        try:
            scope.set_tag('image_key', key.file_path)
            scope.set_tag('owner_id', key.owner_id)
            scope.set_tag('image_id', key.image_id)

            if not s3_loader.key_exists(key.file_path):
                bucket = os.environ.get(SOURCE_BUCKET)
                logging.info(f'NOT FOUND: {key} not found in bucket: {bucket}.')
                continue

            with writer:
                exists_in_db = writer.exists(key.file_path)
                logging.info(f'Data in db {exists_in_db}, force: {force_update}')
                if not exists_in_db or (exists_in_db and force_update):
                    logging.info(f'Extracting and writing metadata to db for {key}')
                    result = lambda_common.write_metadata(writer, key)
                    if result:
                        logging.info(f'result: {result}')
        except:
            x_cnt = x_cnt + 1
            x_writer = lambda_common.init_exception_writer()
            lambda_common.write_exception_event(x_writer, key, sys.exc_info())
    sz = len(keys)
    logging.info(f'OK: Processing of {sz} record(s) completed with {x_cnt} errors')


def api_handler(event, scope, context={}, force_update=False):
    logging.info('api_handler called.')
    key = lambda_common.extract_image_key_from_apig_event(event)
    if not key:
        return lambda_common.generate_json_response(
            f'key path not found in event.', sc=404
        )

    scope.set_tag('image_key', key.file_path)
    scope.set_tag('owner_id', key.owner_id)
    scope.set_tag('image_id', key.image_id)

    if not s3_loader.key_exists(key.file_path):
        logging.info(f'key does not exist {key}')
        return lambda_common.generate_json_response(f'{key} not found.', sc=404)

    writer = lambda_common.init_metadata_writer()
    with writer:
        exists_in_db = writer.exists(key.file_path)
        if not exists_in_db or (exists_in_db and force_update):
            logging.info('going to extract and write metadata to db')
            lambda_common.write_metadata(writer, key)
            return lambda_common.generate_json_response(f'{key} processed.')
        else:
            logging.info('skip writing metadata to db')
            return lambda_common.generate_json_response(f'{key} not processed.', sc=204)
