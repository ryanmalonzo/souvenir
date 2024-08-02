from fastapi import APIRouter, Depends, status

from internal.auth import AuthManager, get_auth_manager
from models import UserCreate
from models.pydantic.auth import AuthIn, AuthOut, AuthVerifyIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def post_register(
    user: UserCreate, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Register a new user in database and send them an email to verify their account."""

    return auth_manager.post_register(user)


@router.post("/verify", status_code=status.HTTP_200_OK, response_model=AuthOut)
def post_verify(
    auth: AuthVerifyIn, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Verify user account with the token received in their email."""

    return auth_manager.post_verify(auth)


@router.post("/login", response_model=AuthOut)
def post_login(
    credentials: AuthIn, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Login user and return their authentication token."""

    return auth_manager.post_login(credentials)
