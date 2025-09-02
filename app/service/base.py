from typing import Generic, TypeVar
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModelT = TypeVar("ModelT", bound=SQLModel)

class BaseService(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: AsyncSession):
        self.session = session
        self.model = model

    async def _get(self, id: UUID) -> ModelT | None:
        return await self.session.get(self.model, id)

    async def _add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)

        return entity

    async def _update(self, entity: ModelT) -> ModelT:
        return await self._add(entity)

    async def _delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.commit()
