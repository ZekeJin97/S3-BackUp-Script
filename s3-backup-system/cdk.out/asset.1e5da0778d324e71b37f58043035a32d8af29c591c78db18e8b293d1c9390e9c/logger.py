import json
import boto3
import os

s3 = boto3.client('s3')
cloudwatch = boto3.client('cloudwatch')
DESTINATION_BUCKET = os.environ['DESTINATION_BUCKET']

def get_object_size(key):
    try:
        response = s3.head_object(Bucket=DESTINATION_BUCKET, Key=key)
        return response['ContentLength']
    except Exception as e:
        print(f"Error getting object size: {e}")
        return None


def handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    try:
        for record in event['Records']:
            sns_message = json.loads(record['Sns']['Message'])
            for s3_record in sns_message['Records']:
                key = s3_record['s3']['object']['key']
                print(f"Processing object key: {key}")

                size = get_object_size(key)
                if size is not None:
                    print(f"Object size: {size}")
                    if 'temp' in key:
                        print(f"Putting metric for temporary object: {key}")
                        cloudwatch.put_metric_data(
                            Namespace='S3BackupSystem',
                            MetricData=[
                                {
                                    'MetricName': 'TemporaryObjectSize',
                                    'Dimensions': [
                                        {
                                            'Name': 'BucketName',
                                            'Value': DESTINATION_BUCKET
                                        },
                                    ],
                                    'Value': size,
                                    'Unit': 'Bytes'
                                },
                            ]
                        )
                else:
                    print(f"Size for key {key} is None")
    except KeyError as e:
        print(f"Skipping non-S3 event: {e}")
    except Exception as e:
        print(f"Error processing record: {e}")
