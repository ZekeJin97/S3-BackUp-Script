import boto3
import os
import json

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']
TOTAL_TEMP_SIZE_KEY = "total_temp_size.txt"

def handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    for record in event['Records']:
        sqs_body = json.loads(record['body'])
        print("SQS body:", json.dumps(sqs_body, indent=2))

        sns_message = json.loads(sqs_body['Message'])
        print("SNS message:", json.dumps(sns_message, indent=2))

        # Handle test event
        if sns_message.get('Event') == 's3:TestEvent':
            print("Received test event, skipping processing.")
            continue

        # Check if 'Trigger' is present in sns_message
        if 'Trigger' not in sns_message:
            print("No 'Trigger' in SNS message, skipping.")
            continue

        metric_name = sns_message['Trigger']['MetricName']
        if metric_name == 'TotalTemporaryFileSize':
            delete_oldest_temporary_file()

def delete_oldest_temporary_file():
    try:
        response = s3.get_object(Bucket=DESTINATION_BUCKET, Key=TOTAL_TEMP_SIZE_KEY)
        total_temp_size = int(response['Body'].read().decode('utf-8'))
        print(f"Current total temporary file size: {total_temp_size} bytes")
    except s3.exceptions.NoSuchKey:
        total_temp_size = 0
        print("Total temporary file size key not found, initializing to 0.")

    response = s3.list_objects_v2(Bucket=DESTINATION_BUCKET)
    if 'Contents' in response:
        # Filter for temporary files
        temp_files = [obj for obj in response['Contents'] if 'temp' in obj['Key']]
        if not temp_files:
            print("No temporary files found to delete.")
            return

        # Find the oldest temporary file
        oldest_file = min(temp_files, key=lambda x: x['LastModified'])
        print(f"Deleting oldest temporary file: {oldest_file['Key']}")
        s3.delete_object(Bucket=DESTINATION_BUCKET, Key=oldest_file['Key'])

        # Update the total temporary file size
        total_temp_size -= oldest_file['Size']
        if total_temp_size < 0:
            total_temp_size = 0

        # Update the total size of temporary files in S3
        s3.put_object(Bucket=DESTINATION_BUCKET, Key=TOTAL_TEMP_SIZE_KEY, Body=str(total_temp_size))
        print(f"Updated total_temp_size in S3: {total_temp_size} bytes")

        # Report the metric to CloudWatch
        response = cloudwatch.put_metric_data(
            Namespace='CopierCleaner',
            MetricData=[
                {
                    'MetricName': 'TotalTemporaryFileSize',
                    'Dimensions': [
                        {'Name': 'BucketName', 'Value': DESTINATION_BUCKET},
                    ],
                    'Value': total_temp_size,
                    'Unit': 'Bytes'
                },
            ]
        )
        print("CloudWatch metric response:", response)
        print(f"Successfully reported total temporary file size: {total_temp_size} bytes to CloudWatch")

    else:
        print("No files found in the bucket.")
