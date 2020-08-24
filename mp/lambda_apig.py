from logging import debug, info, warning
from os import environ
import sentry_sdk

from mp import version, TRIGGER_ERROR

from mp.io.loader.s3_loader import key_exists, download_file_from_s3
from mp.lambda_common import (
    extract_image_key_from_apig_event,
    check_force_update,
    init_writer,
    write_metadata,
    init_monitoring,
    generate_json_response,
)
from mp.util.tools import configure_logging


def api_handler(event, context):
    configure_logging()
    init_monitoring()
    info(f'mp v{version}')
    debug(event)

    with sentry_sdk.configure_scope() as scope:
        scope.set_extra('processor_event', event)

        if environ.get(TRIGGER_ERROR):
            raise Exception('test event')

        key = extract_image_key_from_apig_event(event)
        scope.set_tag('image_key', key.file_path)
        scope.set_tag('owner_id', key.owner_id)
        scope.set_tag('image_id', key.image_id)

        if not key_exists(key.file_path):
            return generate_json_response(f'{key} not found.', httpStatusCode=404)

        force_update = check_force_update(event)
        scope.set_tag('force_update', force_update)

        writer = init_writer()
        with writer:
            exists_in_db = writer.exists(key.file_path)
            if not exists_in_db or (exists_in_db and force_update):
                write_metadata(writer, key)
                return generate_json_response(f'{key} processed.')
            else:
                return generate_json_response(f'{key} not processed.')
