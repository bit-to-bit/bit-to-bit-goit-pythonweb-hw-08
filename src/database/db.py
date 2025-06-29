import configparser
import contextlib
import pathlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_db_url() -> str:
    file_config = pathlib.Path(__file__).parent.parent.parent.joinpath("config.ini")
    config = configparser.ConfigParser()
    config.read(file_config)
    username = config.get("DB", "user")
    password = config.get("DB", "password")
    domain = config.get("DB", "domain")
    port = config.get("DB", "port")
    db_name = config.get("DB", "db_name")
    return f"postgresql+asyncpg://{username}:{password}@{domain}:{port}/{db_name}"

sessionmanager = DatabaseSessionManager(get_db_url())

async def get_db():
    async with sessionmanager.session() as session:
        yield session