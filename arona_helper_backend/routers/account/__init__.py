from fastapi import APIRouter

from .get_avatar import avatar_router
from .login import login_router

account_router = APIRouter(prefix="/account")

account_router.include_router(router=avatar_router)
account_router.include_router(router=login_router)
