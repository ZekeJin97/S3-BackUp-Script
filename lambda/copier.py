import boto3
import os

s3 = boto3.client('s3')

def handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    destination_bucket = os.environ['DESTINATION_BUCKET']

    copy_source = {'Bucket': source_bucket, 'Key': object_key}
    s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=object_key)

    print(f"Copied {object_key} from {source_bucket} to {destination_bucket}")
