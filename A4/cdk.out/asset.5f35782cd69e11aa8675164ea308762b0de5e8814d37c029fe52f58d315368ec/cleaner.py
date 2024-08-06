import boto3
import os
import json

s3 = boto3.client('s3')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    for record in event['Records']:
        sns_message = json.loads(record['body'])
        alarm_message = json.loads(sns_message['Message'])

        # Process the CloudWatch alarm message
        if 'Trigger' in alarm_message:
            metric_name = alarm_message['Trigger']['MetricName']
            if metric_name == 'TemporaryObjectSize':
                delete_temporary_files()


def delete_temporary_files():
    response = s3.list_objects_v2(Bucket=DESTINATION_BUCKET)
    if 'Contents' in response:
        for obj in response['Contents']:
            if 'temp' in obj['Key']:
                print(f"Deleting temporary file: {obj['Key']}")
                s3.delete_object(Bucket=DESTINATION_BUCKET, Key=obj['Key'])
