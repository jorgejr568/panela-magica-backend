from sqlalchemy.orm import Session
from sqlalchemy.sql import select, operators

from models import User as UserModel, CreateUserRequest
from orm import User as UserOrm


def get_user_by_email_or_username(session: Session, email_or_username: str) -> UserModel or None:
    stmp = select(
        UserOrm
    ).filter(
        operators.and_(
            operators.eq(UserOrm.is_active, True),
            operators.or_(
                UserOrm.email == email_or_username,
                UserOrm.username == email_or_username,
            ),
        ),
    )

    user = session.execute(stmp).scalar()
    return user.to_dto() if user else None


def get_user_by_id(session: Session, user_id: int) -> UserModel or None:
    user = session.execute(select(UserOrm).filter(UserOrm.id == user_id)).scalar()
    return user.to_dto() if user else None


def create_user(session: Session, user: CreateUserRequest) -> UserModel:
    user = UserOrm(
        name=user.name,
        username=user.username,
        email=user.email,
        hashed_password=user.password,
        is_active=True,
    )

    session.add(user)
    session.commit()
    return user.to_dto()
