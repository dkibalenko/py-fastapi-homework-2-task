from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from database.models import MovieModel, Base, CountryModel, GenreModel, ActorModel, LanguageModel
from schemas.movies import MovieCreateSchema, MovieDetailSchema


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


async def get_or_create_related_object(
    db: AsyncSession,
    model: Base,
    related_model_name: str,
    field: str = None
) -> Base:
    """Get or create a related object by name or code."""
    if not field:
        field = (
            "code"
            if isinstance(related_model_name, str)
            and len(related_model_name) == 2
            else "name"
        )
    filter_kwargs = {field: related_model_name}
    result = await db.execute(select(model).filter_by(**filter_kwargs))

    existing_object = result.scalars().first()

    if existing_object:
        return existing_object

    instance = model(**filter_kwargs)
    db.add(instance)
    await db.flush()
    return instance


async def get_list_of_related_objects(
    db: AsyncSession,
    model: Base, 
    related_model_names: list[str]
) -> list[Base]:
    """Create a list of related objects."""
    related_objects = [
        await get_or_create_related_object(
            db=db,
            model=model,
            related_model_name=name
        )
        for name in related_model_names
    ]

    return related_objects


async def create_movie(
    db: AsyncSession,
    movie: MovieCreateSchema
) -> MovieDetailSchema:
    """
    Create a movie and all related objects, returning the full movie
    with relationships. Ensures atomicity of the transaction.
    """
    async with db.begin():
        country = await get_or_create_related_object(
            db=db,
            model=CountryModel,
            related_model_name=movie.country
        )
        genres_objects = await get_list_of_related_objects(
            db=db,
            model=GenreModel,
            related_model_names=movie.genres
        )
        actors_objects = await get_list_of_related_objects(
            db=db,
            model=ActorModel,
            related_model_names=movie.actors
        )
        languages_objects = await get_list_of_related_objects(
            db=db,
            model=LanguageModel,
            related_model_names=movie.languages
        )

        db_movie = MovieModel(
            name=movie.name,
            date=movie.date,
            score=movie.score,
            overview=movie.overview,
            status=movie.status,
            budget=movie.budget,
            revenue=movie.revenue,
            country=country,
            genres=genres_objects,
            actors=actors_objects,
            languages=languages_objects
        )

        db.add(db_movie)
        await db.flush()
        await db.refresh(db_movie)
    
    query = (
        select(MovieModel)
        .options(
            joinedload(MovieModel.country),
            selectinload(MovieModel.genres),
            selectinload(MovieModel.actors),
            selectinload(MovieModel.languages),
        )
        .where(MovieModel.id == db_movie.id)
    )

    result = await db.execute(query)
    movie = result.scalar_one_or_none()

    return MovieDetailSchema.model_validate(movie)


async def get_single_movie(
    db: AsyncSession,
    movie_id: int
) -> MovieModel:
    """Retrieves a single movie with the given ID and all related objects."""
    query = (
        select(MovieModel)
        .options(
            joinedload(MovieModel.country),
            selectinload(MovieModel.genres),
            selectinload(MovieModel.actors),
            selectinload(MovieModel.languages),
        )
        .where(MovieModel.id == movie_id)
    )
    result = await db.execute(query)
    movie = result.scalar_one_or_none()
    return movie
