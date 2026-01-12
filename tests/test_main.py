import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator, Any

from ..src.database import get_session
from ..src.main import app
from ..src.models import Base

T_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

test_engine = create_async_engine(T_DATABASE_URL, echo=True)
test_session = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

async def get_test_session() -> AsyncGenerator[AsyncSession, Any]:
    async with test_session() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()

app.dependency_overrides[get_session] = get_test_session

@pytest_asyncio.fixture(scope='session', autouse=True)
async def create_table():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest_asyncio.fixture()
async def client():
    try:
        async with AsyncClient(transport=ASGITransport(app), base_url='http://test') as ascl:
            yield ascl
    finally:
        await ascl.aclose()


@pytest.mark.asyncio
async def test_post_new_recipe(client: AsyncClient):
    '''Проверка добавления нового рецепта.'''
    data = {
        'title': 'Суши',
        'cooking_time': 60,
        'ingredients': 'рис, рыба, водоросли',
        'description': 'свернуть в трубочку'
    }
    response = await client.post('/recipes', json=data)
    assert response.status_code == 200
    recipe = response.json()
    assert recipe['title'] == 'Суши'
    assert recipe['cooking_time'] == 60
    assert recipe['ingredients'] == 'рис, рыба, водоросли'
    assert recipe['description'] == 'свернуть в трубочку'
    assert 'id' in recipe

@pytest.mark.asyncio
async def test_get_deteil_recipe(client: AsyncClient):
    '''Проверка получения страницы с деталями рецепта.'''
    response = await client.get('/recipes/1')
    assert response.status_code == 200
    recipe = response.json()
    assert recipe['title'] == 'Суши'
    assert recipe['cooking_time'] == 60
    assert recipe['ingredients'] == 'рис, рыба, водоросли'
    assert recipe['description'] == 'свернуть в трубочку'
    assert 'views' in recipe

@pytest.mark.asyncio
async def test_get_all_recipes(client: AsyncClient):
    '''Проверка получения списка рецептов.'''
    response = await client.get('/recipes')
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) == 1


# для запуска pytest test_main.py -v
# для завершения  Ctrl+C
