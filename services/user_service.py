import binascii

from pydantic import BaseModel

from models.user import User
from repositories import user_repository


def _hash_password(password: str) -> str:
    from backports.pbkdf2 import pbkdf2_hmac
    from settings import settings
    key = pbkdf2_hmac(
        "sha256",
        password.encode('utf-8'),
        settings().pdkdf2_salt_bytes(),
        settings().pdkdf2_rounds,
    )

    return binascii.hexlify(key).decode('utf-8')


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return _hash_password(plain_password) == hashed_password


def _generate_token(user: User) -> str:
    import jwt
    from settings import settings
    from datetime import datetime, timedelta

    return jwt.encode(
        {
            'id': user.id,
            'name': user.name,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=settings().jwt_expire_seconds),
            'iss': settings().jwt_issuer,
            'aud': [settings().jwt_audience],
        },
        settings().jwt_secret,
        algorithm=settings().jwt_algorithm,
    )


def _validate_token(token: str, session=None) -> 'User':
    import jwt
    from settings import settings

    try:
        payload = jwt.decode(
            token,
            settings().jwt_secret,
            algorithms=[settings().jwt_algorithm],
            audience=settings().jwt_audience,
            issuer=settings().jwt_issuer,
        )
        user = user_repository.get_user_by_id(session, payload['id'])
        if not user:
            raise InvalidTokenError()
        return user
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()


def sign_in(username: str, password: str, session=None) -> 'SignInResponse' or None:
    user = user_repository.get_user_by_email_or_username(session, username)
    if not user:
        raise CredentialsNotMatchError()

    if not _verify_password(password, user.hashed_password):
        raise CredentialsNotMatchError()

    token = _generate_token(user)

    return SignInResponse(
        id=user.id,
        name=user.name,
        token=token,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
    )


def me(token: str, session=None) -> 'MeResponse':
    user = _validate_token(token, session)
    return MeResponse(
        id=user.id,
        name=user.name,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
    )


class SignInResponse(BaseModel):
    id: int
    name: str
    token: str
    username: str
    email: str
    created_at: int


class MeResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str
    created_at: int


class SignInRequest(BaseModel):
    username: str
    password: str


class CredentialsNotMatchError(Exception):
    def __init__(self, message: str = 'Credentials not match'):
        self.message = message
        super().__init__(self.message)


class TokenExpiredError(Exception):
    def __init__(self, message: str = 'Token expired'):
        self.message = message
        super().__init__(self.message)


class InvalidTokenError(Exception):
    def __init__(self, message: str = 'Invalid token'):
        self.message = message
        super().__init__(self.message)
