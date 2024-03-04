from typing import Generator, Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from orm.db import EngineSingleton

BaseOrm = declarative_base()


def get_db() -> Generator:
    with Session(EngineSingleton.get_engine(), autoflush=True) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]