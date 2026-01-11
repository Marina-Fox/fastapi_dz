import pytest
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

@pytest.fixture(scope='session', autouse=True)
async def create_table():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.fixture()
async def client():
    try:
        async with AsyncClient(transport=ASGITransport(app), base_url='http://test') as ascl:
            yield ascl
    finally:
        await ascl.aclose()


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

async def test_get_deteil_recipe(client: AsyncClient):
    '''Проверка получения страницы с деталями рецепта.'''
    # data = {
    #     'title': 'Борщ',
    #     'cooking_time': 2,
    #     'ingredients': 'говядина, лук, морковь, свекла, томатная паста, специи',
    #     'description': 'Варить до готовности, специи по вкусу'
    # }
    # post_resp = await client.post('/recipes', json=data)

    # recipe_id = post_resp.json()['id']
    response = await client.get('/recipes/1')
    assert response.status_code == 200
    recipe = response.json()
    assert recipe['title'] == 'Суши'
    assert recipe['cooking_time'] == 60
    assert recipe['ingredients'] == 'рис, рыба, водоросли'
    assert recipe['description'] == 'свернуть в трубочку'
    assert 'views' in recipe

async def test_get_all_recipes(client: AsyncClient):
    '''Проверка получения списка рецептов.'''
    # data_1 = {
    #     'title': 'Борщ',
    #     'cooking_time': 2,
    #     'ingredients': 'говядина, лук, морковь, свекла, томатная паста, специи',
    #     'description': 'Варить до готовности, специи по вкусу'
    # }
    # await client.post('/recipes', json=data_1)
    # data_2 = {
    #     'title': 'Борщ',
    #     'cooking_time': 2,
    #     'ingredients': 'говядина, лук, морковь, свекла, томатная паста, специи',
    #     'description': 'Варить до готовности, специи по вкусу'
    # }
    # await client.post('/recipes', json=data_2)

    response = await client.get('/recipes')
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) == 1


# для запуска pytest test_main.py -v --asyncio-mode=auto
# для завершения  Ctrl+C
