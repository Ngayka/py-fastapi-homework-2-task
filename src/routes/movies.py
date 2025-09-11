from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi_pagination import Page, add_pagination, paginate

from pagination import CustomParams
from database import get_db, MovieModel
from database.models import CountryModel, GenreModel, ActorModel, LanguageModel
from schemas.movies import  (MovieDetailSchema,
                            MovieListResponseSchema,
                            MovieBaseSchema,
                            MovieCreateSchema,
                            MovieUpdateSchema)
from crud import (get_movies,
                      get_movie,
                      create_movie,
                      update_movie,
                      delete_movie_crud)

router = APIRouter()


@router.get("/movies/", response_model=Page[MovieListResponseSchema])
async def list_movies(
        db: AsyncSession = Depends(get_db),
        params: CustomParams = Depends(),
    ):
    movies = await get_movies(db, select(MovieModel).order_by(MovieModel.id.desc()))

    movies_data = [MovieListResponseSchema.from_orm(m) for m in movies]

    return paginate(movies_data, params)

@router.get("/movies/{movie_id}", response_model=MovieDetailSchema)
async def read_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="No movies found.")
    return movie

@router.post("/movies", response_model=MovieCreateSchema, status_code=201)
async def add_movie(movie: MovieCreateSchema, db: AsyncSession = Depends(get_db)):
    new_movie = await create_movie(db, movie)
    return new_movie

@router.patch("/movies/{movie_id}")
async def edit_movie(movie_id: int, movie: MovieUpdateSchema, db: AsyncSession = Depends(get_db)):
    updated_movie = await update_movie(db, movie_id, movie)
    if not updated_movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")
    return MovieDetailSchema(**updated_movie)

@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    deleted_movie = await delete_movie_crud(db, movie_id)
    if not deleted_movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


