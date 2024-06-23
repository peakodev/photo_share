# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
import contextlib
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.conf.config import settings

class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine, expire_on_commit=False
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        # except Exception as err:
        #     print(err)
        #     session.rollback()
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(settings.postgres_url())


async def get_db():
    async with sessionmanager.session() as session:
        yield session



# engine = create_engine(settings.postgres_url())
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
