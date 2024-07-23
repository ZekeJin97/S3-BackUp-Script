import boto3
import os

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    # Get all objects from the destination bucket
    response = s3.list_objects_v2(Bucket=destination_bucket)

    if 'Contents' in response:
        # Filter objects that contain 'temp' in their key
        temp_objects = [obj for obj in response['Contents'] if 'temp' in obj['Key']]

        if temp_objects:
            # Find the oldest object with 'temp' in its key
            oldest_temp_object = min(temp_objects, key=lambda x: x['LastModified'])

            # Delete the oldest object
            s3.delete_object(Bucket=destination_bucket, Key=oldest_temp_object['Key'])
            print(f"Deleted {oldest_temp_object['Key']}")
        else:
            print("No temporary objects found to delete")
    else:
        print("No objects found in the bucket")
