from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MovieModel


def generate_pagination_links(
    total_pages: int,
    page: int,
    per_page: int
) -> dict[str, str]:
    
    base_url = "/theater/movies/"
    prev_page = (
        f"{base_url}?page={page - 1}&per_page={per_page}"
        if page > 1 else None
    )
    next_page = (
        f"{base_url}?page={page + 1}&per_page={per_page}"
        if page < total_pages else None
    )

    return {
        "prev_page": prev_page,
        "next_page": next_page
    }


async def get_movie_list(
        db: AsyncSession,
        page: int,
        per_page: int
) -> list[MovieModel]:

    offset = (page - 1) * per_page

    query = (
        select(MovieModel)
        .order_by(MovieModel.id.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(query)
    
    movies = result.scalars().all()

    return movies
