import json
import boto3
import os
import logging
from datetime import datetime

# Initialize clients
s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
lambda_client = boto3.client('lambda')
destination_bucket = os.environ['DESTINATION_BUCKET']
logger_lambda_name = os.environ['LOGGER_LAMBDA_NAME']

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    total_temp_size = 0

    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        if 'temp' in key:
            # Get the object size
            try:
                response = s3.head_object(Bucket=source_bucket, Key=key)
                object_size = response['ContentLength']
                total_temp_size += object_size

                # Copy the object to the destination bucket
                copy_source = {'Bucket': source_bucket, 'Key': key}
                s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=key)
                logger.info(f"Copied {key} from {source_bucket} to {destination_bucket}")

                # Log the copy event
                log_event({
                    'event': 'COPY',
                    'source_bucket': source_bucket,
                    'destination_bucket': destination_bucket,
                    'key': key,
                    'size': object_size
                })
            except Exception as e:
                logger.error(f"Error processing {key}: {e}")
                # Log the error event
                log_event({
                    'event': 'ERROR',
                    'source_bucket': source_bucket,
                    'destination_bucket': destination_bucket,
                    'key': key,
                    'error': str(e)
                })

    # Report the total size of temp objects to CloudWatch
    try:
        cloudwatch.put_metric_data(
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
                    'Timestamp': datetime.utcnow(),
                    'Value': total_temp_size,
                    'Unit': 'Bytes'
                },
            ]
        )
        logger.info(f"Reported {total_temp_size} bytes of temporary objects to CloudWatch")
    except Exception as e:
        logger.error(f"Error reporting to CloudWatch: {e}")
        # Log the error event
        log_event({
            'event': 'ERROR',
            'source_bucket': source_bucket,
            'destination_bucket': destination_bucket,
            'error': str(e)
        })


def log_event(event):
    try:
        lambda_client.invoke(
            FunctionName=logger_lambda_name,
            InvocationType='Event',
            Payload=json.dumps(event)
        )
    except Exception as e:
        logger.error(f"Error invoking Logger Lambda: {e}")
