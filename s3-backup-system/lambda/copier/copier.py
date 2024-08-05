import boto3
import os
import json

s3 = boto3.client('s3')

DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        s3_event = json.loads(sns_message)
        for s3_record in s3_event['Records']:
            source_bucket = s3_record['s3']['bucket']['name']
            key = s3_record['s3']['object']['key']

            copy_source = {'Bucket': source_bucket, 'Key': key}
            s3.copy_object(CopySource=copy_source, Bucket=DESTINATION_BUCKET, Key=key)

            log_to_cloudwatch(key)

def log_to_cloudwatch(key):
    cloudwatch = boto3.client('cloudwatch')
    if 'temp' in key:
        response = cloudwatch.put_metric_data(
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
                    'Value': 1.0,
                    'Unit': 'Count'
                },
            ]
        )
