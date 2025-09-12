from pydantic import BaseModel, constr, confloat, conint
from datetime import date
from typing import Optional, List, Literal


class MovieCreateSchema(BaseModel):
    name: constr(min_length=1, max_length=100)
    date: date
    score: confloat(ge=0, le=100)
    overview: str
    status: Literal["RELEASED", "PLANNED", "CANCELLED"]
    budget: Optional[confloat(ge=0)]
    revenue: Optional[confloat(ge=0)]
    country: Optional[str]
    genres: List[str] = []
    actors: List[str] = []
    languages: List[str] = []

    model_config = {"from_attributes": True}


class MovieDetailSchema(BaseModel):
    id: int
    name: constr(min_length=1, max_length=100)
    date: date
    score: confloat(ge=0, le=100)
    overview: str
    status: Literal["RELEASED", "PLANNED", "CANCELLED"]
    budget: Optional[confloat(ge=0)]
    revenue: Optional[confloat(ge=0)]
    country: Optional[str]
    genres: List[str] = []
    actors: List[str] = []
    languages: List[str] = []

    model_config = {"from_attributes": True}


class MovieUpdateSchema(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    date: Optional[date] = None
    score: Optional[confloat(ge=0, le=100)] = None
    overview: Optional[str] = None
    status: Optional[Literal["RELEASED", "PLANNED", "CANCELLED"]] = None
    budget: Optional[confloat(ge=0)] = None
    revenue: Optional[confloat(ge=0)] = None
    country: Optional[str] = None
    genres: Optional[List[str]] = None
    actors: Optional[List[str]] = None
    languages: Optional[List[str]] = None

    model_config = {"from_attributes": True}


class MovieListResponseSchema(BaseModel):
    movies: List[MovieDetailSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int
