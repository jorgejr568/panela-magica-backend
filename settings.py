from functools import lru_cache

from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str
    api_url: str
    storage_path: str = os.path.join(os.path.dirname(__file__), 'storage')


@lru_cache
def settings() -> Settings:
    return Settings(_env_file='.env')
