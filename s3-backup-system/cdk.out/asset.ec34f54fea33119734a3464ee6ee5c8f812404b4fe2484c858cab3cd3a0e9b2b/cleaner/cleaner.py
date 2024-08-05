import os
import boto3
import logging

s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    response = s3.list_objects_v2(Bucket=destination_bucket)
    if 'Contents' in response:
        temp_objects = [obj for obj in response['Contents'] if 'temp' in obj['Key']]
        if temp_objects:
            # Sort the objects by last modified date, oldest first
            temp_objects.sort(key=lambda x: x['LastModified'])
            oldest_object = temp_objects[0]
            try:
                s3.delete_object(Bucket=destination_bucket, Key=oldest_object['Key'])
                logger.info(f"Deleted {oldest_object['Key']} from {destination_bucket}")
            except Exception as e:
                logger.error(f"Error deleting {oldest_object['Key']} from {destination_bucket}: {str(e)}")
