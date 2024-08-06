import boto3
import os

s3 = boto3.client('s3')
source_bucket_name = os.environ['SOURCE_BUCKET']
destination_bucket_name = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        s3_event = record['s3']
        bucket = s3_event['bucket']['name']
        key = s3_event['object']['key']

        if bucket == source_bucket_name:
            copy_source = {'Bucket': bucket, 'Key': key}
            print(f"Copying {key} from {source_bucket_name} to {destination_bucket_name}")
            s3.copy_object(CopySource=copy_source, Bucket=destination_bucket_name, Key=key)
        else:
            print(f"Ignoring event for bucket {bucket}")
