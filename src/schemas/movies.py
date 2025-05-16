from datetime import date

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from database.models import MovieStatusEnum


class MovieBase(BaseModel):
    name: str
    date: date
    score: float
    overview: str
    status: MovieStatusEnum
    budget: Decimal
    revenue: float


class MovieCreate(MovieBase):
    pass


class MovieUpdate(MovieBase):
    pass


class MovieRead(MovieBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
