from typing import Optional

from datetime import date, timedelta

from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)
import pycountry

from database.models import MovieStatusEnum


class CountrySchema(BaseModel):
    code: str
    name: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class GenreSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class ActorSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class LanguageSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class MovieCreateSchema(BaseModel):
    name: str = Field(max_length=255)
    date: date
    score: float = Field(ge=0, le=100)
    overview: str
    status: MovieStatusEnum
    budget: Decimal = Field(ge=0)
    revenue: float = Field(ge=0)
    country: str
    genres: list[str]
    actors: list[str]
    languages: list[str]

    @field_validator("date")
    def validate_date_not_exceed_one_year_future(cls, value):
        max_date = date.today() + timedelta(days=365)

        if value > max_date:
            raise ValueError("Date cannot exceed one year from today.")
        return value

    @field_validator("country")
    def validate_country_iso_alpha3_code(cls, value):
        alpha3_codes = [country.alpha_2 for country in pycountry.countries]

        if value not in alpha3_codes:
            raise ValueError(
                "Country code must be 'ISO 3166-1 alpha-3' format"
            )
        return value


    model_config = ConfigDict(from_attributes=True)


class MovieDetailSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float
    overview: str
    status: MovieStatusEnum
    budget: Decimal
    revenue: float
    country: CountrySchema
    languages: list[LanguageSchema]
    genres: list[GenreSchema]
    actors: list[ActorSchema]

    model_config = ConfigDict(from_attributes=True)


class MovieListItemSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float
    overview: str

    model_config = ConfigDict(from_attributes=True)


class MovieListResponseSchema(BaseModel):
    movies: list[MovieListItemSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int

    model_config = ConfigDict(from_attributes=True)
