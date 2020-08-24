from logging import info
from os import environ

import boto3
from botocore.exceptions import ClientError

from mp import (
    SOURCE_BUCKET,
    DEFAULT_REGION,
)


class KeyNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)


def key_exists(key, region=DEFAULT_REGION):
    bucket = environ[SOURCE_BUCKET]
    s3 = boto3.resource('s3', region_name=region)
    objs = s3.list_objects_v2(Bucket=bucket, MaxKeys=1, Prefix=key,)
    return any([w.key == key for w in objs])


def download_file_from_s3(key, dest, region=DEFAULT_REGION):
    bucket = environ(SOURCE_BUCKET)

    info(f'downloading s3://{bucket}:{key} to {dest}')
    s3 = boto3.resource('s3', region_name=region)

    try:
        s3_obj = s3.Object(bucket, key)
        s3_obj.download_file(dest)
        info(f'{key} downloaded to {dest}')
    except Exception as e:  #  botocore.exceptions.ClientError
        info(f'NOT FOUND: {bucket}/{key}: {e}')
        if e.response['Error']['Code'] == '404':
            raise KeyNotFound(f'{bucket}/{key} not found')
