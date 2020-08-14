'''
Usage: mp [OPTIONS] [IMAGE_FILENAMES]...

Options:
  -i, --image-key TEXT         Key used for this image in remote storage,
                               ignored if multiple filenames are passed.
                               [default: d8cc87e9-4ebc-4a03-a2cd-5fff53f49469/
                               ac4a6a09-c8bd-40a2-b99f-ed0b8a9db500.jpg]

  -d, --db-url DB-URL          Connect information for database to write
                               metadata. Example:
                               driver://user:pass@host/database

  -f, --format [csv|txt|json]  Format of metadata when written to file or to
                               stdout.  [default: txt]

  -o, --output FILENAME        Filename to write out metadata.
  -v, --verbose                Show verbose logging.
  --version                    Show the version and exit.
  --help                       Show this message and exit.
'''
from logging import info
from sys import stdout
from click import command, argument, option, version_option, Choice, File, Path

from mp import version
from mp.io.metadata_reader import extract_metadata
from mp.io.writer.metadata_writer import (
    FilehandleMetadataWriter,
    DatabaseMetadataWriter,
    ConnectionFactory,
)
from mp.model.image_key import ImageKey
from mp.model.metadata import Metadata
from mp.io.writer.metadata_formatter import formatters
from mp.util.tools import DatabaseUrlType, configure_logging


connection_url_envvar = 'MP_DB_URL'
format_types = formatters.keys()


@command(
    name='mp',
    short_help='Extracts metadata from an image for display or saving.',
    epilog='© 2020 Edward Bridges CC BY-NC-SA 4.0',
)
@argument(
    'image-filenames',
    nargs=-1,
    required=False,
    type=Path(exists=True, readable=True, resolve_path=True, allow_dash=True),
)
@option(
    '-i',
    '--image-key',
    required=False,
    default=ImageKey.new(),
    show_default=True,
    help='Key used for this image in remote storage, ignored if multiple filenames are passed.',
)
@option(
    '-d',
    '--db-url',
    required=False,
    type=DatabaseUrlType(),
    envvar=connection_url_envvar,
    help='Connect information for database to write metadata. Example: driver://user:pass@host/database',
)
@option(
    '-f',
    '--format',
    required=False,
    type=Choice(format_types, case_sensitive=False),
    default=('txt'),
    show_default=True,
    help='Format of metadata when written to file or to stdout.',
)
@option(
    '-o',
    '--output',
    required=False,
    type=File(mode='w'),
    help='Filename to write out metadata.',
)
@option('-v', '--verbose', default=False, is_flag=True, help='Show verbose logging.')
@version_option(version=version)
def mp(image_filenames, image_key, db_url, format, output, verbose):
    configure_logging(verbose)

    info(f'mp v{version}')
    writer = None
    if db_url:
        connection_factory = ConnectionFactory.instance(db_url)
        writer = DatabaseMetadataWriter(connection_factory)
    else:
        output_type = output if output else stdout
        formatter = formatters[format]
        writer = FilehandleMetadataWriter(output_type, formatter)

    metadatas = []
    for image_filename in image_filenames:
        image_key = ImageKey.new() if not image_key else image_key
        info(f'gathering metadata from {image_filename} for key {image_key}')
        metadata = extract_metadata(image_key, image_filename, verbose)
        metadatas.append(metadata)

    for metadata in metadatas:
        info(f'writing metadata {metadata.file_path} [{metadata.create_day_id}]')
        writer.write(metadata)


if __name__ == '__main__':
    mp()
