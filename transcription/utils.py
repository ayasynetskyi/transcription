import io
import json

import boto3
import requests


def check_url_exsits(url: str) -> bool:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.RequestException:
        return False
    return True


def upload_url_to_s3(url: str, bucket_name: str, key: str):
    """Upload file by url to s3."""
    bucket = boto3.resource("s3").Bucket(bucket_name)
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        bucket.upload_fileobj(
            Fileobj=response.raw,
            Key=key,
        )


def read_json_from_s3(uri: str):
    """Read and parse json file fom s3 by its uri."""
    bucket_name, key = uri.split("/", 3)[-1].split("/", 1)
    bucket = boto3.resource("s3").Bucket(bucket_name)
    transcription_json = io.BytesIO()
    bucket.download_fileobj(key, transcription_json)
    transcription_json.seek(0)
    return json.load(transcription_json)
