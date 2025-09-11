from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class MovieBaseSchema(BaseModel):
    name: str
    date: date
    score: float
    overview: str
    status: str
    budget: float
    revenue: float
    country_id: int
    country: str
    genres: List[str]
    actors: List[str]
    languages: List[str]


    model_config = {
        "from_attributes": True
    }

class MovieCreateSchema(MovieBaseSchema):
    pass


class MovieDetailSchema(MovieBaseSchema):
    id: int
    country_id: int
    country: str
    genres: List[str]
    actors: List[str]
    languages: List[str]

    model_config = {
        "from_attributes": True
    }

class MovieUpdateSchema(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    score: Optional[float] = None
    overview: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    revenue: Optional[float] = None
    country_id: Optional[int] = None
    country: Optional[str] = None
    genres: Optional[List[str]] = None
    actors: Optional[List[str]] = None
    languages: Optional[List[str]] = None

    model_config = {
        "from_attributes": True
    }

class MovieListResponseSchema(MovieBaseSchema):
    id: int

    model_config = {
        "from_attributes": True
    }
