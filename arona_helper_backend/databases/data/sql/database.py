from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None


async def init_engine(user: str, password: str, host: str, port: int, dbname: str):
    global engine
    database_url = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_async_engine(database_url, echo=True)


def get_session() -> AsyncSession:
    global engine
    if not engine:
        raise Exception("engine not initialized")
    return AsyncSession(
        engine.engine,
        expire_on_commit=False,
        autoflush=True,
    )


async def close_engine():
    global engine
    if engine:
        await engine.dispose()
        engine = None
