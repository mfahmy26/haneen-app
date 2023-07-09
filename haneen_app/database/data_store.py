from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine as create_async_engine0
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

_async_sessionmakers = {}


def create_async_engine(use_pool=True) -> AsyncEngine:
    connection_string = _get_connection_string()
    return create_async_engine0(connection_string, poolclass=None if use_pool else NullPool)


def _get_connection_string():
    db_name = "dxuoiqhd"
    server = "stampy.db.elephantsql.com"
    user = "dxuoiqhd"
    password = "RzlwCJba3iknPZ467TrfkeRcwDmNYuQC"

    return f"postgresql+asyncpg://{user}:{password}@{server}/{db_name}"


def get_async_session(use_pool=True) -> AsyncSession:
    async_sessionmaker = _async_sessionmakers.get(use_pool)
    if not async_sessionmaker:
        async_sessionmaker = _create_async_sessionmaker(create_async_engine(use_pool))
        _async_sessionmakers[use_pool] = async_sessionmaker
    
    return async_sessionmaker()

def _create_async_sessionmaker(engine: AsyncEngine):
    return sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False, class_=AsyncSession)

async def yield_async_session() -> AsyncSession:
    async with get_async_session() as session:
        yield session
