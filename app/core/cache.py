from redis import Redis

from app.core.config import settings

# https://redis.io/docs/latest/develop/clients/redis-py/connect/#basic-connection
redis_client = Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)


def set_cached_count(count: int, key: str = "questions:total_count", ttl: int = 300):
    """Guardar count en cache (TTL en segundos)"""
    redis_client.setex(key, ttl, count)


def get_cached_count(key: str = "questions:total_count") -> int | None:
    """Obtener count cacheado"""
    cached = redis_client.get(key)
    return int(cached) if cached else None


def invalidate_count_cache(key: str = "questions:total_count"):
    """Invalidar cache cuando se crean/eliminan preguntas"""
    redis_client.delete(key)
