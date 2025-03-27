"""
Configuration de la base de données SQLAlchemy.
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Récupération de l'URL de la base de données depuis les variables d'environnement
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Conversion de l'URL SQLite pour le support asynchrone
if DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# Création du moteur asynchrone
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Mettre à True pour le débogage SQL
    future=True,
)

# Session asynchrone
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base déclarative pour les modèles
Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Générateur de session de base de données asynchrone.
    À utiliser comme dépendance FastAPI.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """
    Initialise la base de données en créant toutes les tables.
    À appeler au démarrage de l'application.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 