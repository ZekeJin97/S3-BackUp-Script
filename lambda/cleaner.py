import os
import boto3

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']


def handler(event, context):
    print(f"Cleaner Lambda triggered with event: {event}")

    # List objects in the destination bucket with 'temp' in the key
    response = s3.list_objects_v2(
        Bucket=destination_bucket,
        Prefix='' 
    )

    print(f"List objects response: {response}")

    # Filter to get only temporary files
    temp_files = [obj for obj in response.get('Contents', []) if 'temp' in obj['Key']]

    print(f"Temporary files: {temp_files}")

    if temp_files:
        # Find the oldest temporary object
        oldest = min(temp_files, key=lambda x: x['LastModified'])

        # Delete the oldest temporary object
        s3.delete_object(
            Bucket=destination_bucket,
            Key=oldest['Key']
        )
        print(f"Deleted {oldest['Key']}")
    else:
        print("No temporary objects found")
