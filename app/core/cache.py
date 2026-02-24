from redis import Redis

from app.core.config import settings

# TODO realizar una configuración para producción

# https://redis.io/docs/latest/develop/clients/redis-py/connect/#basic-connection
redis_client = Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)


def set_cached_count(name: str, value: int, ttl: int = 300):
    """Guardar count en cache (TTL en segundos)"""
    # redis_client.setex(key, ttl, count)
    redis_client.set(name=name, value=value, ex=ttl)


def get_cached_count(name: str) -> int | None:
    """Obtener count cacheado"""
    cached = redis_client.get(name)
    return int(cached) if cached else None


def invalidate_count_cache(key: str = "questions:total_count"):
    """Invalidar cache cuando se crean/eliminan preguntas"""
    redis_client.delete(key)
