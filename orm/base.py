from typing import Generator, Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, declarative_base

from orm.db import EngineSingleton

BaseOrm = declarative_base()


def get_db(echo=True) -> Generator:
    with Session(EngineSingleton.get_engine(echo=echo), autoflush=True) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
