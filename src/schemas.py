from pydantic import Field, BaseModel, ConfigDict


class BaseRecipe(BaseModel):
    title: str = Field(..., title='Название рецепта')
    cooking_time: int = Field(..., title='Время приготовления (мин)', gt=1)
    ingredients: str = Field(..., title='Список ингредиентов (через запятую)')
    description: str = Field(..., title='Рецепт')

class RecipeIn(BaseRecipe):
    ...

class RecipeOut(BaseRecipe):
    id: int = Field(..., title='Идентификатор рецепта')
    views: int = Field(..., title='Количество просмотров')

    model_config = ConfigDict(from_attributes = True)
