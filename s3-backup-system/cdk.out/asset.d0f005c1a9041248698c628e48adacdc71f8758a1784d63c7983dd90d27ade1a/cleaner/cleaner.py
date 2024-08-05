import boto3
import os

sqs = boto3.client('sqs')
s3 = boto3.client('s3')

QUEUE_URL = os.environ['QUEUE_URL']
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    # Retrieve messages from SQS queue
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    for message in response.get('Messages', []):
        # Process the message
        body = message['Body']

        # List objects in the destination bucket
        response = s3.list_objects_v2(
            Bucket=DESTINATION_BUCKET
        )

        # Find temporary files based on custom logic (e.g., extension or metadata)
        temporary_files = [obj for obj in response.get('Contents', []) if 'temp' in obj['Key']]

        if temporary_files:
            # Sort files by last modified date and delete the oldest one
            temporary_files.sort(key=lambda x: x['LastModified'])
            oldest_file = temporary_files[0]
            s3.delete_object(Bucket=DESTINATION_BUCKET, Key=oldest_file['Key'])
            print(f"Deleted {oldest_file['Key']}")

        # Delete the message from the queue
        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=message['ReceiptHandle']
        )
