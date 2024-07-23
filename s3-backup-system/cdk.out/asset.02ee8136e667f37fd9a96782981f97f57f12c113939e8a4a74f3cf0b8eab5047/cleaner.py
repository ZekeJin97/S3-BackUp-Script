import boto3
import os

s3 = boto3.client('s3')

def handler(event, context):
    destination_bucket = os.environ['DESTINATION_BUCKET']
    temp_objects = []

    response = s3.list_objects_v2(Bucket=destination_bucket)

    for obj in response.get('Contents', []):
        if 'temp' in obj['Key']:
            temp_objects.append((obj['Key'], obj['LastModified']))

    if temp_objects:
        temp_objects.sort(key=lambda x: x[1])  # Sort by modification date
        oldest_temp = temp_objects[0][0]
        s3.delete_object(Bucket=destination_bucket, Key=oldest_temp)
        print(f"Deleted {oldest_temp} from {destination_bucket}")
