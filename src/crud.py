from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models import MovieModel
from schemas.movies import  (MovieDetailSchema,
    MovieListResponseSchema,
    MovieBaseSchema,
    MovieCreateSchema,
    MovieUpdateSchema)


async def create_movie(db: AsyncSession, movie: MovieCreateSchema):
    new_movie = MovieModel(**movie.model_dump())
    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)
    return new_movie


async def update_movie(db: AsyncSession, movie_id: int, movie: MovieUpdateSchema):
    result = await db.execute(select(MovieModel).options(
        selectinload(MovieModel.country),
        selectinload(MovieModel.actors),
        selectinload(MovieModel.languages),
    ).where(MovieModel.id == movie_id)
    )
    db_movie = result.scalar_one_or_none()
    if not db_movie:
        return None
    for key, value in movie.model_dump(exclude_unset=True).items():
        setattr(db_movie, key, value)

    await db.commit()
    await db.refresh(db_movie)
    return {
        "id": db_movie.id,
        "name": db_movie.name,
        "date": db_movie.date,
        "score": db_movie.score,
        "overview": db_movie.overview,
        "status": db_movie.status,
        "budget": db_movie.budget,
        "revenue": db_movie.revenue,
        "country": db_movie.country.name if db_movie.country else None,
        "genres": [g.name for g in db_movie.genres] if db_movie.genres else [],
        "actors": [a.name for a in db_movie.actors] if db_movie.actors else [],
        "languages": [l.name for l in db_movie.languages] if db_movie.languages else [],
    }


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