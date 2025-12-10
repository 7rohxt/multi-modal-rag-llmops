import redis
import re

def load_redis_client(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
):
    """Return a new Redis client instance."""
    return redis.Redis(
        host=host,
        port=port,
        db=db,
        decode_responses=decode_responses
    )

def normalize_query(query: str) -> str:
    q = query.lower().strip()
    q = re.sub(r"\s+", " ", q)  # collapse multiple spaces
    return q

def cache_get(query: str, redis_client):
    key = normalize_query(query)
    return redis_client.get(key)

def cache_set(query: str, answer: str, redis_client, ttl=86400):  # 24 hours
    key = normalize_query(query)
    redis_client.set(key, answer, ex=ttl)