import boto3
import os
import json

cloudwatch = boto3.client('cloudwatch')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        sns_message = json.loads(record['Sns']['Message'])
        key = sns_message['key']

        # Assume the size of the object can be fetched or is part of the message
        # Here we just use a placeholder value
        size = get_object_size(key)

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

def get_object_size(key):
    # Fetch object size logic
    s3 = boto3.client('s3')
    response = s3.head_object(Bucket=DESTINATION_BUCKET, Key=key)
    return response['ContentLength']
