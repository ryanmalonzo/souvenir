from fastapi import Depends, HTTPException, status
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from dependencies import get_session
from models.user import User, UserCreate


class AuthManager:
    def __init__(self, session: Session = Depends(get_session)):
        self._session = session

    def post_register(self, user: UserCreate):
        """Register a new user in database."""

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


def get_auth_manager(session: Session = Depends(get_session)) -> AuthManager:
    return AuthManager(session)
