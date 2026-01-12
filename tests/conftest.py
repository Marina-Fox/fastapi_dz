from typing import Any, AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..src.database import get_session
from ..src.main import app
from ..src.models import Base

T_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def engine_test():
    _engine = create_async_engine(T_DATABASE_URL, echo=True)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    await _engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def get_test_session(engine_test):
    test_session = async_sessionmaker(engine_test, expire_on_commit=False)

    async def override_get_session() -> AsyncGenerator[AsyncSession, Any]:
        async with test_session() as session:
            try:
                yield session
                await session.rollback()
            finally:
                await session.close()

    app.dependency_overrides[get_session] = override_get_session
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(get_test_session):
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        yield ac
