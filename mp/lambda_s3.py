import logging
import os

import sentry_sdk

from mp import version, TRIGGER_ERROR, SOURCE_BUCKET
from mp.io.loader import s3_loader
from mp import lambda_common
from mp.util import tools


def s3_handler(event, context={}):
    tools.configure_logging()
    logging.info(f'mp v{version}')
    logging.debug(event)

    lambda_common.init_monitoring()
    with sentry_sdk.configure_scope() as scope:
        scope.set_extra('processor_event', event)

        if os.environ.get(TRIGGER_ERROR):
            raise Exception('test event')

        keys = lambda_common.extract_image_keys_from_s3_event(event)

        force_update = lambda_common.check_force_update(event)
        scope.set_tag('force_update', force_update)

        writer = lambda_common.init_writer()
        for key in keys:
            scope.set_tag('image_key', key.file_path)
            scope.set_tag('owner_id', key.owner_id)
            scope.set_tag('image_id', key.image_id)

            if not s3_loader.key_exists(key.file_path):
                bucket = os.environ.get(SOURCE_BUCKET)
                logging.info(f'{key} not found in bucket: {bucket}.')
                continue

            with writer:
                exists_in_db = writer.exists(key.file_path)
                if not exists_in_db or (exists_in_db and force_update):
                    result = lambda_common.write_metadata(key, writer)
                    if result:
                        logging.info(f'result: {result}')
