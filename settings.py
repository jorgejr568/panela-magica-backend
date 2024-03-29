import binascii

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    api_url: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_region: str
    s3_endpoint: str
    s3_cdn_url: str
    pdkdf2_salt: str = 'aaef2d3f4d77ac66e9c5a6c3d8f921d1'
    pdkdf2_rounds: int = 50000
    jwt_secret: str = 'jwt_secret'
    jwt_expire_seconds: int = 3600
    jwt_issuer: str = 'panela-magica'
    jwt_audience: str = 'urn:panela-magica-api'
    jwt_algorithm: str = 'HS256'

    def pdkdf2_salt_bytes(self) -> bytes:
        return binascii.unhexlify(self.pdkdf2_salt)


# @lru_cache
def settings() -> Settings:
    return Settings(_env_file='.env')
