import boto3
import os
from dotenv import load_dotenv
from temporalio.common import RetryPolicy
from datetime import timedelta

load_dotenv()

def get_s3_path():
    return boto3.client(
        's3', 
        region_name = os.environ['AWS_REGION'],
        aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'],
        endpoint_url = os.environ['AWS_S3_ENDPOINT_URL']
    )

def parse_s3_path(s3_path:str):
    s3_path_no_scheme = s3_path.replace("s3://",'')
    bucket,_,key = s3_path_no_scheme.partition('/')
    return bucket,key

def save_job_description(
    job_id: str,
    job_description: str,
    bucket: str = "ats"
) -> str:

    s3_client = get_s3_path()

    key = f"jobs/{job_id}.txt"

    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=job_description.encode("utf-8"),
        ContentType="text/plain"
    )

    return f"s3://{bucket}/{key}"


def get_job_description(
    job_id: str,
    bucket: str = "ats"
) -> str:

    s3_client = get_s3_path()

    key = f"jobs/{job_id}.txt"

    response = s3_client.get_object(
        Bucket=bucket,
        Key=key
    )

    return response["Body"].read().decode("utf-8")