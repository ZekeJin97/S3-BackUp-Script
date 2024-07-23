import boto3
import time

s3 = boto3.client('s3')
source_bucket = 'copierstack-sourcebucketddd2130a-vc3snocinfuo'  # replace with your actual source bucket name

def create_object(key, size_kb):

    size_bytes = int(size_kb * 1024)
    content = '0' * size_bytes
    s3.put_object(Bucket=source_bucket, Key=key, Body=content)


create_object('project.txt', 1)
time.sleep(60)
create_object('temp.txt', 1)
time.sleep(60)
create_object('project_new.txt', 1)
time.sleep(60)
create_object('temporary_data.txt', 2.5)
time.sleep(60)
create_object('project_new_new.txt', 1)
time.sleep(60)
create_object('real_temporary_data.txt', 2)
('real_temporary_data.txt', 2)
