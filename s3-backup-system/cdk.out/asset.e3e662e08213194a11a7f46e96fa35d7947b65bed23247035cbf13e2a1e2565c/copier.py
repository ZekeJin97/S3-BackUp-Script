import boto3
import os

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        object_size = record['s3']['object']['size']

        # Copy the object to the destination bucket
        copy_source = {'Bucket': source_bucket, 'Key': object_key}
        s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=object_key)
        print(f"Copied {object_key} from {source_bucket} to {destination_bucket}")

        # If the object is a temporary file, update the CloudWatch metric
        if "temp" in object_key:
            print(f"Temporary object {object_key} of size {object_size} bytes")
            response = cloudwatch.put_metric_data(
                Namespace='S3BackupSystem',
                MetricData=[
                    {
                        'MetricName': 'TemporaryObjectSize',
                        'Dimensions': [
                            {
                                'Name': 'BucketName',
                                'Value': destination_bucket
                            },
                        ],
                        'Value': object_size,
                        'Unit': 'Bytes'
                    },
                ]
            )
            print(f"Published metric data: {response}")
