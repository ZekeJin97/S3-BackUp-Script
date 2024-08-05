import boto3
import time

s3 = boto3.client('s3')
source_bucket = 'copierstack-sourcebucketddd2130a-zkenaqgjgtw6'  # Replace with your source bucket name

def create_object(key, size_kb):
    if size_kb == 2.5:
        content = '0' * 1024 * 2 + '0' * 512  # 2 KB + 0.5 KB
    else:
        content = '0' * 1024 * int(size_kb)  # Convert size_kb to an integer
    s3.put_object(Bucket=source_bucket, Key=key, Body=content)
    print(f"Created object {key} of size {size_kb} KB in {source_bucket}")

# Create objects with delays
create_object('project.txt', 1)
time.sleep(50)
create_object('temp.txt', 1)
time.sleep(50)
create_object('project_new.txt', 1)
time.sleep(50)
create_object('temporary_data.txt', 2.5)
time.sleep(50)
create_object('project_new_new.txt', 1)
time.sleep(50)
create_object('real_temporary_data.txt', 2)