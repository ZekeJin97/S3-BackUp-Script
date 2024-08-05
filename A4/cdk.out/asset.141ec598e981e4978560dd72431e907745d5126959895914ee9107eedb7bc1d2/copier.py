import boto3
import os

s3 = boto3.client('s3')
sns = boto3.client('sns')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def handler(event, context):
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        copy_source = {'Bucket': source_bucket, 'Key': key}
        s3.copy_object(Bucket=DESTINATION_BUCKET, CopySource=copy_source, Key=key)

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f'File {key} copied to {DESTINATION_BUCKET}',
            Subject='S3 File Copied'
        )
