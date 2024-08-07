import json
import boto3

s3 = boto3.client('s3')


def handler(event, context):
    try:
        # Read the total_temp_size.txt file from the destination bucket
        dest_bucket = "copiercleanerstack-destinationbucket4becdb47-ivopdizgy3ws"
        total_temp_size_key = "total_temp_size.txt"

        try:
            response = s3.get_object(Bucket=dest_bucket, Key=total_temp_size_key)
            total_temp_size = int(response['Body'].read().decode('utf-8'))
        except s3.exceptions.NoSuchKey:
            total_temp_size = 0

        print(f"Current total temporary files size: {total_temp_size}")

        # Process the incoming event
        for record in event['Records']:
            message = json.loads(record['body'])
            sns_message = json.loads(message['Message'])

            for sns_record in sns_message['Records']:
                s3_info = sns_record['s3']
                bucket_name = s3_info['bucket']['name']
                object_key = s3_info['object']['key']
                object_size = s3_info['object']['size']

                print(f"Processing object key: {object_key} from bucket: {bucket_name}")

                # Update total_temp_size if the file is a temporary file
                if "temporary" in object_key:
                    total_temp_size += object_size
                    print(
                        f"Added {object_size} to total temporary files size. New total: {total_temp_size}")

                # Handle non-temporary files (logging purpose)
                else:
                    print(
                        f"Non-temporary file {object_key} processed. No change to total temporary files size.")

        # Write the updated total_temp_size back to the destination bucket
        s3.put_object(Bucket=dest_bucket, Key=total_temp_size_key, Body=str(total_temp_size))
        print(f"Updated total_temp_size.txt in {dest_bucket}")

    except Exception as e:
        print(f"Error processing S3 event: {e}")

