import os
import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')

destination_bucket = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    logger.info(f"Copier Lambda triggered with event: {event}")

    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        source_key = record['s3']['object']['key']
        copy_source = {'Bucket': source_bucket, 'Key': source_key}

        # Copy the object
        s3.copy_object(Bucket=destination_bucket, Key=source_key, CopySource=copy_source)
        logger.info(f"Copied {source_key} from {source_bucket} to {destination_bucket}")

        # Check if the object is a temporary object
        if 'temp' in source_key:
            object_size = record['s3']['object']['size']
            logger.info(f"Temporary object {source_key} of size {object_size} bytes")

            # Publish the size to CloudWatch metric
            response = cloudwatch.put_metric_data(
                Namespace='S3BackupSystem',
                MetricData=[
                    {
                        'MetricName': 'TemporaryObjectSize',
                        'Dimensions': [
                            {
                                'Name': 'BucketName',
                                'Value': destination_bucket
                            },
                        ],
                        'Value': object_size,
                        'Unit': 'Bytes'
                    },
                ]
            )
            logger.info(f"Published metric data: {response}")

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
