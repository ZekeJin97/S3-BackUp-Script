import boto3
import os

s3 = boto3.client('s3')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    temp_objects = []

    # List all objects in the destination bucket
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=DESTINATION_BUCKET)

    for page in page_iterator:
        for obj in page.get('Contents', []):
            if 'temp' in obj['Key']:
                temp_objects.append(obj)

    # Find the oldest temp object
    if temp_objects:
        oldest_temp_object = min(temp_objects, key=lambda x: x['LastModified'])
        s3.delete_object(Bucket=DESTINATION_BUCKET, Key=oldest_temp_object['Key'])
        print(f"Deleted {oldest_temp_object['Key']}")
    else:
        print("No temporary objects found to delete")
