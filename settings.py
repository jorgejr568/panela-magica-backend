from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ''


@lru_cache
def settings() -> Settings:
    return Settings(_env_file='.env')
