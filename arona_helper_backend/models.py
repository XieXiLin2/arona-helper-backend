from typing import Annotated
from urllib.parse import unquote_plus

from pydantic import BaseModel, field_validator


# region upstream api response models
class FavourRankingData(BaseModel):
    id: str
    stu: str
    favor: str
    level: str
    nick: str

    @field_validator("nick")
    def nick_unquoted(cls, v: str) -> str:  # noqa: N805
        return unquote_plus(v)


class FavorRankingResponse(BaseModel):
    code: Annotated[int, str]
    num: Annotated[int, str]
    favor: list[FavourRankingData]


class FavorUserData(BaseModel):
    stu: str
    favor: str
    level: str


class FavorUserResponse(BaseModel):
    code: Annotated[int, str]
    num: Annotated[int, str]
    favor: list[FavorUserData]


class FavorRankingPageData(BaseModel):
    all_count: int
    all_page: int
    now_count: int
    now_page: int


class FavorRankingPageResponse(BaseModel):
    msg: str
    status: int
    success: bool
    data: FavorRankingPageData


class FavorEditData(BaseModel):
    level: int
    now: int
    next: int


class FavorEditResponse(BaseModel):
    msg: str
    status: int
    success: bool
    data: FavorEditData


class NickEditResponse(BaseModel):
    msg: str
    status: int
    success: bool


# endregion


class RankingData(BaseModel):
    uid: str
    nick: str
    stu: str
    level: int
    grade: int


class LoginData(BaseModel):
    user_id: str
    exp: int
