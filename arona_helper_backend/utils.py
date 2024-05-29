import httpx
from cookit.pyd import type_validate_python

from arona_helper_backend.models import (
    FavorEditResponse,
    FavorRankingResponse,
    FavorUserResponse,
    FavorRankingPageResponse,
    NickEditResponse,
)
from arona_helper_backend.config import config


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
                            "char": char if char else "",
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
                            "num": num if num else "",
                        },
                    )
                )
                .raise_for_status()
                .json(),
            )

    async def nick_edit(
        self,
        uid: int,
        nick: str | None = None,
    ) -> NickEditResponse:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            return type_validate_python(
                NickEditResponse,
                (
                    await client.post(
                        "/nick_edit",
                        json={
                            "uid": uid,
                            "nick": nick if nick else "",
                        },
                    )
                )
                .raise_for_status()
                .json(),
            )


async def stu_alias_convert(stu: str) -> str | None:
    async with httpx.AsyncClient(
        base_url=config.bawiki_data, follow_redirects=True
    ) as client:
        stu_alias_list: dict[str, list[str]] = (
            (await client.get("/data/stu_alias.json")).raise_for_status().json()
        )
        for key, values in stu_alias_list.items():
            if stu in values:
                return key
        return None


def page_count(total_count: int, num: int) -> int:
    return (total_count + num - 1) // num
