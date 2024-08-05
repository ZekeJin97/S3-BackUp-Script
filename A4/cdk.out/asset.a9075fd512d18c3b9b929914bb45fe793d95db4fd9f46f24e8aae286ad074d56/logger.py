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
    print("Received event:", json.dumps(event, indent=2))

    for record in event['Records']:
        sqs_body = json.loads(record['body'])
        print("SQS body:", json.dumps(sqs_body, indent=2))

        sns_message = json.loads(sqs_body['Message'])
        print("SNS message:", json.dumps(sns_message, indent=2))

        # Handle s3:TestEvent
        if 'Records' not in sns_message:
            print("No 'Records' in SNS message, skipping.")
            continue

        for s3_record in sns_message['Records']:
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
                    cloudwatch.put_metric_data(
                        Namespace='S3BackupSystem',
                        MetricData=[
                            {
                                'MetricName': 'TemporaryObjectSize',
                                'Dimensions': [
                                    {
                                        'Name': 'BucketName',
                                        'Value': DESTINATION_BUCKET
                                    }
                                ],
                                'Value': size,
                                'Unit': 'Bytes'
                            }
                        ]
                    )
            else:
                print(f'Failed to get size for key {key} after 3 attempts.')
