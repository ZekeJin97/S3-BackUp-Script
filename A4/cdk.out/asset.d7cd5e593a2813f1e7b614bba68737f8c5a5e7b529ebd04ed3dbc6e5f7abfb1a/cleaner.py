import boto3
import os
import json
from datetime import datetime

s3 = boto3.client('s3')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    for record in event['Records']:
        sqs_body = json.loads(record['body'])
        print("SQS body:", json.dumps(sqs_body, indent=2))

        sns_message = json.loads(sqs_body['Message'])
        print("SNS message:", json.dumps(sns_message, indent=2))

        # Handle test event
        if sns_message.get('Event') == 's3:TestEvent':
            print("Received test event, skipping processing.")
            continue

        # Check if 'Trigger' is present in sns_message
        if 'Trigger' not in sns_message:
            print("No 'Trigger' in SNS message, skipping.")
            continue

        metric_name = sns_message['Trigger']['MetricName']
        if metric_name == 'TotalTemporaryFileSize':
            delete_oldest_temporary_file()

def delete_oldest_temporary_file():
    response = s3.list_objects_v2(Bucket=DESTINATION_BUCKET)
    if 'Contents' in response:
        # Filter for temporary files
        temp_files = [obj for obj in response['Contents'] if 'temp' in obj['Key']]
        if not temp_files:
            print("No temporary files found to delete.")
            return

        # Find the oldest temporary file
        oldest_file = min(temp_files, key=lambda x: x['LastModified'])
        print(f"Deleting oldest temporary file: {oldest_file['Key']}")
        s3.delete_object(Bucket=DESTINATION_BUCKET, Key=oldest_file['Key'])
    else:
        print("No files found in the bucket.")
