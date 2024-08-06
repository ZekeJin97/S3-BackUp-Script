import boto3
import os
import time

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        key = record['s3']['object']['key']
        size = None

        for attempt in range(3):  # Retry up to 3 times
            try:
                response = s3.head_object(Bucket=destination_bucket, Key=key)
                size = response['ContentLength']
                break
            except s3.exceptions.NoSuchKey:
                print(f'Object {key} not found in bucket {destination_bucket}')
                time.sleep(5)  # Wait for 5 seconds before retrying
            except Exception as e:
                print(f'Error getting object size: {e}')
                time.sleep(5)  # Wait for 5 seconds before retrying

        if size is not None:
            print(f'Size for key {key} is {size}')
            metric_name = 'TemporaryObjectSize' if 'temp' in key else 'NonTemporaryObjectSize'
            cloudwatch.put_metric_data(
                Namespace='S3BackupSystem',
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Dimensions': [
                            {
                                'Name': 'BucketName',
                                'Value': destination_bucket
                            }
                        ],
                        'Value': size,
                        'Unit': 'Bytes'
                    }
                ]
            )
        else:
            print(f'Failed to get size for key {key} after 3 attempts.')
