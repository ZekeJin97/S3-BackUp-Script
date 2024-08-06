import boto3
import json
import os

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    for record in event['Records']:
        sns_message = json.loads(record['body'])
        s3_event = json.loads(sns_message['Message'])

        for s3_record in s3_event['Records']:
            source_bucket = s3_record['s3']['bucket']['name']
            source_key = s3_record['s3']['object']['key']

            copy_source = {'Bucket': source_bucket, 'Key': source_key}
            destination_key = source_key

            print(f'Copying object {source_key} from {source_bucket} to {destination_bucket}')
            s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=destination_key)
