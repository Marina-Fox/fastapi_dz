from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .database import Base, engine, get_session
from .models import Recipe
from .schemas import RecipeIn, RecipeOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/recipes", response_model=List[RecipeOut])
async def get_all_recipes(session: AsyncSession = Depends(get_session)):
    """
    Получить список всех рецептов.
    Поля в таблице:
    название блюда,
    количество просмотров,
    время приготовления (в минутах).
    Рецепты отсортированы по количеству просмотров. Если число просмотров совпадает,
    рецепты сортируются по времени приготовления.
    """
    result = await session.execute(
        select(Recipe).order_by(Recipe.views.desc(), Recipe.cooking_time.asc())
    )
    return result.scalars().all()


@app.post("/recipes", response_model=RecipeOut)
async def post_new_recipe(
    recipe: RecipeIn, session: AsyncSession = Depends(get_session)
):
    """Создать новый рецепт."""
    new_recep = Recipe(**recipe.model_dump())
    session.add(new_recep)
    await session.commit()
    await session.refresh(new_recep)
    return new_recep


@app.get("/recipes/{recipe_id}", response_model=RecipeOut)
async def get_deteil_recipe(
    recipe_id: int, session: AsyncSession = Depends(get_session)
):
    """
    Получить детальную информацию о конкретном рецепте:
    название блюда,
    время приготовления,
    список ингредиентов,
    текстовое описание.
    """
    result = await session.execute(select(Recipe).filter(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    recipe.views += 1
    await session.commit()
    return recipe
