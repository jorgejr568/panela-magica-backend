import email_validator
from pydantic import BaseModel, field_validator


class User(BaseModel):
    id: int
    name: str
    username: str
    email: str
    hashed_password: str
    created_at: int
    is_active: bool
    created_at: int


class CreateUserRequest(BaseModel):
    name: str
    username: str
    email: str
    password: str

    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('name must not be empty')
        return v

    @field_validator('username')
    def username_must_be_lower_cased_and_have_at_least_4_characters(cls, v):
        if not v:
            raise ValueError('username must not be empty')
        if len(v) < 4:
            raise ValueError('username must have at least 8 characters')
        if not v.islower():
            raise ValueError('username must be lower cased')
        return v

    @field_validator('email')
    def email_must_be_a_valid_email(cls, v):
        if not v:
            raise ValueError('email must not be empty')
        try:
            email_validator.validate_email(v)
        except email_validator.EmailNotValidError:
            raise ValueError('email must be a valid email')
        return v

    @field_validator('password')
    def password_must_have_at_least_8_characters(cls, v):
        if not v:
            raise ValueError('password must not be empty')
        if len(v) < 8:
            raise ValueError('password must have at least 8 characters')
        return v


class CreateUserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str
    created_at: int
    is_active: bool

    @staticmethod
    def from_dto(user: User) -> 'CreateUserResponse':
        return CreateUserResponse(
            id=user.id,
            name=user.name,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active,
        )
