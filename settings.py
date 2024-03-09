import binascii
from functools import lru_cache

from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str
    api_url: str
    storage_path: str = os.path.join(os.path.dirname(__file__), 'storage')
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_region: str
    s3_endpoint: str
    s3_cdn_url: str
    pdkdf2_salt: str = 'pdkdf2_salt'
    pdkdf2_rounds: int = 50000
    jwt_secret: str

    @lru_cache
    def pdkdf2_salt_bytes(self) -> bytes:
        return binascii.unhexlify(self.pdkdf2_salt)


# @lru_cache
def settings() -> Settings:
    return Settings(_env_file='.env')
