from cookit.pyd import model_dump
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from arona_helper_backend.config import config
from arona_helper_backend.utils import FavourQueryAPI, page_count, stu_alias_convert

favor_router = APIRouter(prefix="/favor")
API = FavourQueryAPI(base_url=config.upstream)


@favor_router.get(
    path="",
    name="获取好感度排行榜 (综合)",
    description="获取好感度排行榜 (综合)",
)
async def ranking(
    uid: int | None = None,
    char: str | None = None,
    page: int = 1,
    num: int = 10,
    reverse: bool = False,
) -> JSONResponse:
    # validate
    if (num and num < 0) or (page and page < 0):
        return JSONResponse(
            content={
                "status": 400,
                "message": "参数错误",
            },
            status_code=400,
        )
    # end validate
    if not uid:
        ranking_resp = await API.favor_ranking(
            char=char,
            page=page,
            num=num,
            reverse=reverse,
        )
        if len(ranking_resp.favor) == 0 and char:
            char = await stu_alias_convert(char)
            if not char:
                return JSONResponse(
                    content={
                        "status": 404,
                        "message": "未找到角色",
                    },
                    status_code=404,
                )
        counting_resp = await API.favor_ranking_page(char=char, page=page, num=num)
        total_page = counting_resp.data.all_page
        current_start = counting_resp.data.now_count
        current_page = counting_resp.data.now_page
        total_count = counting_resp.data.all_count
    else:
        ranking_resp = await API.favor_user(uid=uid, char=char)
        if len(ranking_resp.favor) == 0 and char:
            char = await stu_alias_convert(char)
            if not char:
                return JSONResponse(
                    content={
                        "status": 404,
                        "message": "未找到角色",
                    },
                    status_code=404,
                )
            ranking_resp = await API.favor_user(uid=uid, char=char)
            if len(ranking_resp.favor) == 0:
                return JSONResponse(
                    content={
                        "status": 404,
                        "message": "未找到 UID",
                    },
                    status_code=404,
                )
        total_page = page_count(len(ranking_resp.favor), num)
        current_start = (page - 1) * num
        current_page = page
        total_count = ranking_resp.num
    if page > total_page:
        return JSONResponse(
            content={
                "status": 403,
                "message": "页数超出范围",
            },
            status_code=403,
        )
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "data": [
                    model_dump(i)
                    for i in ranking_resp.favor[current_start : current_start + num]
                ],
                "current_page": current_page,
                "current_count": current_start + num,
                "current_start": current_start,
                "total_count": total_count,
                "total_page": total_page,
            },
        },
        status_code=200,
    )


@favor_router.get(
    path="/char",
    description="获取角色好感度排行榜 (by 角色名)",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "status": 200,
                        "data": {
                            "data": ["..."],
                            "current_page": 1,
                            "current_count": 10,
                            "current_start": 1,
                        },
                    },
                },
            },
        },
    },
)
async def ranking_char(
    char: str | None = None,
    page: int = 1,
    num: int = 10,
    reverse: bool = False,
) -> JSONResponse:
    # validate
    if (num and num < 0) or (page and page < 0):
        return JSONResponse(
            content={
                "status": 400,
                "message": "参数错误",
            },
            status_code=400,
        )
    # end validate

    ranking_resp = await API.favor_ranking(
        char=char,
        page=page,
        num=num,
        reverse=reverse,
    )
    if len(ranking_resp.favor) == 0 and char:
        char = await stu_alias_convert(char)
        if not char:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": "未找到角色",
                },
                status_code=404,
            )
        ranking_resp = await API.favor_ranking(
            char=char,
            page=page,
            num=num,
            reverse=reverse,
        )
    counting_resp = await API.favor_ranking_page(char=char, page=page, num=num)
    if counting_resp.data.now_page > counting_resp.data.all_page:
        return JSONResponse(
            content={
                "status": 403,
                "message": "页数超出范围",
            },
            status_code=403,
        )
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "data": [model_dump(i) for i in ranking_resp.favor],
                "current_page": counting_resp.data.now_page,
                "current_count": ranking_resp.num,
                "current_start": counting_resp.data.now_count,
                "total_count": counting_resp.data.all_count,
                "total_page": counting_resp.data.all_page,
            },
        },
        status_code=200,
    )


@favor_router.get(
    path="/user",
    description="获取角色好感度排行榜 (by UID)",
)
async def ranking_user(
    uid: int,
    char: str | None = None,
    page: int = 1,
    num: int = 10,
) -> JSONResponse:
    # validate
    if (num and num < 0) or (page and page < 0):
        return JSONResponse(
            content={
                "status": 400,
                "message": "参数错误",
            },
            status_code=400,
        )
    # end validate
    ranking_resp = await API.favor_user(uid=uid, char=char)
    if len(ranking_resp.favor) == 0 and char:
        char = await stu_alias_convert(char)
        if not char:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": "未找到角色",
                },
                status_code=404,
            )
        ranking_resp = await API.favor_user(uid=uid, char=char)
        if len(ranking_resp.favor) == 0:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": "未找到 UID",
                },
                status_code=404,
            )
    total_page = page_count(len(ranking_resp.favor), num)
    if page > total_page:
        return JSONResponse(
            content={
                "status": 403,
                "message": "页数超出范围",
            },
            status_code=403,
        )
    current_start = (page - 1) * num
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "data": [
                    model_dump(i)
                    for i in ranking_resp.favor[current_start : current_start + num]
                ],
                "current_page": page,
                "current_count": num,
                "current_start": current_start + 1,
                "total_page": total_page,
                "total_count": ranking_resp.num,
            },
        },
        status_code=200,
    )
