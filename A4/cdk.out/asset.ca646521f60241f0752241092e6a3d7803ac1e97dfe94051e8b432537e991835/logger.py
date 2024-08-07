import json
import boto3

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')


def handler(event, context):
    try:
        dest_bucket = "copiercleanerstack-destinationbucket4becdb47-ivopdizgy3ws"
        total_temp_size_key = "total_temp_size.txt"

        try:
            response = s3.get_object(Bucket=dest_bucket, Key=total_temp_size_key)
            total_temp_size = int(response['Body'].read().decode('utf-8'))
        except s3.exceptions.NoSuchKey:
            total_temp_size = 0

        for record in event['Records']:
            message = json.loads(record['body'])
            sns_message = json.loads(message['Message'])

            for sns_record in sns_message['Records']:
                s3_info = sns_record['s3']
                bucket_name = s3_info['bucket']['name']
                object_key = s3_info['object']['key']
                object_size = s3_info['object']['size']

                if "temp" in object_key:
                    total_temp_size += object_size

        s3.put_object(Bucket=dest_bucket, Key=total_temp_size_key, Body=str(total_temp_size))

        cloudwatch.put_metric_data(
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

    except Exception as e:
        print(f"Error processing S3 event: {e}")
