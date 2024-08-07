import json
import boto3
import os

s3 = boto3.client('s3')
destination_bucket_name = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    for record in event['Records']:
        sns_message = json.loads(record['body'])
        s3_event = json.loads(sns_message['Message'])
        if 'Records' in s3_event:
            for s3_record in s3_event['Records']:
                s3_bucket = s3_record['s3']['bucket']['name']
                s3_object = s3_record['s3']['object']['key']
                copy_source = {'Bucket': s3_bucket, 'Key': s3_object}
                destination_key = s3_object
                s3.copy_object(Bucket=destination_bucket_name, CopySource=copy_source, Key=destination_key)
                print(f"Copied {s3_object} from {s3_bucket} to {destination_bucket_name}/{destination_key}")
