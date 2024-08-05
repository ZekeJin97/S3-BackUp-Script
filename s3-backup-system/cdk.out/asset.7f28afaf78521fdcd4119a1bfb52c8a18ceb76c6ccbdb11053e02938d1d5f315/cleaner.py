import boto3
import os
import json

s3 = boto3.client('s3')
sqs = boto3.client('sqs')
destination_bucket = os.environ['DESTINATION_BUCKET']
queue_url = os.environ['QUEUE_URL']

def handler(event, context):
    for record in event['Records']:
        message = json.loads(record['body'])
        if message['detail']['state']['value'] == 'ALARM':
            # List all objects in the destination bucket
            response = s3.list_objects_v2(Bucket=destination_bucket)
            if 'Contents' in response:
                temp_objects = [obj for obj in response['Contents'] if 'temp' in obj['Key']]
                # Sort temp objects by last modified time
                temp_objects.sort(key=lambda x: x['LastModified'])
                # Delete the oldest temp object
                if temp_objects:
                    oldest_temp = temp_objects[0]
                    s3.delete_object(Bucket=destination_bucket, Key=oldest_temp['Key'])
                    print(f"Deleted {oldest_temp['Key']}")
