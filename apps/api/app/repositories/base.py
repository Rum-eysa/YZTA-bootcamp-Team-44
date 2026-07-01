"""Base repository for database operations"""
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: str) -> Optional[ModelType]:
        """Get a single record by ID"""
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record"""
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: str, obj: ModelType) -> Optional[ModelType]:
        """Update a record"""
        result = await self.session.execute(
            update(self.model).where(self.model.id == id).values(**obj.__dict__)
        )
        await self.session.commit()
        return await self.get(id)

    async def delete(self, id: str) -> bool:
        """Delete a record"""
        result = await self.session.execute(delete(self.model).where(self.model.id == id))
        await self.session.commit()
        return result.rowcount > 0
