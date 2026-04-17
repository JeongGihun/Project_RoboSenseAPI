from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db_models import ApiKey
from app.auth import generate_api_key, verify_admin_key

router = APIRouter(prefix="/admin", tags=["관리"])


@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
async def issue_api_key(
    body: dict = None,
    admin_key: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """API Key 발급. 평문 키는 이 응답에서만 확인 가능."""
    robot_id = body.get("robot_id") if body else None
    plain_key, salt, key_hash = generate_api_key()

    api_key = ApiKey(key_hash=key_hash, salt=salt, robot_id=robot_id)
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return {
        "id": api_key.id,
        "api_key": plain_key,
        "robot_id": api_key.robot_id,
        "message": "키 발급 완료",
    }


@router.get("/api-keys")
async def list_api_keys(
    admin_key: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """발급된 API Key 목록. 해시/salt는 반환하지 않음."""
    result = await db.execute(select(ApiKey))
    keys = result.scalars().all()
    return [
        {
            "id": k.id,
            "robot_id": k.robot_id,
            "created_at": k.created_at.isoformat() if k.created_at else None,
            "revoked": k.revoked,
        }
        for k in keys
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    admin_key: str = Depends(verify_admin_key),
    db: AsyncSession = Depends(get_db),
):
    """API Key 폐기."""
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id))
    key = result.scalar_one_or_none()
    if not key:
        return {"message": "해당 키가 존재하지 않습니다"}
    key.revoked = 1
    await db.commit()
    return {"message": "키가 폐기되었습니다", "id": key_id}
