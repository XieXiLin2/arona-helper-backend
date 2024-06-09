# from sqlalchemy import URL

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None


async def init_engine(user: str, password: str, host: str, port: int, dbname: str):
    global engine
    database_url = URL.create(
        drivername="mysql+asyncmy",
        username=user,
        password=password,
        host=host,
        port=port,
        database=dbname,
    )
    engine = create_async_engine(database_url, echo=True)


def get_engine() -> AsyncEngine:
    global engine
    if not engine:
        raise Exception("Engine is not initialized")
    return engine


def get_session():
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )()


async def close_engine():
    global engine
    if engine:
        await engine.dispose()
        engine = None
