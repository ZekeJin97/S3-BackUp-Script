import boto3
import os

cloudwatch = boto3.client('cloudwatch')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    for record in event['Records']:
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']

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
                            },
                        ],
                        'Value': size,
                        'Unit': 'Bytes'
                    },
                ]
            )
