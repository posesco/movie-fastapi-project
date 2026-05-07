from fastapi import APIRouter, UploadFile, File, Query, HTTPException, status
from typing import Optional
import uuid

from src.api.deps import CurrentUserDep
from src.services.storage import storage_service

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    current_user: CurrentUserDep,
    file: UploadFile = File(...),
    folder: Optional[str] = Query(None, description="Target folder in storage")
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content type {file.content_type} not allowed. Allowed: {ALLOWED_CONTENT_TYPES}"
        )

    # Generate unique filename to avoid collisions
    extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = f"{uuid.uuid4()}"
    if extension:
        unique_filename = f"{unique_filename}.{extension}"

    file_bytes = await file.read()
    
    url = await storage_service.upload_file(
        file_bytes=file_bytes,
        filename=unique_filename,
        content_type=file.content_type,
        folder=folder
    )

    return {
        "url": url,
        "filename": unique_filename,
        "content_type": file.content_type
    }
