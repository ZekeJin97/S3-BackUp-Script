import boto3
import os
import json

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))  # Debugging statement
    objects_to_delete = []
    response = s3.list_objects_v2(Bucket=destination_bucket)
    if 'Contents' in response:
        for obj in response['Contents']:
            if 'temp' in obj['Key']:
                objects_to_delete.append({'Key': obj['Key']})

    if objects_to_delete:
        delete_response = s3.delete_objects(
            Bucket=destination_bucket,
            Delete={'Objects': objects_to_delete}
        )
        print(f'Deleted {len(objects_to_delete)} temporary files')
