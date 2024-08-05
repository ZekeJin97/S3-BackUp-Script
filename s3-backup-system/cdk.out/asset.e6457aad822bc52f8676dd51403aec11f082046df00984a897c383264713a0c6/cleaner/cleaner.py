import boto3
import os
import json
from datetime import datetime

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']
QUEUE_URL = os.environ['QUEUE_URL']

def handler(event, context):
    messages = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=10)
    if 'Messages' in messages:
        for message in messages['Messages']:
            process_message()
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=message['ReceiptHandle'])

def process_message():
    temp_objects = list_temp_objects(DESTINATION_BUCKET)
    if temp_objects:
        oldest_object = min(temp_objects, key=lambda x: x['LastModified'])
        s3.delete_object(Bucket=DESTINATION_BUCKET, Key=oldest_object['Key'])
        print(f"Deleted oldest temp object: {oldest_object['Key']}")

def list_temp_objects(bucket_name):
    temp_objects = []
    response = s3.list_objects_v2(Bucket=bucket_name)
    while 'Contents' in response:
        for obj in response['Contents']:
            if 'temp' in obj['Key']:
                temp_objects.append(obj)
        if response['IsTruncated']:
            response = s3.list_objects_v2(Bucket=bucket_name, ContinuationToken=response['NextContinuationToken'])
        else:
            break
    return temp_objects
