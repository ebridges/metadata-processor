from logging import debug, info, warn
from os import environ


from mp import (
    version,
    MONITORING_DSN,
    OPERATING_ENV,
    DATABASE_URL,
)
from mp.io.loader.s3_loader import key_exists, download_file_from_s3
from mp.io.metadata_reader import extract_metadata
from mp.io.writer.metadata_writer import (
    DatabaseMetadataWriter,
    ConnectionFactory,
)
from mp.util.tools import configure_logging


def s3_handler(event, context):
    info(f'mp v{version}')
    debug(event)
    configure_logging()
    init_monitoring()
    writer = init_writer()

    with configure_scope() as scope:
        scope.set_extra('processor_event', event)

        if environ.get(TRIGGER_ERROR):
            raise Exception('test event')

        keys = extract_image_keys(event)

        for key in keys:
            scope.set_tag('image_key', key.file_path)
            scope.set_tag('owner_id', key.owner_id)
            scope.set_tag('image_id', key.image_id)

            if not key_exists(key.file_path):
                return not_found_response(key)

            force_update = check_force_update(event)

            with writer:
                result = write_metadata(key, writer)
                if result:
                    info(f'result: {result}')
