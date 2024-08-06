import boto3
import json
import os

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    for record in event['Records']:
        sqs_body = json.loads(record['body'])
        print("SQS body:", json.dumps(sqs_body, indent=2))

        sns_message = json.loads(sqs_body['Message'])
        print("SNS message:", json.dumps(sns_message, indent=2))

        # Check if 'Records' is present in sns_message to avoid KeyError
        if 'Records' in sns_message:
            for s3_record in sns_message['Records']:
                source_bucket = s3_record['s3']['bucket']['name']
                source_key = s3_record['s3']['object']['key']

                copy_source = {'Bucket': source_bucket, 'Key': source_key}
                destination_key = source_key

                print(f'Copying object {source_key} from {source_bucket} to {destination_bucket}')
                s3.copy_object(CopySource=copy_source, Bucket=destination_bucket,
                               Key=destination_key)
        else:
            print("No 'Records' in SNS message, skipping.")
