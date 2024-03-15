from pydantic import ValidationError
from sqlalchemy.orm import Session
from orm.base import get_db
from models import CreateUserRequest, CreateUserResponse
from services import user_service, UserAlreadyExistsError


def create_user(session: Session, request: CreateUserRequest) -> CreateUserResponse:
    return user_service.create_user(request, session)


if __name__ == '__main__':
    session = next(get_db())

    try:
        request = CreateUserRequest(
            name=input('Name: '),
            username=input('Username: '),
            email=input('Email: '),
            password=input('Password: '),
        )

        response = create_user(session, request)
        print("User created successfully! User ID:", response.id)
    except ValidationError as e:
        for error in e.errors():
            print(error['loc'], error['msg'])
    except UserAlreadyExistsError:
        print("User already exists")

