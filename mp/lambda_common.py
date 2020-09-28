from json import dumps
from logging import debug, info, warning, error
from os import environ
from tempfile import NamedTemporaryFile
from traceback import format_tb
from uuid import uuid4

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from mp import (
    version,
    MONITORING_DSN,
    OPERATING_ENV,
    DATABASE_URL,
    FORCE_UPDATE,
)
from mp.model.image_key import ImageKey
from mp.io.loader.s3_loader import download_file_from_s3
from mp.io.metadata_reader import extract_metadata
from mp.io.writer.connection_factory import ConnectionFactory
from mp.io.writer.metadata_writer import (
    MetadataWriter,
    DatabaseMetadataWriter,
)
from mp.io.writer.exception_writer import (
    ExceptionEventWriter,
    DatabaseExceptionEventWriter,
)
from mp.util.tools import parse_db_url


def extract_image_key_from_apig_event(event: object) -> ImageKey:
    debug('extract_image_key_from_apig_event called')
    if not event:
        return None
    path = event.get('path')
    try:
        return ImageKey(path=path[1:]) if path else None
    except ValueError:
        return None


def extract_image_keys_from_s3_event(event: object) -> [ImageKey]:
    debug('extract_image_keys_from_s3_event called')
    keys = []
    if event:
        for record in event.get('Records', []):
            key = record.get('s3', {}).get('object', {}).get('key')
            keys.append(ImageKey(path=key)) if key else None
    return keys


def check_force_update(event: object) -> bool:
    debug('check_force_update called')
    if FORCE_UPDATE in environ:  # pragma: no cover
        return True
    if not event:
        return None
    qs = event.get('queryStringParameters')
    return True if qs and 'update' in qs else False


def init_monitoring() -> None:  # pragma: no cover
    debug('init_monitoring called')
    dsn = environ.get(MONITORING_DSN)
    env = environ.get(OPERATING_ENV)

    if not dsn:
        warning(f'DSN not found in envronment under key {MONITORING_DSN}')
        return

    sentry_sdk.init(
        dsn=dsn,
        integrations=[AwsLambdaIntegration()],
        release=f'v{version}',
        send_default_pii=False,
        traces_sample_rate=0.50,
        environment=env,
        _experiments={'auto_enabling_integrations': True},
    )
    info(f'Monitoring configured with DSN: {dsn}')


def connection_factory():  # pragma: no cover
    u = environ.get(DATABASE_URL)
    url = parse_db_url(u)
    return ConnectionFactory.instance(url)


def init_exception_writer() -> ExceptionEventWriter:  # pragma: no cover
    debug('init_exception_writer called')
    conn_factory = connection_factory()
    return DatabaseExceptionEventWriter(conn_factory)


def init_metadata_writer() -> MetadataWriter:  # pragma: no cover
    debug('init_metadata_writer called')
    conn_factory = connection_factory()
    return DatabaseMetadataWriter(conn_factory)


def write_metadata(writer: MetadataWriter, key: ImageKey) -> object:  # pragma: no cover
    debug(f'write_metadata called: {writer} for {key}')
    with NamedTemporaryFile(suffix=f'.{key.extension}') as temp:
        download_file_from_s3(key, temp.name)
        metadata = extract_metadata(key, temp.name)
        debug(metadata)
        return writer.write(metadata)


def generate_json_response(message, sc=200):
    debug(f'generate_json_response called {sc}')
    mesg = {'message': message}
    debug(f'response {sc} with message: {message}')
    return {
        'isBase64Encoded': False,
        'statusCode': sc,
        'headers': {'content-type': 'text/json'},
        'body': dumps(mesg),
    }


def write_exception_event(writer, image_key, exception):
    exc = exception[0]
    type_name = exc.__name__
    error(f'Received exception when processing {image_key}: {type_name}')
    tb = '\n'.join(format_tb(exception[2]))
    event = {
        'id': uuid4(),
        'owner': image_key.owner_id,
        'file_path': image_key.file_path,
        'error_code': type_name,
        'message': ' '.join(exception[1].args),
        'reason': tb,
        'original_file_path': None,
    }
    return writer.write(event)
