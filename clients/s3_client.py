from typing import BinaryIO

import boto3
from settings import settings

session = boto3.session.Session()
client = session.client('s3',
                        region_name=settings().s3_region,
                        endpoint_url=settings().s3_endpoint,
                        aws_access_key_id=settings().s3_access_key,
                        aws_secret_access_key=settings().s3_secret_key)


def upload_file(data: BinaryIO, path: str) -> str:
    metadata = {
        'ContentType': 'image/jpeg',
        'ACL': 'public-read',
    }
    client.upload_fileobj(data, settings().s3_bucket, path, ExtraArgs=metadata)
    return "{}/{}".format(settings().s3_cdn_url, path)