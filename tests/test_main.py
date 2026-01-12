import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_post_new_recipe(client: AsyncClient):
    """Проверка добавления нового рецепта."""
    data = {
        "title": "Суши",
        "cooking_time": 60,
        "ingredients": "рис, рыба, водоросли",
        "description": "свернуть в трубочку",
    }
    response = await client.post("/recipes", json=data)
    assert response.status_code == 200
    recipe = response.json()
    assert recipe["title"] == "Суши"
    assert recipe["cooking_time"] == 60
    assert recipe["ingredients"] == "рис, рыба, водоросли"
    assert recipe["description"] == "свернуть в трубочку"
    assert "id" in recipe


@pytest.mark.asyncio
async def test_get_deteil_recipe(client: AsyncClient):
    """Проверка получения страницы с деталями рецепта."""
    response = await client.get("/recipes/1")
    assert response.status_code == 200
    recipe = response.json()
    assert recipe["title"] == "Суши"
    assert recipe["cooking_time"] == 60
    assert recipe["ingredients"] == "рис, рыба, водоросли"
    assert recipe["description"] == "свернуть в трубочку"
    assert "views" in recipe


@pytest.mark.asyncio
async def test_get_all_recipes(client: AsyncClient):
    """Проверка получения списка рецептов."""
    response = await client.get("/recipes")
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) == 1


# для запуска pytest test_main.py -v
# для завершения  Ctrl+C
