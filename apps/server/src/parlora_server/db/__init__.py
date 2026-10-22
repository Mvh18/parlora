"""Async database access: SQLAlchemy 2 with asyncpg (design D10)."""

import asyncio
import logging

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from parlora_server.config import DatabaseSettings

logger = logging.getLogger(__name__)

# Deterministic constraint names, so Alembic autogenerate produces stable diffs.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base of every table; the baseline revision has none yet."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Database:
    """The engine and session factory. Creating it opens no connection."""

    def __init__(self, settings: DatabaseSettings) -> None:
        self.engine: AsyncEngine = create_async_engine(
            settings.url.get_secret_value(), pool_pre_ping=True
        )
        self.sessions = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def ping(self, timeout: float = 2.0) -> bool:
        """True when the database answers `SELECT 1` within `timeout` seconds."""
        try:
            async with asyncio.timeout(timeout), self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception as error:  # any failure means "not ready"
            # The type only: driver messages can include the host or user name.
            logger.warning("database ping failed: %s", type(error).__name__)
            return False
        return True

    async def dispose(self) -> None:
        await self.engine.dispose()
