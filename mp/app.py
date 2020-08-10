from mp.io.metadata_reader import extract_metadata
from mp.model.image_key import ImageKey
from mp.model.metadata import Metadata
from mp.io.writer.metadata_formatter import formatters


def save_metadata(image_key, file_location, writer, verbose):
    log_level = 'debug' if verbose else 'warn'
    metadata = extract_metadata(image_key, file_location(), log_level)
    writer(metadata)


if __name__ == '__main__':
    import argparse

    from mp.io.loader.filesystem_loader import FilesystemLoader
    from mp.io.writer.metadata_writer import MetadataWriter

    parser = argparse.ArgumentParser(
        description='Process an image and print metadata to stdout.'
    )
    parser.add_argument(
        '--image_path', '-i', action='store', help='Path of image to process.'
    )
    parser.add_argument(
        '--output',
        '-o',
        action='store',
        default='stdout',
        help='Where to output metadata. Default: stdout.',
    )
    parser.add_argument(
        '--format',
        '-f',
        action='store',
        default='csv',
        help='What format to write out metadata in. Default: csv.',
    )
    parser.add_argument('--verbose', action='store_true', help='Verbose flag')
    args = parser.parse_args()

    image_key = ImageKey()
    formatter = formatters[args.format]
    writer = MetadataWriter.instance(args.output, formatter)
    file_loader = FilesystemLoader(args.image_path)
    save_metadata(image_key, file_loader.file_path, writer.write, args.verbose)
