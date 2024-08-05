import os
import boto3

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
destination_bucket = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    print(f"Copier Lambda triggered with event: {event}")

    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']

        copy_source = {'Bucket': source_bucket, 'Key': key}
        s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=key)
        print(f"Copied {key} from {source_bucket} to {destination_bucket}")

        if 'temp' in key:
            print(f"Temporary object {key} of size {size} bytes")
            cloudwatch.put_metric_data(
                Namespace='S3BackupSystem',
                MetricData=[{
                    'MetricName': 'TemporaryObjectSize',
                    'Dimensions': [{'Name': 'BucketName', 'Value': destination_bucket}],
                    'Unit': 'Bytes',
                    'Value': size
                }]
            )
            print(f"Published metric data for {key}")
