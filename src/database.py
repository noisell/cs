from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated
from sqlalchemy import String, text

from src.config import DATABASE_URL

engine = create_async_engine(url=DATABASE_URL)
session_factory = async_sessionmaker(engine, expire_on_commit=False)
str256 = Annotated[str, 256]


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        str256: String(256),
    }


intPK = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
time = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"),
    onupdate=datetime.now(UTC).replace(tzinfo=None),
)]
