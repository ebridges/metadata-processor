from json import dumps
from logging import debug, info, warning
from os import environ
from tempfile import NamedTemporaryFile

from sentry_sdk import init
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from mp import (
    version,
    MONITORING_DSN,
    OPERATING_ENV,
    DATABASE_URL,
)
from mp.model.image_key import ImageKey
from mp.io.loader.s3_loader import download_file_from_s3
from mp.io.metadata_reader import extract_metadata
from mp.io.writer.metadata_writer import (
    MetadataWriter,
    DatabaseMetadataWriter,
    ConnectionFactory,
)


def extract_image_key_from_apig_event(event: object) -> ImageKey:
    if not event:
        return None
    path = event.get('path')
    return ImageKey(path=path[1:]) if path else None


def extract_image_keys_from_s3_event(event: object) -> [ImageKey]:
    keys = []
    for record in event['Records']:
        key = record.get('s3', {}).get('object', {}).get('key')
        keys.append(ImageKey(path=key)) if key else None
    return keys


def check_force_update(event: object) -> bool:
    if not event:
        return None
    qs = event.get('queryStringParameters')
    print(f'qs: {qs}')
    return True if qs and 'update' in qs else False


def init_monitoring() -> None:  # pragma: no cover
    dsn = environ.get(MONITORING_DSN)
    env = environ.get(OPERATING_ENV)

    if not dsn:
        warning(f'DSN not found in envronment under key {MONITORING_DSN}')
        return

    init(
        dsn=dsn,
        integrations=[AwsLambdaIntegration()],
        release=f'v{version}',
        send_default_pii=False,
        traces_sample_rate=0.50,
        environment=env,
        _experiments={'auto_enabling_integrations': True},
    )
    info(f'Monitoring configured with DSN: {dsn}')


def init_writer() -> MetadataWriter:  # pragma: no cover
    url = environ.get(DATABASE_URL)
    conn_factory = ConnectionFactory.instance(url)
    return DatabaseMetadataWriter(conn_factory)


def write_metadata(writer: MetadataWriter, key: ImageKey) -> object:  # pragma: no cover
    with NamedTemporaryFile(suffix=key.extension) as temp:
        download_file_from_s3(key, temp.name)
        metadata = extract_metadata(key, temp.name)
        return writer.write(metadata)


def generate_json_response(message, httpStatusCode=200):
    mesg = {'message': message}
    debug(f'response {httpStatusCode} with message: {message}')
    return {
        'isBase64Encoded': False,
        'statusCode': httpStatusCode,
        'headers': {'content-type': 'text/json'},
        'body': dumps(mesg),
    }