from json import loads
import logging
import os

import boto3
import sentry_sdk

from unittest.mock import MagicMock

from mp import lambda_common
from mp.util import tools

MOCK_BUCKET = 'mock_bucket_name'

mock_event_keys = [
    'f26801ac-5f83-445f-b9bf-84913a46ba9c/4974c818-12f6-42de-9913-df95cf14970c.jpg',
    'f26801ac-5f83-445f-b9bf-84913a46ba9c/5835d2fa-0982-49fd-8b3c-df950e8a739f.jpg',
    'f26801ac-5f83-445f-b9bf-84913a46ba9c/49c62fe7-b816-4ab9-a7ed-2ce54615e3b3.jpg',
    'f26801ac-5f83-445f-b9bf-84913a46ba9c/28692e9d-7ab6-4347-946f-8fece3ebe98f.jpg',
]

apig_event_sample = loads(
    '''{
    "resource": "/",
    "path": "/",
    "httpMethod": "GET",
    "headers": {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "s_fid=7AAB6XMPLAFD9BBF-0643XMPL09956DE2; regStatus=pre-register",
        "Host": "70ixmpl4fl.execute-api.us-east-2.amazonaws.com",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "upgrade-insecure-requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        "X-Amzn-Trace-Id": "Root=1-5e66d96f-7491f09xmpl79d18acf3d050",
        "X-Forwarded-For": "52.255.255.12",
        "X-Forwarded-Port": "443",
        "X-Forwarded-Proto": "https"
    },
    "multiValueHeaders": {
        "accept": [
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        ],
        "accept-encoding": [
            "gzip, deflate, br"
        ],
        "accept-language": [
            "en-US,en;q=0.9"
        ],
        "cookie": [
            "s_fid=7AABXMPL1AFD9BBF-0643XMPL09956DE2; regStatus=pre-register;"
        ],
        "Host": [
            "70ixmpl4fl.execute-api.ca-central-1.amazonaws.com"
        ],
        "sec-fetch-dest": [
            "document"
        ],
        "sec-fetch-mode": [
            "navigate"
        ],
        "sec-fetch-site": [
            "none"
        ],
        "upgrade-insecure-requests": [
            "1"
        ],
        "User-Agent": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        ],
        "X-Amzn-Trace-Id": [
            "Root=1-5e66d96f-7491f09xmpl79d18acf3d050"
        ],
        "X-Forwarded-For": [
            "52.255.255.12"
        ],
        "X-Forwarded-Port": [
            "443"
        ],
        "X-Forwarded-Proto": [
            "https"
        ]
    },
    "queryStringParameters": null,
    "multiValueQueryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "requestContext": {
        "resourceId": "2gxmpl",
        "resourcePath": "/",
        "httpMethod": "GET",
        "extendedRequestId": "JJbxmplHYosFVYQ=",
        "requestTime": "10/Mar/2020:00:03:59 +0000",
        "path": "/Prod/",
        "accountId": "123456789012",
        "protocol": "HTTP/1.1",
        "stage": "Prod",
        "domainPrefix": "70ixmpl4fl",
        "requestTimeEpoch": 1583798639428,
        "requestId": "77375676-xmpl-4b79-853a-f982474efe18",
        "identity": {
            "cognitoIdentityPoolId": null,
            "accountId": null,
            "cognitoIdentityId": null,
            "caller": null,
            "sourceIp": "52.255.255.12",
            "principalOrgId": null,
            "accessKey": null,
            "cognitoAuthenticationType": null,
            "cognitoAuthenticationProvider": null,
            "userArn": null,
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "user": null
        },
        "domainName": "70ixmpl4fl.execute-api.us-east-2.amazonaws.com",
        "apiId": "70ixmpl4fl"
    },
    "body": null,
    "isBase64Encoded": false
}
'''
)

apig_event_sample['path'] = f'/{mock_event_keys[0]}'


s3_put_multiple_event_sample = loads(
    '''{
   "Records":[
      {
         "eventVersion":"2.1",
         "eventSource":"aws:s3",
         "awsRegion":"us-west-2",
         "eventTime":"1970-01-01T00:00:00.000Z",
         "eventName":"ObjectCreated:Put",
         "userIdentity":{
            "principalId":"AIDAJDPLRKLG7UEXAMPLE"
         },
         "requestParameters":{
            "sourceIPAddress":"127.0.0.1"
         },
         "responseElements":{
            "x-amz-request-id":"C3D13FE58DE4C810",
            "x-amz-id-2":"FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
         },
         "s3":{
            "s3SchemaVersion":"1.0",
            "configurationId":"testConfigRule",
            "bucket":{
               "name":"mybucket",
               "ownerIdentity":{
                  "principalId":"A3NL1KOZZKExample"
               },
               "arn":"arn:aws:s3:::mybucket"
            },
            "object":{
               "key": "dummy-key",
               "size":1024,
               "eTag":"d41d8cd98f00b204e9800998ecf8427e",
               "versionId":"096fKKXTRTtl3on89fVO.nfljtsv6qko",
               "sequencer":"0055AED6DCD90281E5"
            }
         }
      },
      {
         "eventVersion":"2.1",
         "eventSource":"aws:s3",
         "awsRegion":"us-west-2",
         "eventTime":"1970-01-01T00:00:00.000Z",
         "eventName":"ObjectCreated:Put",
         "userIdentity":{
            "principalId":"AIDAJDPLRKLG7UEXAMPLE"
         },
         "requestParameters":{
            "sourceIPAddress":"127.0.0.1"
         },
         "responseElements":{
            "x-amz-request-id":"C3D13FE58DE4C810",
            "x-amz-id-2":"FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
         },
         "s3":{
            "s3SchemaVersion":"1.0",
            "configurationId":"testConfigRule",
            "bucket":{
               "name":"mybucket",
               "ownerIdentity":{
                  "principalId":"A3NL1KOZZKExample"
               },
               "arn":"arn:aws:s3:::mybucket"
            },
            "object":{
               "key": "dummy-key",
               "size":1024,
               "eTag":"d41d8cd98f00b204e9800998ecf8427e",
               "versionId":"096fKKXTRTtl3on89fVO.nfljtsv6qko",
               "sequencer":"0055AED6DCD90281E5"
            }
         }
      },
      {
         "eventVersion":"2.1",
         "eventSource":"aws:s3",
         "awsRegion":"us-west-2",
         "eventTime":"1970-01-01T00:00:00.000Z",
         "eventName":"ObjectCreated:Put",
         "userIdentity":{
            "principalId":"AIDAJDPLRKLG7UEXAMPLE"
         },
         "requestParameters":{
            "sourceIPAddress":"127.0.0.1"
         },
         "responseElements":{
            "x-amz-request-id":"C3D13FE58DE4C810",
            "x-amz-id-2":"FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
         },
         "s3":{
            "s3SchemaVersion":"1.0",
            "configurationId":"testConfigRule",
            "bucket":{
               "name":"mybucket",
               "ownerIdentity":{
                  "principalId":"A3NL1KOZZKExample"
               },
               "arn":"arn:aws:s3:::mybucket"
            },
            "object":{
               "key": "dummy-key",
               "size":1024,
               "eTag":"d41d8cd98f00b204e9800998ecf8427e",
               "versionId":"096fKKXTRTtl3on89fVO.nfljtsv6qko",
               "sequencer":"0055AED6DCD90281E5"
            }
         }
      },
      {
         "eventVersion":"2.1",
         "eventSource":"aws:s3",
         "awsRegion":"us-west-2",
         "eventTime":"1970-01-01T00:00:00.000Z",
         "eventName":"ObjectCreated:Put",
         "userIdentity":{
            "principalId":"AIDAJDPLRKLG7UEXAMPLE"
         },
         "requestParameters":{
            "sourceIPAddress":"127.0.0.1"
         },
         "responseElements":{
            "x-amz-request-id":"C3D13FE58DE4C810",
            "x-amz-id-2":"FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
         },
         "s3":{
            "s3SchemaVersion":"1.0",
            "configurationId":"testConfigRule",
            "bucket":{
               "name":"mybucket",
               "ownerIdentity":{
                  "principalId":"A3NL1KOZZKExample"
               },
               "arn":"arn:aws:s3:::mybucket"
            },
            "object":{
               "key": "dummy-key",
               "size":1024,
               "eTag":"d41d8cd98f00b204e9800998ecf8427e",
               "versionId":"096fKKXTRTtl3on89fVO.nfljtsv6qko",
               "sequencer":"0055AED6DCD90281E5"
            }
         }
      }
   ]
}'''
)

for counter, record in enumerate(s3_put_multiple_event_sample['Records']):
    record['s3']['object']['key'] = mock_event_keys[counter]


s3_put_single_event_sample = {'Records': [s3_put_multiple_event_sample['Records'][0]]}


def setup_mocks(
    mocker, writer_exists_retval=False, force_update_retval=False, mock_env={}
):
    if len(mock_env) > 0:
        mocker.patch.dict(os.environ, mock_env)

    mocker.patch.object(tools, 'configure_logging')
    mocker.patch.object(logging, 'info')
    mocker.patch.object(logging, 'debug')
    mocker.patch.object(lambda_common, 'init_monitoring')

    mock_scope = MagicMock()
    mock_sentry = MagicMock(return_value=mock_scope)
    mocker.patch.object(sentry_sdk, 'configure_scope', mock_sentry)

    mock_s3 = MagicMock()
    # used by s3_loader.key_exists:
    mock_s3.list_objects_v2 = MagicMock(return_value=mock_event_keys)
    mocker.patch.object(boto3, 'resource', MagicMock(return_value=mock_s3))

    mock_force_upd = MagicMock(return_value=force_update_retval)
    mocker.patch.object(lambda_common, 'check_force_update', mock_force_upd)

    mock_writer = MagicMock()
    mock_writer.exists = MagicMock(return_value=writer_exists_retval)
    mock_init_writer = MagicMock(return_value=mock_writer)
    mocker.patch.object(lambda_common, 'init_writer', mock_init_writer)

    mocker.patch.object(lambda_common, 'write_metadata', MagicMock())


def assert_mocks(
    event_write_count=1, init_writer_call_count=1, force_update_call_count=1
):
    tools.configure_logging.assert_called_once()
    logging.info.assert_called()
    logging.debug.assert_called()
    lambda_common.init_monitoring.assert_called_once()
    lambda_common.check_force_update.call_count == force_update_call_count
    lambda_common.init_writer.call_count == init_writer_call_count
    lambda_common.write_metadata.call_count == event_write_count
