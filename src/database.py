from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Any

DATABASE_URL = 'sqlite+aiosqlite:///./recipe.db'

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session() as session:
        yield session
