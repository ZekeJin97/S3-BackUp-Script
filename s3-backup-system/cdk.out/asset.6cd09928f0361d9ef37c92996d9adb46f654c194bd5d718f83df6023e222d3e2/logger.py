import boto3
import os

cloudwatch = boto3.client('cloudwatch')
s3 = boto3.client('s3')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        s3_event = json.loads(sns_message)
        for s3_record in s3_event['Records']:
            key = s3_record['s3']['object']['key']
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
    response = s3.head_object(Bucket=DESTINATION_BUCKET, Key=key)
    return response['ContentLength']
