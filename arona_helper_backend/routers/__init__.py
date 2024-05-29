from fastapi import APIRouter

from .favor_ranking import favor_router
from .nick import nick_router

base_router = APIRouter()

base_router.include_router(router=favor_router)
base_router.include_router(router=nick_router)
