import boto3
import os
import json
import time

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']
TOTAL_TEMP_SIZE_KEY = 'total_temp_size.txt'

def get_object_size(bucket, key):
    try:
        response = s3.head_object(Bucket=bucket, Key=key)
        return response['ContentLength']
    except s3.exceptions.NoSuchKey:
        print(f'Object {key} not found in bucket {bucket}')
        return None
    except Exception as e:
        print(f'Error getting object size: {e}')
        return None

def get_total_temp_size():
    try:
        response = s3.get_object(Bucket=DESTINATION_BUCKET, Key=TOTAL_TEMP_SIZE_KEY)
        total_size = int(response['Body'].read().decode('utf-8'))
        return total_size
    except s3.exceptions.NoSuchKey:
        print(f'{TOTAL_TEMP_SIZE_KEY} not found in bucket {DESTINATION_BUCKET}, initializing to 0.')
        return 0
    except Exception as e:
        print(f'Error getting total temp size: {e}')
        return 0

def set_total_temp_size(total_size):
    try:
        s3.put_object(Bucket=DESTINATION_BUCKET, Key=TOTAL_TEMP_SIZE_KEY, Body=str(total_size))
    except Exception as e:
        print(f'Error setting total temp size: {e}')

def handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    total_temp_size = get_total_temp_size()

    for record in event['Records']:
        sqs_body = json.loads(record['body'])
        print("SQS body:", json.dumps(sqs_body, indent=2))

        sns_message = json.loads(sqs_body['Message'])
        print("SNS message:", json.dumps(sns_message, indent=2))

        # Handle test event
        if sns_message.get('Event') == 's3:TestEvent':
            print("Received test event, skipping processing.")
            continue

        # Check if 'Records' is present in sns_message
        if 'Records' not in sns_message:
            print("No 'Records' in SNS message, skipping.")
            continue

        for s3_record in sns_message['Records']:
            key = s3_record['s3']['object']['key']
            bucket_name = s3_record['s3']['bucket']['name']

            print(f'Processing object key: {key} from bucket: {bucket_name}')

            size = None
            for attempt in range(3):  # Retry up to 3 times
                size = get_object_size(bucket_name, key)
                if size is not None:
                    break
                print(f'Retry {attempt + 1}: Object {key} not found. Retrying...')
                time.sleep(5)  # Wait for 5 seconds before retrying

            if size is not None:
                print(f'Size for key {key} is {size}')
                if 'temp' in key:
                    total_temp_size += size
                # Report the total size of temporary objects
                cloudwatch.put_metric_data(
                    Namespace='S3BackupSystem',
                    MetricData=[
                        {
                            'MetricName': 'TotalTemporaryObjectSize',
                            'Dimensions': [
                                {
                                    'Name': 'BucketName',
                                    'Value': DESTINATION_BUCKET
                                }
                            ],
                            'Value': total_temp_size,
                            'Unit': 'Bytes'
                        }
                    ]
                )
                set_total_temp_size(total_temp_size)
            else:
                print(f'Failed to get size for key {key} after 3 attempts.')
                # Report a zero increase for non-temporary objects
                cloudwatch.put_metric_data(
                    Namespace='S3BackupSystem',
                    MetricData=[
                        {
                            'MetricName': 'TotalTemporaryObjectSize',
                            'Dimensions': [
                                {
                                    'Name': 'BucketName',
                                    'Value': DESTINATION_BUCKET
                                }
                            ],
                            'Value': total_temp_size,
                            'Unit': 'Bytes'
                        }
                    ]
                )
