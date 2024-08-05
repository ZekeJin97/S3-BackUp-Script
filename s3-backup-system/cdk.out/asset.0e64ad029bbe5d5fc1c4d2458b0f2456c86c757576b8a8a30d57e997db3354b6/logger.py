import boto3
import os
import logging
import json
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info(f"Received event: {event}")

    for record in event.get('Records', []):
        # Check if the event is from S3
        if record.get('eventSource') == 'aws:s3':
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
                logger.error(f"Error getting object size for {key}: {e}")
        else:
            logger.warning(f"Skipping non-S3 event: {record}")


def get_object_size(key):
    try:
        response = s3.head_object(Bucket=DESTINATION_BUCKET, Key=key)
        return response['ContentLength']
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.error(f"Object {key} not found in bucket {DESTINATION_BUCKET}")
        else:
            logger.error(f"Unexpected error: {e}")
        return None
