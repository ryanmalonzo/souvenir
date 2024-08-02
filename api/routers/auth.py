from fastapi import APIRouter, Depends, status

from internal.auth import AuthManager, get_auth_manager
from models import UserCreate
from models.pydantic.auth import AuthIn, AuthOut

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
def post_register(
    user: UserCreate, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Register a new user in database and return their authentication token."""

    return auth_manager.post_register(user)


@router.post("/login", response_model=AuthOut)
def post_login(
    credentials: AuthIn, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Login user and return their authentication token."""

    return auth_manager.post_login(credentials)
