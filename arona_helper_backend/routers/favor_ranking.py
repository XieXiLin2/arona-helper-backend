from typing import Annotated

from annotated_types import Gt
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.future import select

from arona_helper_backend.databases.data.sql.database import get_session
from arona_helper_backend.databases.data.sql.models import Favor
from arona_helper_backend.utils import stu_alias_convert

favor_router = APIRouter(prefix="/favor")


# @favor_router.get(
#     path="/char",
#     name="获取角色好感度排行榜 (by 角色名)",
#     description="获取角色好感度排行榜 (by 角色名)",
#     responses={
#         200: {
#             "content": {
#                 "application/json": {
#                     "example": {
#                         "status": 200,
#                         "data": {
#                             "data": [
#                                 {
#                                     "id": "70415",
#                                     "stu": "阿露",
#                                     "favor": "3930",
#                                     "level": "25",
#                                     "nick": "",
#                                 },
#                                 "...",
#                             ],
#                             "current_page": 1,
#                             "current_count": 10,
#                             "current_start": 1,
#                         },
#                     },
#                 },
#             },
#         },
#     },
# )
# async def ranking_char(
#     char: str | None = None,
#     page: int = 1,
#     num: int = 10,
#     reverse: bool = False,
# ) -> JSONResponse:
#     # validate
#     if (num and num < 0) or (page and page < 0):
#         return JSONResponse(
#             content={
#                 "status": 400,
#                 "message": "参数错误",
#             },
#             status_code=400,
#         )
#     # end validate

#     ranking_resp = await API.favor_ranking(
#         char=char,
#         page=page,
#         num=num,
#         reverse=reverse,
#     )
#     if len(ranking_resp.favor) == 0 and char:
#         char = await stu_alias_convert(char)
#         if not char:
#             return JSONResponse(
#                 content={
#                     "status": 404,
#                     "message": "未找到角色",
#                 },
#                 status_code=404,
#             )
#         ranking_resp = await API.favor_ranking(
#             char=char,
#             page=page,
#             num=num,
#             reverse=reverse,
#         )
#     counting_resp = await API.favor_ranking_page(char=char, page=page, num=num)
#     if counting_resp.data.now_page > counting_resp.data.all_page:
#         return JSONResponse(
#             content={
#                 "status": 403,
#                 "message": "页数超出范围",
#             },
#             status_code=403,
#         )
#     return JSONResponse(
#         content={
#             "status": 200,
#             "data": {
#                 "data": [model_dump(i) for i in ranking_resp.favor],
#                 "current_page": counting_resp.data.now_page,
#                 "current_count": ranking_resp.num,
#                 "current_start": counting_resp.data.now_count,
#                 "total_count": counting_resp.data.all_count,
#                 "total_page": counting_resp.data.all_page,
#             },
#         },
#         status_code=200,
#     )


# @favor_router.get(
#     path="/user",
#     name="获取角色好感度排行榜 (by UID)",
#     description="获取角色好感度排行榜 (by UID)",
#     responses={
#         200: {
#             "content": {
#                 "application/json": {
#                     "example": {
#                         "status": 200,
#                         "data": {
#                             "data": [
#                                 {
#                                     "stu": "泉",
#                                     "favor": "90",
#                                     "level": "4",
#                                 },
#                                 "...",
#                             ],
#                             "current_page": 1,
#                             "current_count": 10,
#                             "current_start": 1,
#                             "total_page": 7,
#                             "total_count": 64,
#                         },
#                     },
#                 },
#             },
#         },
#     },
# )
# async def ranking_user(
#     uid: int,
#     char: str | None = None,
#     page: int = 1,
#     num: int = 10,
# ) -> JSONResponse:
#     # validate
#     if (num and num < 0) or (page and page < 0):
#         return JSONResponse(
#             content={
#                 "status": 400,
#                 "message": "参数错误",
#             },
#             status_code=400,
#         )
#     # end validate
#     ranking_resp = await API.favor_user(uid=uid, char=char)
#     if len(ranking_resp.favor) == 0 and char:
#         char = await stu_alias_convert(char)
#         if not char:
#             return JSONResponse(
#                 content={
#                     "status": 404,
#                     "message": "未找到角色",
#                 },
#                 status_code=404,
#             )
#         ranking_resp = await API.favor_user(uid=uid, char=char)
#         if len(ranking_resp.favor) == 0:
#             return JSONResponse(
#                 content={
#                     "status": 404,
#                     "message": "未找到 UID",
#                 },
#                 status_code=404,
#             )
#     total_page = page_count(len(ranking_resp.favor), num)
#     if page > total_page:
#         return JSONResponse(
#             content={
#                 "status": 403,
#                 "message": "页数超出范围",
#             },
#             status_code=403,
#         )
#     current_start = (page - 1) * num
#     return JSONResponse(
#         content={
#             "status": 200,
#             "data": {
#                 "data": [
#                     model_dump(i)
#                     for i in ranking_resp.favor[current_start : current_start + num]
#                 ],
#                 "current_page": page,
#                 "current_count": num,
#                 "current_start": current_start + 1,
#                 "total_page": total_page,
#                 "total_count": ranking_resp.num,
#             },
#         },
#         status_code=200,
#     )


@favor_router.get("", name="获取好感度排行榜")
async def ranking(
    uid: str | None = None,
    char: str | None = None,
    page: Annotated[int, Gt(0)] = 1,
    num: Annotated[int, Gt(0)] = 10,
    reverse: bool = False,
) -> JSONResponse:
    statement = select(Favor)
    if uid:
        statement = statement.where(Favor.Id == uid)
    if char:
        statement = statement.where(Favor.stu == stu_alias_convert(char))
    async with get_session() as session:
        query_resp = await session.scalars(
            statement.order_by(
                Favor.level.asc() if reverse else Favor.level.desc(),
            ).slice((page - 1) * num, page * num),
        )
    return JSONResponse(
        content={
            "status": 200,
            "data": {
                "data": [
                    {
                        "uid": item.Id,
                        "nick": f"{item.Id} 老师",
                        "stu": item.stu,
                        "level": item.favor,
                        "grade": item.level,
                    }
                    for item in query_resp
                ],
            },
        },
        status_code=200,
    )
    #     resp_data = [
    #         RankingData(
    #             uid=i.Id,
    #             nick=f"{i.Id} 老师",
    #             stu=i.stu,
    #             level=i.favor,
    #             grade=i.level,
    #         )
    #         for i in query_resp.scalars().all()
    #     ]
    # return JSONResponse(
    #     content={
    #         "status": 200,
    #         "data": {
    #             "data": [model_dump(i) for i in resp_data],
    #         },
    #     },
    #     status_code=200,
    # )
