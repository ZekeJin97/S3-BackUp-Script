import json

import boto3
import os

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']
logger_lambda_name = os.environ['LOGGER_LAMBDA_NAME']
lambda_client = boto3.client('lambda')


def handler(event, context):
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        source_key = record['s3']['object']['key']
        copy_source = {'Bucket': source_bucket, 'Key': source_key}
        s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=source_key)
        print(f'Copied {source_key} from {source_bucket} to {destination_bucket}')

        # Invoke the logger lambda function
        try:
            response = lambda_client.invoke(
                FunctionName=logger_lambda_name,
                InvocationType='Event',
                Payload=json.dumps({'key': source_key}).encode('utf-8')
            )
            print(f'Invoked logger for {source_key}')
        except Exception as e:
            print(f'Error invoking Logger Lambda: {e}')
