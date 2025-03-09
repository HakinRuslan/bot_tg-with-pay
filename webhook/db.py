

from sqlalchemy import MetaData
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime
from config import url
from sqlalchemy import func, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import BigInteger, Text, ForeignKey, Date

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

print(f"адрес текущиий - {url}")

engine = create_async_engine(url)
session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session

metadata = MetaData()


class Base(DeclarativeBase):
    __abstract__ = True  

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )