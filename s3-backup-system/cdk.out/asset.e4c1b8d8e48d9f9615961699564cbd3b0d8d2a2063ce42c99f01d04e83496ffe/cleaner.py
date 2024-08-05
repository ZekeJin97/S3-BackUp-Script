import boto3
import os

s3 = boto3.client('s3')

DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    # List objects in the destination bucket
    objects = s3.list_objects_v2(Bucket=DESTINATION_BUCKET)
    if 'Contents' in objects:
        temp_objects = [obj for obj in objects['Contents'] if 'temp' in obj['Key']]
        if temp_objects:
            # Find the oldest temporary object
            oldest_temp_object = min(temp_objects, key=lambda obj: obj['LastModified'])
            s3.delete_object(Bucket=DESTINATION_BUCKET, Key=oldest_temp_object['Key'])
            print(f'Deleted {oldest_temp_object["Key"]} from {DESTINATION_BUCKET}')
