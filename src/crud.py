from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date, timedelta
from fastapi import HTTPException, Depends

from database.models import (
    MovieModel,
    CountryModel,
    GenreModel,
    LanguageModel,
    ActorModel)

from schemas.movies import (
    MovieDetailSchema,
    MovieListResponseSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
)



async def get_or_create(db, Model, value: str):
    stmt = select(Model).where(field == value)
    result = await db.execute(stmt)
    instance = result.scalar_one_or_none()
    if instance:
        return instance
    instance = Model(**{field.key: value})
    db.add(instance)
    await db.flush()
    return instance


async def create_movie(db: AsyncSession, movie: MovieCreateSchema):
    country = await get_or_create(db, CountryModel, movie.country)
    genres = [await get_or_create(db, GenreModel, g) for g in movie.genres]
    languages = [
        await get_or_create(db, LanguageModel, l) for l in movie.languages
    ]
    actors = [await get_or_create(db, ActorModel, a) for a in movie.actors]
    stmt = select(MovieModel).where(
        MovieModel.name == movie.name, MovieModel.date == movie.date
    )
    result = await db.execute(stmt)
    duplicate = result.scalar_one_or_none()
    if duplicate:
        raise HTTPException(
            status_code=409, detail=f"A movie with the name '{duplicate.name}' and release date '{duplicate.date.isoformat()}' already exists."
        )
    if not (0 <= movie.score <= 100):
        raise HTTPException(status_code=400, detail="Invalid input data.")
    if movie.revenue is not None and movie.revenue < 0:
        raise HTTPException(status_code=400, detail="Invalid input data.")
    if movie.budget is not None and movie.budget < 0:
        raise HTTPException(status_code=400, detail="Invalid input data.")
    if movie.date > date.today() + timedelta(days=365):
        raise HTTPException(status_code=400, detail="Invalid input data.")
    new_movie = MovieModel(
        name=movie.name,
        date=movie.date,
        score=movie.score,
        overview=movie.overview,
        status=movie.status,
        budget=movie.budget,
        revenue=movie.revenue,
        country=country,
        genres=genres,
        actors=actors,
        languages=languages,
    )
    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)
    return new_movie


async def update_movie(db: AsyncSession, movie_id: int, movie: MovieUpdateSchema):
    result = await db.execute(
        select(MovieModel)
        .options(
            selectinload(MovieModel.country),
            selectinload(MovieModel.actors),
            selectinload(MovieModel.languages),
        )
        .where(MovieModel.id == movie_id)
    )
    db_movie = result.scalar_one_or_none()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    data = movie.model_dump(exclude_unset=True)
    if "score" in data and not (0 <= data["score"] <= 100):
        raise HTTPException(status_code=400, detail="Invalid input data.")
    if "revenue" in data and data["revenue"] is not None and data["revenue"] < 0:
        raise HTTPException(status_code=400, detail="Invalid input data.")
    if "budget" in data and data["budget"] is not None and data["budget"] < 0:
        raise HTTPException(status_code=400, detail="Invalid input data.")
    if "date" in data and data["date"] > date.today() + timedelta(days=365):
        raise HTTPException(status_code=400, detail="Invalid input data.")

    for key, value in data.items():
        setattr(db_movie, key, value)

    await db.commit()
    await db.refresh(db_movie)
    return {"detail": "Movie update successfully."}


async def delete_movie_crud(db: AsyncSession, movie_id: int):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    db_movie = result.scalar_one_or_none()
    if not db_movie:
        return None
    await db.delete(db_movie)
    await db.commit()
    return db_movie


async def get_movie(db: AsyncSession, movie_id: int):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()
    return movie


async def get_movies(db: AsyncSession, query):
    result = await db.execute(query)
    movies = result.scalars().all()
    return movies
