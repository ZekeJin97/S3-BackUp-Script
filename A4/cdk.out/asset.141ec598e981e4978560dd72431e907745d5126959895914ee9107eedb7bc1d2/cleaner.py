import boto3
import os

s3 = boto3.client('s3')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    temp_objects = []

    response = s3.list_objects_v2(Bucket=DESTINATION_BUCKET)
    for obj in response.get('Contents', []):
        if 'temp' in obj['Key']:
            temp_objects.append(obj)

    if temp_objects:
        oldest_temp_object = min(temp_objects, key=lambda x: x['LastModified'])
        s3.delete_object(Bucket=DESTINATION_BUCKET, Key=oldest_temp_object['Key'])
