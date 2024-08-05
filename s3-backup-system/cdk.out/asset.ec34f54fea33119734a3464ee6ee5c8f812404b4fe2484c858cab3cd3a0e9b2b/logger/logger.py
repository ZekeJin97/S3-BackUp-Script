import json
import boto3
import os

cloudwatch = boto3.client('cloudwatch')
s3 = boto3.client('s3')

def handler(event, context):
    destination_bucket = os.environ['DESTINATION_BUCKET']
    total_temp_size = 0

    # List objects in the destination bucket
    response = s3.list_objects_v2(Bucket=destination_bucket)

    # Calculate total size of temporary objects
    if 'Contents' in response:
        for obj in response['Contents']:
            if 'temp' in obj['Key']:
                total_temp_size += obj['Size']

    # Put the metric data to CloudWatch
    cloudwatch.put_metric_data(
        Namespace='S3BackupSystem',
        MetricData=[
            {
                'MetricName': 'TemporaryObjectSize',
                'Dimensions': [
                    {
                        'Name': 'BucketName',
                        'Value': destination_bucket
                    }
                ],
                'Value': total_temp_size,
                'Unit': 'Bytes'
            }
        ]
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Reported {} bytes of temporary objects to CloudWatch'.format(total_temp_size))
    }
