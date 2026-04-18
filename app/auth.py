import hashlib
import secrets
import os
import logging
from typing import Optional

from fastapi import Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db_models import ApiKey
from app.exceptions import ApiKeyMissingError, ApiKeyInvalidError

logger = logging.getLogger(__name__)


def generate_api_key() -> tuple[str, str, str]:
    """API Key 생성. (plain_key, salt, key_hash) 반환."""
    plain_key = secrets.token_urlsafe(32)
    salt = secrets.token_hex(16)
    key_hash = hash_api_key(plain_key, salt)
    return plain_key, salt, key_hash


def hash_api_key(plain_key: str, salt: str) -> str:
    """SHA-256으로 API Key 해싱."""
    return hashlib.sha256(f"{salt}{plain_key}".encode()).hexdigest()


async def verify_api_key(
    x_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    """X-API-Key 헤더 검증. 유효하지 않으면 401."""
    if not x_api_key:
        raise ApiKeyMissingError()

    result = await db.execute(
        select(ApiKey).where(ApiKey.revoked == 0)
    )
    keys = result.scalars().all()

    for key_record in keys:
        if hash_api_key(x_api_key, key_record.salt) == key_record.key_hash:
            return key_record

    raise ApiKeyInvalidError()


def verify_admin_key(x_admin_key: Optional[str] = Header(None)) -> str:
    """관리자 키 검증."""
    admin_key = os.getenv("ADMIN_KEY", "")
    if not x_admin_key or x_admin_key != admin_key:
        raise HTTPException(status_code=401, detail="관리자 키가 필요합니다")
    return x_admin_key
