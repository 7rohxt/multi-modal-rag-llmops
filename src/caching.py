import redis
import re
import os
from typing import Optional

def load_redis_client(
    host=None,
    port=6379,
    db=0,
    decode_responses=True,
    use_aws=False
):
    """Load Redis client - works for both local and AWS ElastiCache."""
    
    # Determine which host to use
    if use_aws or os.getenv("USE_AWS_REDIS").lower() == "true":
        # AWS ElastiCache mode
        host = os.getenv("ELASTICACHE_ENDPOINT")
        if not host:
            raise ValueError("ELASTICACHE_ENDPOINT not set in .env")
    else:
        # Local Redis mode
        host = host or os.getenv("REDIS_HOST", "localhost")
    
    try:
        client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        client.ping()  # Test connection
        return client
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        raise


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