import datetime
import os
import secrets

import jwt
from fastapi import Depends, HTTPException, status
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from dependencies import SOUVENIR_EMAIL, get_session
from internal.mailer.mailer import Mailer, get_mailer
from models import User, UserCreate
from models.database import Token, TokenStatus
from models.pydantic.auth import AuthIn, AuthOut, AuthVerifyIn

JWT_EXPIRY_NB_DAYS = 3


class AuthManager:
    def __init__(
        self,
        session: Session = Depends(get_session),
        mailer: Mailer = Depends(get_mailer),
    ):
        self._session = session
        self._mailer = mailer

    def _store_token_in_db(
        self, user: User, token_name: TokenStatus, token: str
    ) -> None:
        if user.id is None:
            raise ValueError("User must be saved in database before storing token")

        user.tokens.append(Token(name=token_name, token=token, user_id=user.id))
        self._session.add(user)
        self._session.commit()

    def _send_welcome_email(self, user: User) -> None:
        """
        Send a welcome email to the user with a link to verify their account.
        """

        token = secrets.token_urlsafe(32)

        self._store_token_in_db(user, TokenStatus.email, token)

        activation_url = (
            f"{os.getenv('WEBAPP_URL')}/verify?token={token}&email={user.email}"
        )

        self._mailer.send_email(
            "Verify your Souvenir account",
            SOUVENIR_EMAIL,
            user.email,
            "welcome.html",
            {"email": user.email, "activation_url": activation_url},
        )

    def _encode_jwt(self, user: User) -> str:
        return jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(days=JWT_EXPIRY_NB_DAYS),
            },
            os.getenv("JWT_SECRET"),
            algorithm="HS256",
        )

    def post_register(self, user: UserCreate) -> None:
        """Register a new user in database and send them an email to verify their account."""

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

        self._send_welcome_email(db_user)

    def post_verify(self, auth: AuthVerifyIn) -> AuthOut:
        """Verify provided token and mark the user as verified."""

        statement = (
            select(Token).where(Token.name == "email").where(Token.token == auth.token)
        )
        db_token = self._session.exec(statement).first()

        if not db_token or db_token.verified:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="token_not_found"
            )

        db_token.verified = True
        db_token.updated_at = datetime.datetime.now(datetime.timezone.utc)

        self._session.add(db_token)
        self._session.commit()

        return AuthOut(token=self._encode_jwt(db_token.user))

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
