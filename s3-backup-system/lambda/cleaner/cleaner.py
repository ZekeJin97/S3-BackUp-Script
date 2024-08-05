import boto3
import os

s3 = boto3.client('s3')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    temp_objects = []

    # List all objects in the destination bucket
    response = s3.list_objects_v2(Bucket=DESTINATION_BUCKET)
    for obj in response.get('Contents', []):
        if 'temp' in obj['Key']:
            temp_objects.append(obj)

    # Find the oldest temp object
    if temp_objects:
        oldest_temp_object = min(temp_objects, key=lambda x: x['LastModified'])
        print(f"Deleting oldest temporary object: {oldest_temp_object['Key']}")
        s3.delete_object(Bucket=DESTINATION_BUCKET, Key=oldest_temp_object['Key'])
    else:
        print("No temporary objects found to delete.")
