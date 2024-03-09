from models.user import User
from repositories import user_repository
from pydantic import BaseModel


def _hash_password(password: str) -> str:
    from backports.pbkdf2 import pbkdf2_hmac
    from settings import settings
    return pbkdf2_hmac(
        "sha256",
        password.encode('utf-8'),
        settings().pdkdf2_salt_bytes(),
        settings().pdkdf2_rounds,
    ).hex()


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return _hash_password(plain_password) == hashed_password


def _generate_token(user: User) -> str:
    import jwt
    from settings import settings
    return jwt.encode(
        {
            'id': user.id,
            'name': user.name,
        },
        settings().jwt_secret,
        algorithm='HS256',
    )


def sign_in(username: str, password: str) -> 'SignInResponse' or None:
    user = user_repository.get_user_by_email_or_username(username)
    if not user:
        raise CredentialsNotMatchError()

    if not _verify_password(password, user.hashed_password):
        raise CredentialsNotMatchError()

    token = _generate_token(user)

    return SignInResponse(
        id=user.id,
        token=token,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
    )


class SignInResponse(BaseModel):
    id: int
    token: str
    username: str
    email: str
    created_at: int


class CredentialsNotMatchError(Exception):
    def __init__(self, message: str = 'Credentials not match'):
        self.message = message
        super().__init__(self.message)