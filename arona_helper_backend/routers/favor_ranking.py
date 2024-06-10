from typing import Annotated

from annotated_types import Gt
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.future import select

from arona_helper_backend.databases.data.sql.database import get_session
from arona_helper_backend.databases.data.sql.models import Favor
from arona_helper_backend.utils import stu_alias_convert

favor_router = APIRouter(prefix="/favor")


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
        # total_count = func.count()
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
