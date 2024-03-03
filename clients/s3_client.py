from typing import BinaryIO

import boto3
from settings import settings


class S3Client:
    __instance = None
    __client = None
    __session = None

    @staticmethod
    def get_instance():
        if S3Client.__instance == None:
            S3Client()
        return S3Client.__instance

    def __init__(self):
        if S3Client.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            S3Client.__instance = self
            self.__session = boto3.session.Session()
            self.__client = self.__session.client('s3',
                        region_name=settings().s3_region,
                        endpoint_url=settings().s3_endpoint,
                        aws_access_key_id=settings().s3_access_key,
                        aws_secret_access_key=settings().s3_secret_key)

    def upload_file(self, data: BinaryIO, path: str) -> str:
        metadata = {
            'ContentType': 'image/jpeg',
            'ACL': 'public-read',
        }
        self.__client.upload_fileobj(data, settings().s3_bucket, path, ExtraArgs=metadata)
        return "{}/{}".format(settings().s3_cdn_url, path)
