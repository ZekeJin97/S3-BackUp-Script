import boto3
import time

s3_client = boto3.client('s3')
source_bucket = 's3backupsystemstack-sourcebucketddd2130a-pxthiplfvjtk'

def create_object(key, size_kb):
    content = '0' * (1024 * int(size_kb))
    s3_client.put_object(Bucket=source_bucket, Key=key, Body=content)
    print(f"Uploaded {key} ({size_kb}KB)")

# Upload objects
create_object('project.txt', 1)
time.sleep(1)
create_object('temp.txt', 1)
time.sleep(1)
create_object('project_new.txt', 1)
time.sleep(1)
create_object('temporary_data.txt', 2.5)
time.sleep(1)
create_object('project_new_new.txt', 1)
time.sleep(1)
create_object('real_temporary_data.txt', 2)

print("All objects uploaded.")
