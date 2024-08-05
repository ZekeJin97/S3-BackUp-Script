import boto3
import os

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')

DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']

        # Copy the object to the destination bucket
        copy_source = {'Bucket': source_bucket, 'Key': key}
        s3.copy_object(CopySource=copy_source, Bucket=DESTINATION_BUCKET, Key=key)

        # Check if the object is temporary
        if 'temp' in key:
            # Put metric data to CloudWatch
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
                        'Unit': 'Bytes',
                        'Value': size
                    }
                ]
            )
