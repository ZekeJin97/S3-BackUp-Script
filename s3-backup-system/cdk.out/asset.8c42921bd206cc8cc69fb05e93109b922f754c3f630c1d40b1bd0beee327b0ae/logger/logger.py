import boto3
import os

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
destination_bucket = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    key = event['key']
    if 'temp' in key:
        response = s3.head_object(Bucket=destination_bucket, Key=key)
        size = response['ContentLength']

        cloudwatch.put_metric_data(
            Namespace='S3BackupSystem',
            MetricData=[
                {
                    'MetricName': 'TemporaryObjectSize',
                    'Dimensions': [
                        {'Name': 'BucketName', 'Value': destination_bucket},
                    ],
                    'Unit': 'Bytes',
                    'Value': size
                },
            ]
        )
        print(f'Reported {size} bytes of temporary objects to CloudWatch')
