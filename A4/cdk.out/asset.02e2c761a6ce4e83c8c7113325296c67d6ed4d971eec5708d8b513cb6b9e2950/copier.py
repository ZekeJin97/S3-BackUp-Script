import boto3
import os

s3 = boto3.client('s3')
source_bucket = os.environ['SOURCE_BUCKET']
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        source_key = record['s3']['object']['key']
        copy_source = {'Bucket': source_bucket, 'Key': source_key}
        destination_key = source_key

        s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=destination_key)
        print(f'Copied {source_key} to {destination_bucket}/{destination_key}')
