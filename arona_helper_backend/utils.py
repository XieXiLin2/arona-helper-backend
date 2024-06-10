import math
import random
import string
from typing import Annotated

import httpx
import jwt
from cookit.pyd import type_validate_python
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from arona_helper_backend.config import config
from arona_helper_backend.exceptions import AronaError
from arona_helper_backend.models import (
    FavorEditResponse,
    FavorRankingPageResponse,
    FavorRankingResponse,
    FavorUserResponse,
    LoginData,
    NickEditResponse,
)

bot_verify_bearer = HTTPBearer(
    bearerFormat="string",
    scheme_name="Bot Verify Bearer",
    description="Bot Verification",
)
user_verify_bearer = HTTPBearer(
    bearerFormat="string",
    scheme_name="User Verify Bearer",
    description="User Verification",
)


class FavourQueryAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def favor_ranking(
        self,
        char: str | None = None,
        page: int | None = None,
        num: int | None = None,
        reverse: bool = False,
    ) -> FavorRankingResponse:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            return type_validate_python(
                FavorRankingResponse,
                (
                    await client.get(
                        "/favor_ranking",
                        params={
                            "char": char,
                            "page": page,
                            "num": num,
                            "sort": "ASC" if reverse else "",
                        },
                    )
                )
                .raise_for_status()
                .json(),
            )

    async def favor_user(
        self,
        uid: int,
        char: str | None = None,
    ) -> FavorUserResponse:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            return type_validate_python(
                FavorUserResponse,
                (
                    await client.get(
                        "/favor_user",
                        params={
                            "uid": uid,
                            "char": char or "",
                        },
                    )
                )
                .raise_for_status()
                .json(),
            )

    async def favor_ranking_page(
        self,
        char: str | None = None,
        page: int | None = None,
        num: int | None = 10,
    ) -> FavorRankingPageResponse:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            return type_validate_python(
                FavorRankingPageResponse,
                (
                    await client.get(
                        "/favor_ranking_page",
                        params={
                            "page": page,
                            "num": num,
                            "char": char,
                        },
                    )
                )
                .raise_for_status()
                .json(),
            )

    async def favor_edit(
        self,
        uid: int,
        char: str,
        num: int | None = None,
    ) -> FavorEditResponse:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            return type_validate_python(
                FavorEditResponse,
                (
                    await client.post(
                        "/favor_edit",
                        json={
                            "uid": uid,
                            "char": char,
                            "num": num or "",
                        },
                    )
                )
                .raise_for_status()
                .json(),
            )

    async def nick_edit(
        self,
        uid: str,
        nick: str | None = None,
    ) -> NickEditResponse:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            return type_validate_python(
                NickEditResponse,
                (
                    await client.post(
                        url="/nick_edit",
                        json={
                            "uid": uid,
                            "nick": nick or "",
                        },
                        # convert to content to request
                    )
                )
                .raise_for_status()
                .json(),
            )


async def stu_alias_convert(stu: str) -> str | None:
    async with httpx.AsyncClient(
        base_url=config.bawiki_data,
        follow_redirects=True,
    ) as client:
        stu_alias_list: dict[str, list[str]] = (
            (await client.get("/data/stu_alias.json")).raise_for_status().json()
        )
        for key, values in stu_alias_list.items():
            if stu in values:
                return key
        return stu


def calculate_pages(num_per_page: int, total_items: int):
    pages: int = math.ceil(total_items / num_per_page)
    return pages


def rs_generator(
    size: int = 6,
    chars: str = string.ascii_uppercase + string.digits,
) -> str:
    return "".join(random.choice(chars) for _ in range(size))


def verify_jwt(jwt_token: str) -> LoginData:
    try:
        return type_validate_python(
            LoginData,
            jwt.decode(
                jwt=jwt_token,
                key=config.secret.jwt_secret,
                algorithms=[config.secret.jwt_algorithm],
            ),
        )
    except jwt.ExpiredSignatureError as e:
        raise ValueError("Token Expired") from e
    except jwt.InvalidTokenError as e:
        raise ValueError("Invalid Token") from e


def get_login_data(
    token: Annotated[HTTPAuthorizationCredentials, Depends(user_verify_bearer)],
) -> LoginData:
    try:
        user_profile = verify_jwt(token.credentials)
    except ValueError as e:
        raise AronaError(e.args[0]) from e
    return user_profile
