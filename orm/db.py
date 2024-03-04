from typing import Optional

from sqlalchemy import create_engine, Engine

from settings import settings


class EngineSingleton:
    _engine: Optional[Engine] = None

    @classmethod
    def get_engine(cls) -> Engine:
        if cls._engine is None:
            cls._engine = create_engine(settings().database_url, echo=True)
        return cls._engine

    @classmethod
    def close_engine(cls):
        if cls._engine is not None:
            cls._engine.dispose()
            cls._engine = None
            return True
        return False

    @classmethod
    def create_all(cls):
        cls.get_engine()
        from orm import BaseOrm
        BaseOrm.metadata.create_all(cls._engine)
        return True
