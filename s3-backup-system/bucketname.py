import boto3

s3_client = boto3.client('s3')

# List all buckets
response = s3_client.list_buckets()

# Print bucket names
print("Available buckets:")
for bucket in response['Buckets']:
    print(bucket['Name'])
