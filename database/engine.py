from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from database.models.base import Base


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def create_session_maker() -> async_sessionmaker:
    engine = create_async_engine('sqlite+aiosqlite:///database/base.db')
    await create_tables(engine)
    return async_sessionmaker(engine, expire_on_commit=False)
