from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    username: str
    email: str
    hashed_password: str
    created_at: int
    is_active: bool
    created_at: int
