from typing import Optional

from sqlalchemy import create_engine, Engine

from settings import settings


class EngineSingleton:
    _engine: Optional[Engine] = None

    @classmethod
    def get_engine(cls, echo=True) -> Engine:
        if cls._engine is None:
            cls._engine = create_engine(settings().database_url, echo=echo)
        return cls._engine

    @classmethod
    def close_engine(cls):
        if cls._engine is not None:
            cls._engine.dispose()
            cls._engine = None
            return True
        return False
