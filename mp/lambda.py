from logging import debug, info, warn
from os import environ

from sentry_sdk import init, configure_scope
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from mp import (
    version,
    MONITORING_DSN,
    OPERATING_ENV,
    DATABASE_URL,
)
from mp.io.metadata_reader import extract_metadata
from mp.io.writer.metadata_writer import (
    DatabaseMetadataWriter,
    ConnectionFactory,
)
from mp.util.tools import configure_logging


def setup_logging(evt):
    verboseLogging = False
    qs = evt.get('queryStringParameters')
    if qs and 'verbose' in qs:
        verboseLogging = True
    configure_logging(verboseLogging)


def init_monitoring():
    dsn = environ.get(MONITORING_DSN)
    env = environ.get(OPERATING_ENV)

    if not dsn:
        warn(f'DSN not found in envronment under key {MONITORING_DSN}')
        return

    info(f'Configuring monitoring via DSN: {dsn}')
    init(
        dsn=dsn,
        integrations=[AwsLambdaIntegration()],
        release=f'v{version}',
        send_default_pii=False,
        traces_sample_rate=0.50,
        environment=env,
        _experiments={'auto_enabling_integrations': True},
    )


def init_writer():
    url = environ.get(DATABASE_URL)
    conn_factory = ConnectionFactory.instance(url)
    return DatabaseMetadataWriter(conn_factory)


def extract_image_keys(event) -> [ImageKey]:
    pass


def handler(event, context):
    info(f'mp v{version}')
    debug(event)
    setup_logging(event)
    init_monitoring()
    writer = init_writer()

    with configure_scope() as scope:
        scope.set_extra('processor_event', event)

        if environ.get(TRIGGER_ERROR):
            raise Exception('test event')

        keys = extract_image_keys(event)

        for key in keys:
            scope.set_tag('image_key', image_key.file_path)
            scope.set_tag('owner_id', image_key.owner_id)
            scope.set_tag('image_id', image_key.image_id)

            with NamedTemporaryFile(suffix=ext) as temp:
                download_file_from_s3(key, temp.name)
                metadata = extract_metadata(key, temp.name)
                with writer:
                    result = writer.write(metadata)
                if result:
                    info(f'result: {result}')
