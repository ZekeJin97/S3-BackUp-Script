import os
import boto3
import logging

s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        copy_source = {'Bucket': source_bucket, 'Key': key}

        try:
            s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=key)
            logger.info(f"Copied {key} from {source_bucket} to {destination_bucket}")
        except Exception as e:
            logger.error(f"Error copying {key} from {source_bucket} to {destination_bucket}: {str(e)}")
