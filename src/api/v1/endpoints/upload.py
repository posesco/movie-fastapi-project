from fastapi import APIRouter, UploadFile, File, Query, HTTPException, status
from typing import Optional
import uuid

from src.api.deps import CurrentUserDep
from src.services.storage import storage_service
from src.services.storage.strategies import UploadContext, resolve_path

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    current_user: CurrentUserDep,
    file: UploadFile = File(...),
    context: UploadContext = Query(
        UploadContext.GENERAL, 
        description="Business context for the upload"
    )
) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content type {file.content_type} not allowed. Allowed: {ALLOWED_CONTENT_TYPES}"
        )

    # Generate unique filename
    extension = file.filename.split(".")[-1] if "." in file.filename else ""
    unique_filename = str(uuid.uuid4())
    if extension:
        unique_filename = f"{unique_filename}.{extension}"

    # Resolve controlled path instead of accepting arbitrary folder
    path = resolve_path(context, current_user.id, unique_filename)

    file_bytes = await file.read()

    url = await storage_service.upload_file(
        file_bytes=file_bytes,
        key=path,
        content_type=file.content_type
    )

    return {
        "url": url,
        "filename": unique_filename,
        "path": path,
        "context": context
    }

