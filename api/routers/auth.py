from fastapi import APIRouter, Depends

from internal.auth import AuthManager, get_auth_manager
from models.user import UserCreate

router = APIRouter(tags=["auth"])


@router.post("/register")
def post_register(
    user: UserCreate, auth_manager: AuthManager = Depends(get_auth_manager)
):
    """Register a new user in database."""

    return auth_manager.post_register(user)
