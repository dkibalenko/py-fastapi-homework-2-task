from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db, MovieModel
from schemas.movies import MovieListResponseSchema
from crud import get_movie_list, generate_pagination_links

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def read_movies(
    db_session: AsyncSession = Depends(get_db),
    page: int = Query(
        default=1,
        ge=1,
        description="Specifies the page number to retrieve."
    ),
    per_page: int = Query(
        default=10,
        ge=1,
        le=20,
        description="Specifies the number of items to display per page."
    )
):

    movies = await get_movie_list(db=db_session, page=page, per_page=per_page)

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_items = await db_session.scalar(
        select(func.count()).select_from(MovieModel)
    )
    total_pages = (total_items + per_page - 1) // per_page

    pagination_links = generate_pagination_links(
        total_pages=total_pages,
        page=page,
        per_page=per_page
    )

    return {
        "movies": movies,
        "prev_page": pagination_links["prev_page"],
        "next_page": pagination_links["next_page"],
        "total_pages": total_pages,
        "total_items": total_items
    }
