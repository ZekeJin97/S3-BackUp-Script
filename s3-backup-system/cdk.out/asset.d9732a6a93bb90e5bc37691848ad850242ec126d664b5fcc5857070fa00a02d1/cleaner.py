import boto3
import os

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    # Check if the alarm state is ALARM
    if event.get('detail-type') == 'CloudWatch Alarm State Change':
        alarm_state = event['detail']['state']['value']
        if alarm_state != 'ALARM':
            print(f"Alarm state is {alarm_state}, not ALARM. Exiting.")
            return

    # Get all objects with 'temp' in their key from the destination bucket
    response = s3.list_objects_v2(
        Bucket=destination_bucket,
        Prefix='temp'
    )

    if 'Contents' in response:
        # Sort objects by last modified date
        sorted_objects = sorted(response['Contents'], key=lambda obj: obj['LastModified'])
        # Get the oldest object key
        oldest_temp_object = sorted_objects[0]['Key']

        # Delete the oldest object
        s3.delete_object(Bucket=destination_bucket, Key=oldest_temp_object)
        print(f"Deleted {oldest_temp_object}")
    else:
        print("No temporary objects found to delete.")
