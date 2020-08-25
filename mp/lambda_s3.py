import logging
import os

import sentry_sdk

from mp import version, TRIGGER_ERROR, SOURCE_BUCKET
from mp.io.loader.s3_loader import key_exists, download_file_from_s3
from mp.lambda_common import (
    extract_image_keys_from_s3_event,
    init_monitoring,
    generate_json_response,
    check_force_update,
    init_writer,
    write_metadata,
)
from mp.util import tools


def s3_handler(event, context={}):
    tools.configure_logging()
    logging.info(f'mp v{version}')
    logging.debug(event)

    init_monitoring()
    with sentry_sdk.configure_scope() as scope:
        scope.set_extra('processor_event', event)

        if os.environ.get(TRIGGER_ERROR):
            raise Exception('test event')

        keys = extract_image_keys_from_s3_event(event)

        for key in keys:
            scope.set_tag('image_key', key.file_path)
            scope.set_tag('owner_id', key.owner_id)
            scope.set_tag('image_id', key.image_id)

            if not key_exists(key.file_path):
                bucket = os.environ.get(SOURCE_BUCKET)
                logging.info(f'{key} not found in bucket: {bucket}.')
                continue

            force_update = check_force_update(event)

            writer = init_writer()
            with writer:
                result = write_metadata(key, writer)
                if result:
                    logging.info(f'result: {result}')
