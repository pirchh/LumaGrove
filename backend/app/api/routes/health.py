from fastapi import APIRouter

from app.core.config import settings
from app.db.session import get_db_health

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "database": get_db_health(),
    }
