from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Boolean, Column
from sqlmodel import Enum as SQLModelEnum
from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(sa_column_kwargs={"unique": True})


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    tokens: list["Token"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str


class TokenStatus(str, Enum):
    email = "email"
    password_reset = "password_reset"


class Token(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: TokenStatus = Field(sa_column=Column(SQLModelEnum(TokenStatus)))
    token: str
    verified: Optional[bool] = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="tokens")
