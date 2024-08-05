import boto3
import os
import time

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    print(f"Cleaner Lambda triggered with event: {event}")

    # Introduce a slight delay to ensure metric reporting is accurate
    time.sleep(10)

    # Get all objects with 'temp' in their key from the destination bucket
    response = s3.list_objects_v2(
        Bucket=destination_bucket,
        Prefix='temp'
    )

    if 'Contents' not in response:
        print("No temporary objects found.")
        return

    # Sort objects by LastModified date (oldest first)
    objects = sorted(response['Contents'], key=lambda obj: obj['LastModified'])

    total_temp_size = sum(obj['Size'] for obj in objects)
    print(f"Total size of temporary objects: {total_temp_size} bytes")

    # Delete objects until the total size is below the threshold
    for obj in objects:
        if total_temp_size <= 3 * 1024:
            break
        s3.delete_object(Bucket=destination_bucket, Key=obj['Key'])
        total_temp_size -= obj['Size']
        print(f"Deleted {obj['Key']} of size {obj['Size']} bytes")
