import json
import boto3

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')


def handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    try:
        dest_bucket = "copiercleanerstack-destinationbucket4becdb47-ivopdizgy3ws"
        total_temp_size_key = "total_temp_size.txt"

        # Initialize total_temp_size
        try:
            response = s3.get_object(Bucket=dest_bucket, Key=total_temp_size_key)
            total_temp_size = int(response['Body'].read().decode('utf-8'))
            print(f"Current total temporary file size: {total_temp_size} bytes")
        except s3.exceptions.NoSuchKey:
            total_temp_size = 0
            print("Total temporary file size key not found, initializing to 0.")

        for record in event['Records']:
            message = json.loads(record['body'])
            sns_message = json.loads(message['Message'])
            print("Processing SNS message:", json.dumps(sns_message, indent=2))

            for sns_record in sns_message['Records']:
                s3_info = sns_record['s3']
                object_key = s3_info['object']['key']
                object_size = s3_info['object']['size']

                print(f"Processing object key: {object_key}, size: {object_size} bytes")

                if "temp" in object_key:
                    total_temp_size += object_size
                    print(f"Temporary file detected. Updated total size: {total_temp_size} bytes")

        # Update the total size of temporary files in S3
        s3.put_object(Bucket=dest_bucket, Key=total_temp_size_key, Body=str(total_temp_size))
        print(f"Updated total_temp_size in S3: {total_temp_size} bytes")

        # Report the metric to CloudWatch
        response = cloudwatch.put_metric_data(
            Namespace='CopierCleaner',
            MetricData=[
                {
                    'MetricName': 'TotalTemporaryFileSize',
                    'Dimensions': [
                        {'Name': 'BucketName', 'Value': dest_bucket},
                    ],
                    'Value': total_temp_size,
                    'Unit': 'Bytes'
                },
            ]
        )
        print("CloudWatch metric response:", response)

        print(
            f"Successfully reported total temporary file size: {total_temp_size} bytes to CloudWatch")

    except Exception as e:
        print(f"Error processing S3 event: {e}")
