import datetime
import os

import jwt
from fastapi import Depends, HTTPException, status
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from dependencies import SOUVENIR_EMAIL, get_session
from internal.mailer.mailer import Mailer, get_mailer
from models.auth import AuthIn, AuthOut
from models.user import User, UserCreate

JWT_EXPIRY_NB_DAYS = 3


class AuthManager:
    def __init__(
        self,
        session: Session = Depends(get_session),
        mailer: Mailer = Depends(get_mailer),
    ):
        self._session = session
        self._mailer = mailer

    def _encode_jwt(self, user: User):
        return jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(days=JWT_EXPIRY_NB_DAYS),
            },
            os.environ.get("JWT_SECRET"),
            algorithm="HS256",
        )

    def post_register(self, user: UserCreate) -> AuthOut:
        """Register a new user in database and return their authentication token."""

        try:
            db_user = User.model_validate(
                user, update={"hashed_password": bcrypt.hash(user.password)}
            )
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        self._session.add(db_user)

        try:
            self._session.commit()
            self._session.refresh(db_user)
        except IntegrityError:
            self._session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="email_already_registered"
            )

        self._mailer.send_email(
            "Welcome!",
            SOUVENIR_EMAIL,
            user.email,
            "welcome.html",
            {"email": user.email},
        )

        return AuthOut(token=self._encode_jwt(db_user))

    def post_login(self, credentials: AuthIn) -> AuthOut:
        """Login user and return their authentication token."""

        statement = select(User).where(User.email == credentials.email)
        db_user = self._session.exec(statement).first()

        if not db_user or not bcrypt.verify(
            credentials.password, db_user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
            )

        return AuthOut(token=self._encode_jwt(db_user))


def get_auth_manager(
    session: Session = Depends(get_session), mailer: Mailer = Depends(get_mailer)
) -> AuthManager:
    return AuthManager(session, mailer)
