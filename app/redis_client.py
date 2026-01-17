from redis.asyncio import Redis
from typing import Optional
import logging

logger = logging.getLogger(__name__)

redis_client : Optional[Redis] = None

async def connect_redis() -> Redis :
    global redis_client

    redis_client = Redis(
        host = "localhost",
        port = 6379,
        decode_responses=True,
        encoding="utf-8",
        db=0
    )

    try :
        result = await redis_client.ping()
        logger.info(f"Redis 연결 성공 : {result}")
    except Exception as e :
        logger.warning(f"Redis 연결 실패 : {e}")
        raise

    return redis_client

async def close_redis() -> None :
    global redis_client
    if redis_client :
        await redis_client.close()
        logger.info("Redis 연결 종료")
    else :
        logger.warning("Redis가 연결되어 있지 않음")

def get_redis() -> Redis :
    if redis_client is None :
        raise RuntimeError("Redis가 연결되어 있지 않습니다. 먼저 연결해주세요")

    return redis_client