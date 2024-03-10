from typing import BinaryIO


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
        import boto3
        from settings import settings
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

    def upload_fileobj(self, body: BinaryIO, bucket: str, key: str, **kwargs):
        self.__client.upload_fileobj(body, bucket, key, **kwargs)

    @classmethod
    def __destroy__(cls):
        cls.__instance = None
        cls.__client = None
        cls.__session = None


def upload_file(file: BinaryIO, key: str, public=True, mime_type=None) -> str:
    from settings import settings

    s3 = S3Client.get_instance()
    metadata = {
        'ACL': 'public-read' if public else 'private',
        'ContentType': mime_type if mime_type else 'application/octet-stream',
    }

    s3.upload_fileobj(file, settings().s3_bucket, key, ExtraArgs=metadata)
    return "{}/{}".format(settings().s3_cdn_url, key)
