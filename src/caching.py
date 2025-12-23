import redis
import re
import os
from typing import Optional

def load_redis_client():
    host = os.getenv("ELASTICACHE_ENDPOINT")
    if not host:
        raise RuntimeError("ELASTICACHE_ENDPOINT not set")

    print(f"Using Redis host: {host}")

    client = redis.Redis(
        host=host,
        port=6379,
        db=0,
        decode_responses=True,

        # 🔑 REQUIRED FOR ELASTICACHE SERVERLESS
        ssl=True,
        ssl_cert_reqs=None,

        socket_connect_timeout=5,
        socket_timeout=5,
    )

    client.ping()
    print("✅ Redis ping successful")
    return client



def normalize_query(query: str) -> str:
    """Normalize query for consistent cache keys"""
    q = query.lower().strip()
    q = re.sub(r"\s+", " ", q)  # collapse multiple spaces
    q = re.sub(r'[^\w\s]', '', q)  # remove punctuation
    return q


def cache_get(query: str, redis_client) -> Optional[str]:
    """Get cached response for a query."""
    key = f"rag:query:{normalize_query(query)}"
    return redis_client.get(key)


def cache_set(query: str, answer: str, redis_client, ttl: int = 3600):
    """Cache a query-answer pair."""
    key = f"rag:query:{normalize_query(query)}"
    redis_client.setex(key, ttl, answer)