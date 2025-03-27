"""
Configuration et utilitaires Redis.
"""
import os
from typing import Any, Optional

import redis.asyncio as redis
from fastapi import HTTPException

# Configuration Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_POOL = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)

async def get_redis() -> redis.Redis:
    """
    Retourne une connexion Redis depuis le pool.
    À utiliser comme dépendance FastAPI.
    """
    client = redis.Redis(connection_pool=REDIS_POOL)
    try:
        yield client
    finally:
        await client.close()

class RedisService:
    """Service pour interagir avec Redis."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[str]:
        """Récupère une valeur depuis Redis."""
        try:
            return await self.redis.get(key)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """
        Stocke une valeur dans Redis.
        
        Args:
            key: Clé Redis
            value: Valeur à stocker
            expire: Temps d'expiration en secondes (optionnel)
        """
        try:
            await self.redis.set(key, value, ex=expire)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def delete(self, key: str) -> None:
        """Supprime une clé de Redis."""
        try:
            await self.redis.delete(key)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans Redis."""
        try:
            return await self.redis.exists(key)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def increment(self, key: str) -> int:
        """Incrémente un compteur Redis."""
        try:
            return await self.redis.incr(key)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def add_to_set(self, key: str, *values: Any) -> int:
        """Ajoute des valeurs à un ensemble Redis."""
        try:
            return await self.redis.sadd(key, *values)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def remove_from_set(self, key: str, *values: Any) -> int:
        """Retire des valeurs d'un ensemble Redis."""
        try:
            return await self.redis.srem(key, *values)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def get_set_members(self, key: str) -> set:
        """Récupère tous les membres d'un ensemble Redis."""
        try:
            return await self.redis.smembers(key)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def publish(self, channel: str, message: str) -> int:
        """Publie un message sur un canal Redis."""
        try:
            return await self.redis.publish(channel, message)
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def subscribe(self, *channels: str) -> redis.client.PubSub:
        """
        Souscrit à des canaux Redis.
        Retourne un objet PubSub pour la lecture des messages.
        """
        try:
            pubsub = self.redis.pubsub()
            await pubsub.subscribe(*channels)
            return pubsub
        except redis.RedisError as e:
            raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")

    async def clear_all(self) -> None:
        """
        Supprime toutes les clés de la base Redis.
        À utiliser avec précaution, uniquement en développement.
        """
        if os.getenv("ENVIRONMENT") == "development":
            try:
                await self.redis.flushall()
            except redis.RedisError as e:
                raise HTTPException(status_code=500, detail=f"Erreur Redis: {str(e)}")
        else:
            raise HTTPException(
                status_code=403,
                detail="Cette opération n'est autorisée qu'en développement"
            ) 