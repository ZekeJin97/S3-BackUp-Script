import boto3
import os
import json

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
lambda_client = boto3.client('lambda')

DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']
LOGGER_LAMBDA_NAME = os.environ['LOGGER_LAMBDA_NAME']

def handler(event, context):
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        source_key = record['s3']['object']['key']

        # Copy the object
        copy_source = {'Bucket': source_bucket, 'Key': source_key}
        s3.copy_object(CopySource=copy_source, Bucket=DESTINATION_BUCKET, Key=source_key)

        # Calculate the size of the temporary objects and report to CloudWatch
        total_size = calculate_temp_size(DESTINATION_BUCKET)
        report_temp_size(total_size)

        # Log the copy event
        log_event(f"Copied {source_key} from {source_bucket} to {DESTINATION_BUCKET}")

def calculate_temp_size(bucket_name):
    temp_size = 0
    response = s3.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        if 'temp' in obj['Key']:
            temp_size += obj['Size']
    return temp_size

def report_temp_size(size):
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
                'Unit': 'Bytes',
                'Value': size
            },
        ]
    )

def log_event(message):
    lambda_client.invoke(
        FunctionName=LOGGER_LAMBDA_NAME,
        InvocationType='Event',
        Payload=json.dumps({'message': message})
    )
