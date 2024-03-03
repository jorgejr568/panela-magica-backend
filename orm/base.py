from typing import Generator, Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from settings import settings

BaseOrm = declarative_base()

engine = create_engine(settings().database_url)


def get_db() -> Generator:
    with Session(engine) as session:
        yield session

with open('orm/base.py', 'r') as file:
    code = file.read()
    exec(code)
SessionDep = Annotated[Session, Depends(get_db)]