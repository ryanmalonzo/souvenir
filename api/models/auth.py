from pydantic import BaseModel, EmailStr


class AuthIn(BaseModel):
    email: EmailStr
    password: str


class AuthOut(BaseModel):
    token: str
