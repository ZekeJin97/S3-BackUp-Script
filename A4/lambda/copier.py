import boto3
import os
import json

s3 = boto3.client('s3')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def copy_object(key, bucket):
    try:
        copy_source = {
            'Bucket': bucket,
            'Key': key
        }
        s3.copy_object(CopySource=copy_source, Bucket=DESTINATION_BUCKET, Key=key)
        print(f"Successfully copied {key} from {bucket} to {DESTINATION_BUCKET}")
    except Exception as e:
        print(f"Error copying object {key} from {bucket} to {DESTINATION_BUCKET}: {e}")

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

        # Check if 'Records' is present in sns_message
        if 'Records' not in sns_message:
            print("No 'Records' in SNS message, skipping.")
            continue

        for s3_record in sns_message['Records']:
            s3_bucket = s3_record['s3']['bucket']['name']
            s3_key = s3_record['s3']['object']['key']

            print(f'Processing object key: {s3_key} from bucket: {s3_bucket}')

            copy_object(s3_key, s3_bucket)
