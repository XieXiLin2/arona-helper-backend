from fastapi import APIRouter

from .account import account_router
from .favor_ranking import favor_router
from .nick import nick_router

base_router = APIRouter()

base_router.include_router(router=favor_router)
base_router.include_router(router=nick_router)
base_router.include_router(router=account_router)
