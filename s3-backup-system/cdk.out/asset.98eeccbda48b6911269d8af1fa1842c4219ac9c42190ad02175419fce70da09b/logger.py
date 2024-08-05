import boto3
import os
import json
import time

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']


def get_object_size(key):
    try:
        response = s3.head_object(Bucket=DESTINATION_BUCKET, Key=key)
        return response['ContentLength']
    except s3.exceptions.NoSuchKey:
        print(f'Object {key} not found in bucket {DESTINATION_BUCKET}')
        return None
    except Exception as e:
        print(f'Error getting object size: {e}')
        return None


def handler(event, context):
    total_temp_size = 0
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        s3_event = json.loads(sns_message)
        s3_record = s3_event['Records'][0]
        key = s3_record['s3']['object']['key']

        print(f'Processing object key: {key}')

        size = None
        for attempt in range(3):  # Retry up to 3 times
            size = get_object_size(key)
            if size is not None:
                break
            print(f'Retry {attempt + 1}: Object {key} not found. Retrying...')
            time.sleep(5)  # Wait for 5 seconds before retrying

        if size is not None:
            print(f'Size for key {key} is {size}')
            if 'temp' in key:
                total_temp_size += size
                print(f'Temporary file {key} size added to total: {total_temp_size}')
            cloudwatch.put_metric_data(
                Namespace='S3BackupSystem',
                MetricData=[
                    {
                        'MetricName': 'ObjectSize',
                        'Dimensions': [
                            {
                                'Name': 'BucketName',
                                'Value': DESTINATION_BUCKET
                            },
                            {
                                'Name': 'FileName',
                                'Value': key
                            }
                        ],
                        'Value': size,
                        'Unit': 'Bytes'
                    }
                ]
            )
        else:
            print(f'Failed to get size for key {key} after 3 attempts.')

    # Publish total size of temporary files
    cloudwatch.put_metric_data(
        Namespace='S3BackupSystem',
        MetricData=[
            {
                'MetricName': 'TotalTempSize',
                'Value': total_temp_size,
                'Unit': 'Bytes'
            }
        ]
    )
    print(f'Total temporary files size published: {total_temp_size}')
