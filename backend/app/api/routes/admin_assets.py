from __future__ import annotations

import hashlib
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select

from app.db.models import Asset
from app.db.session import SessionLocal
from app.schemas.content import AssetRead

router = APIRouter(prefix="/admin/assets", tags=["admin-assets"])

ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_UPLOAD_BYTES = 12 * 1024 * 1024
MEDIA_ROOT = Path(__file__).resolve().parents[3] / "media"
UPLOAD_DIR = MEDIA_ROOT / "uploads"


def safe_filename(value: str) -> str:
    stem = Path(value).stem or "upload"
    suffix = Path(value).suffix.lower()
    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-") or "upload"
    return f"{safe_stem[:80]}{suffix}"


@router.post("/upload", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def upload_asset(file: UploadFile = File(...)) -> AssetRead:
    if file.content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only jpeg, png, webp, and gif image uploads are supported for now.",
        )

    data = await file.read()
    size = len(data)
    if size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file was empty.")
    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Uploaded file is too large.")

    digest = hashlib.sha256(data).hexdigest()
    original_filename = file.filename or "upload"
    safe_original = safe_filename(original_filename)
    suffix = Path(safe_original).suffix.lower()
    stored_filename = f"{digest[:16]}-{uuid.uuid4().hex[:8]}{suffix}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    storage_path = UPLOAD_DIR / stored_filename

    with SessionLocal() as db:
        existing = db.scalar(select(Asset).where(Asset.sha256 == digest))
        if existing is not None:
            return AssetRead.model_validate(existing)

        storage_path.write_bytes(data)
        public_url = f"/media/uploads/{stored_filename}"
        asset = Asset(
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=str(storage_path),
            public_url=public_url,
            mime_type=file.content_type or "application/octet-stream",
            size_bytes=size,
            sha256=digest,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return AssetRead.model_validate(asset)
