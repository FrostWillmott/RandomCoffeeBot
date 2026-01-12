"""Base the repository with common CRUD operations."""

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base the repository with generic CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """Initialize repository with model and session.

        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        """Get entity by ID.

        Args:
            id: Entity ID

        Returns:
            Entity or None if not found
        """
        result = await self.session.get(self.model, id)
        return result  # type: ignore[no-any-return]

    async def get_all(self) -> list[ModelType]:
        """Get all entities.

        Returns:
            List of entities
        """
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        """Create a new entity.

        Args:
            entity: Entity to create

        Returns:
            Created entity
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        """Update existing entity.

        Args:
            entity: Entity to update

        Returns:
            Updated entity
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        """Delete entity.

        Args:
            entity: Entity to delete
        """
        await self.session.delete(entity)
        await self.session.flush()
