import boto3
import logging
from botocore.exceptions import ClientError
from aws_config import access_key, secret_key

filename = input("Input your filename?")
bucket = input("What S3 bucket do you want to upload to?")

s3_client = boto3.client('s3', 
    aws_access_key_id = access_key, 
    aws_secret_access_key = secret_key)

try:
    response = s3_client.upload_file(filename, bucket, filename)
    s3_client.put_object_acl(ACL='public-read', Bucket=bucket, Key=filename)
except ClientError as e:
    logging.error(e)
    print("Error")

print("Success")
