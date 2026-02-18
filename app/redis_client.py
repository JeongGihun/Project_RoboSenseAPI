from redis.asyncio import Redis, ConnectionPool
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

redis_client : Optional[Redis] = None
connection_pool : Optional[ConnectionPool] = None

async def connect_redis() -> Redis :
    global redis_client, connection_pool

    connection_pool = ConnectionPool(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        db=0,
        decode_responses=True,
        encoding="utf-8",
        max_connections=100,
        socket_connect_timeout=5,
        socket_keepalive=True
    )
    redis_client = Redis(connection_pool = connection_pool)

    try :
        result = await redis_client.ping()
        logger.info(f"Redis 연결 성공 : {result}")
    except Exception as e :
        logger.warning(f"Redis 연결 실패 : {e}")
        raise

    return redis_client

async def close_redis() -> None :
    global redis_client, connection_pool

    if redis_client :
        await redis_client.close()
        logger.info("Redis 연결 종료")
    else :
        logger.warning("Redis가 연결되어 있지 않음")

    if connection_pool :
        await connection_pool.disconnect()
        logger.info("Redis Connection pool 연결 종료")
    else :
        logger.warning("Redis Connection pool이 연결되어 있지 않음")

def get_redis() -> Redis :
    if redis_client is None :
        raise RuntimeError("Redis가 연결되어 있지 않습니다. 먼저 연결해주세요")

    return redis_client