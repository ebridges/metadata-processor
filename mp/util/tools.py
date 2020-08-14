from logging import getLogger, basicConfig, DEBUG, INFO
from urllib.parse import urlparse

import click


class DatabaseUrlType(click.ParamType):  # pragma: no cover
    name = 'db-url'

    def convert(self, value, param, ctx):
        try:
            u = urlparse(value)
            return {
                'url': value,
                'dbtype': u.scheme,
                'hostname': u.hostname,
                'port': u.port,
                'dbname': u.path[1:],
                'username': u.username,
                'password': u.password,
            }
        except ValueError as e:
            self.fail(
                f'DB connection url in unexpected format: {value} ({str(e)})',
                param,
                ctx,
            )


def configure_logging(verbose):  # pragma: no cover
    if verbose:
        level = DEBUG
    else:
        level = INFO

    if getLogger().hasHandlers():
        # The Lambda environment pre-configures a handler logging to stderr.
        # If a handler is already configured, `.basicConfig` does not execute.
        # Thus we set the level directly.
        getLogger().setLevel(level)
    else:
        basicConfig(
            format='[%(asctime)s][%(levelname)s] %(message)s',
            datefmt='%Y/%m/%d %H:%M:%S',
            level=level,
        )
