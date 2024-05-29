from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session
import contextlib

from arona_helper_backend.config import config


def get_engine() -> Engine:
    return create_engine(
        url=f"{config.database.dialect}{f'+{config.database.driver}' if config.database.driver else ''}://{config.database.host}{f':{config.database.port}' if config.database.port else ''}/{config.database.db}?{config.database.args if config.database.args else ''}",
        echo=config.database.debug,
    )


@contextlib.contextmanager
def get_session(engine: Engine):
    session = Session(bind=engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
