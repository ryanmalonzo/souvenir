from pydantic import BaseModel, EmailStr


class AuthIn(BaseModel):
    email: EmailStr
    password: str


class AuthVerifyIn(BaseModel):
    email: EmailStr
    token: str


class AuthOut(BaseModel):
    token: str
