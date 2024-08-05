import boto3
import os
import json

s3 = boto3.client('s3')
source_bucket = os.environ['SOURCE_BUCKET']
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))  # Debugging statement
    for record in event['Records']:
        sqs_message = json.loads(record['body'])  # Extract SQS message
        s3_event = json.loads(sqs_message['Message'])  # Extract the actual S3 event
        for s3_record in s3_event['Records']:
            if 's3' in s3_record:
                source_key = s3_record['s3']['object']['key']
                copy_source = {'Bucket': source_bucket, 'Key': source_key}
                destination_key = source_key

                s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=destination_key)
                print(f'Copied {source_key} to {destination_bucket}/{destination_key}')
            else:
                print(f'Unexpected S3 record format: {json.dumps(s3_record, indent=2)}')
