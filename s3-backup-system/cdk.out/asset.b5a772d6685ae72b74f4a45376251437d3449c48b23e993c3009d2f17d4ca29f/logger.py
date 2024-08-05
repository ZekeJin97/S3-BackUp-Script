import json
import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        key = record['s3']['object']['key']
        try:
            size = get_object_size(key)
            if size is not None and 'temp' in key:
                cloudwatch.put_metric_data(
                    Namespace='S3BackupSystem',
                    MetricData=[
                        {
                            'MetricName': 'TemporaryObjectSize',
                            'Dimensions': [
                                {
                                    'Name': 'BucketName',
                                    'Value': DESTINATION_BUCKET
                                },
                            ],
                            'Value': size,
                            'Unit': 'Bytes'
                        },
                    ]
                )
        except ClientError as e:
            print(f"Error getting object size for {key}: {e}")

def get_object_size(key):
    try:
        response = s3.head_object(Bucket=DESTINATION_BUCKET, Key=key)
        return response['ContentLength']
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Object {key} not found in bucket {DESTINATION_BUCKET}")
        else:
            print(f"Unexpected error: {e}")
        return None
