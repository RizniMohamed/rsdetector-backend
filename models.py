from pydantic import BaseModel


class User(BaseModel):
    password: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str

class UserIn(BaseModel):
    email: str
    password: str