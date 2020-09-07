from logging import info, warning
from os import environ

import boto3
from botocore.exceptions import ClientError

from mp import (
    SOURCE_BUCKET,
    DEFAULT_REGION,
)


class KeyDownloadError(Exception):
    def __init__(self, message):
        super().__init__(message)


def key_exists(key, region=DEFAULT_REGION):
    bucket = environ[SOURCE_BUCKET]
    s3 = boto3.client('s3', region_name=region)
    objs = s3.list_objects_v2(Bucket=bucket, MaxKeys=1, Prefix=key)
    sc = objs.get('ResponseMetadata', {}).get('HTTPStatusCode')
    return sc == 200


def download_file_from_s3(key, dest, region=DEFAULT_REGION):
    bucket = environ[SOURCE_BUCKET]

    info(f'downloading s3://{bucket}:{key} to {dest}')
    s3 = boto3.resource('s3', region_name=region)

    try:
        s3_obj = s3.Object(bucket, key)
        s3_obj.download_file(dest)
        info(f'{key} downloaded to {dest}')
    except Exception as e:
        warning(f'ERROR: {bucket}/{key}: {e}')
        raise KeyDownloadError(f'{bucket}/{key} not found: {e}')
