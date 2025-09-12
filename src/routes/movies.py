from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi_pagination import Page, add_pagination, paginate

from pagination import CustomParams
from database import get_db, MovieModel
from database.models import CountryModel, GenreModel, ActorModel, LanguageModel
from schemas.movies import (
    MovieDetailSchema,
    MovieListResponseSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
)
from crud import get_movies, get_movie, create_movie, update_movie, delete_movie_crud

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def list_movies(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
):
    total_items = await db.scalar(select(func.count()).select_from(MovieModel))
    if total_items == 0:
        raise HTTPException(status_code=404, detail="No movies found.")
    total_pages = (total_items + per_page - 1) // per_page

    if page > total_pages and total_items > 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    offset = (page - 1) * per_page

    result = await db.execute(select(MovieModel).offset(offset).limit(per_page))
    movies = result.scalars().all()
    movies_pydantic = [
        MovieDetailResponseSchema.model_validate(
            {
                "id": movie.id,
                "name": movie.name,
                "date": movie.date,
                "score": movie.score,
                "genres": [g.name for g in movie.genres] if movie.genres else [],
                "overview": movie.overview,
                "status": movie.status,
                "languages": [g.name for g in movie.language] if movie.language else [],
                "budget": movie.budget,
                "revenue": movie.revenue,
                "country": movie.country,
                "actors": [a.name for a in movie.actor] if movie.actors else [],
            }
        )
        for movie in movies
    ]

    base_url = "/theater/movies"
    prev_page = f"{base_url}/?page={page - 1}&per_page={per_page}" if page > 1 else ""
    next_page = (
        f"{base_url}/?page={page + 1}&per_page={per_page}" if page < total_pages else ""
    )

    return MovieListResponseSchema(
        movies=movies_pydantic,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get("/movies/{movie_id}", response_model=MovieDetailSchema)
async def read_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")
    return movie


@router.post("/movies", response_model=MovieListResponseSchema, status_code=201)
async def add_movie(movie: MovieCreateSchema, db: AsyncSession = Depends(get_db)):
    new_movie = await create_movie(db, movie)
    return new_movie


@router.patch("/movies/{movie_id}")
async def edit_movie(
    movie_id: int, movie: MovieUpdateSchema, db: AsyncSession = Depends(get_db)
):
    await update_movie(db, movie_id, movie)

    return {"detail": "Movie updated successfully."}


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    deleted_movie = await delete_movie_crud(db, movie_id)
    if not deleted_movie:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
