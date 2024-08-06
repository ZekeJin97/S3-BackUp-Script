import json
import boto3
import os

s3_client = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        # Extract the S3 bucket and object key from the SQS message
        sns_message = json.loads(record['body'])
        s3_event = json.loads(sns_message['Message'])
        s3_bucket = s3_event['Bucket']
        s3_object_key = s3_event['Key']

        # Copy the object from the source bucket to the destination bucket
        copy_source = {'Bucket': s3_bucket, 'Key': s3_object_key}
        try:
            s3_client.copy_object(
                CopySource=copy_source,
                Bucket=destination_bucket,
                Key=s3_object_key
            )
            print(f'Successfully copied {s3_object_key} from {s3_bucket} to {destination_bucket}')
        except Exception as e:
            print(f'Error copying {s3_object_key} from {s3_bucket} to {destination_bucket}: {e}')
            raise e


