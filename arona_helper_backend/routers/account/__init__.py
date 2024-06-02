from fastapi import APIRouter

from .login import login_router

account_router = APIRouter(prefix="/account")

account_router.include_router(router=login_router)
