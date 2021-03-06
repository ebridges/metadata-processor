from os import environ
from logging import getLogger, basicConfig, DEBUG, INFO, debug
from urllib.parse import urlparse

import click

from mp import VERBOSE_LOGGING
from mp.model.image_key import ImageKey


class ImageKeyType(click.ParamType):  # pragma: no cover
    name = 'image-key'

    def convert(self, value, param, ctx):
        try:
            debug(f'parsing image key: {value}')
            return ImageKey(value)
        except ValueError as e:
            self.fail(f'ImageKey in unexpected format: {value} ({str(e)})', param, ctx)


class DatabaseUrlType(click.ParamType):
    name = 'db-url'

    def convert(self, value, param, ctx):
        try:
            debug(f'parsing database url: {value}')
            return parse_db_url(value)
        except ValueError as e:
            self.fail(
                f'DB connection url in unexpected format: {value} ({str(e)})',
                param,
                ctx,
            )


def parse_db_url(value):
    u = urlparse(value)

    if not u.scheme:
        raise ValueError('URL scheme is required.')

    if not u.path:
        raise ValueError('URL path is required.')

    path = u.path if not u.path.startswith('/') else u.path[1:]
    return {
        'url': value,
        'dbtype': u.scheme,
        'hostname': u.hostname,
        'port': u.port,
        'dbname': path,
        'username': u.username,
        'password': u.password,
    }


def configure_logging(verbose=False):  # pragma: no cover
    if environ.get(VERBOSE_LOGGING):
        level = DEBUG
    elif verbose:
        level = DEBUG
    else:
        level = INFO

    if getLogger().hasHandlers():
        # The Lambda environment pre-configures a handler logging to stderr.
        # If a handler is already configured, `.basicConfig` does not execute.
        # Thus we set the level directly.
        getLogger().setLevel(level)

    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=level,
    )
