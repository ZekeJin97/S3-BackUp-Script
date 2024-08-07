import boto3
import os

s3 = boto3.client('s3')
bucket_name = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    print("Cleaner triggered")
    response = s3.list_objects_v2(Bucket=bucket_name)

    if 'Contents' in response:
        for obj in response['Contents']:
            if 'temp' in obj['Key']:
                print(f"Deleting {obj['Key']} from bucket {bucket_name}")
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    else:
        print("No objects found in bucket")
