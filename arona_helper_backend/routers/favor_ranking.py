from typing import Annotated

from annotated_types import Gt
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.future import select

from arona_helper_backend.databases.data.sql.database import get_session
from arona_helper_backend.databases.data.sql.models import Favor
from arona_helper_backend.utils import calculate_pages, stu_alias_convert

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
    state_total = select(func.count("*")).select_from(Favor)
    if uid:
        statement = statement.where(Favor.Id == uid)
        state_total = state_total.where(Favor.Id == uid)
    if char:
        statement = statement.where(Favor.stu == stu_alias_convert(char))
        state_total = state_total.where(Favor.stu == stu_alias_convert(char))
    async with get_session() as session:
        query_resp = await session.scalars(
            statement.order_by(
                Favor.favor.asc() if reverse else Favor.favor.desc(),
            ).slice((page - 1) * num, page * num),
        )
        total_count = (
            await session.scalars(
                state_total.order_by(
                    Favor.favor.asc() if reverse else Favor.favor.desc(),
                ),
            )
        ).one()
    rank = (page - 1) * num + 1
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
                    for index, item in enumerate(query_resp)
                ],
                "current_page": page,
                "current_count": rank,
                "total_page": calculate_pages(num, total_count),
                "total_count": total_count,
            },
        },
        status_code=200,
    )
