from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.config import settings

engine = create_async_engine(
    url=settings.get_connection_string, 
    echo=True
)

# generate table data / auto migration
async def create_db_tables():
    async with engine.begin() as conn:
        from app.database.models import Shipment
        await conn.run_sync(SQLModel.metadata.create_all)


# create async session
async def get_session():
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
