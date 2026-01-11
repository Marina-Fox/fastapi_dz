from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Recipe(Base):
    __tablename__='recipes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    cooking_time: Mapped[int] = mapped_column(Integer, nullable=False)
    ingredients: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0)
