# S3 / MinIO Integration Plan

## Objective
Add optional image upload for movies using `aioboto3` (S3 compatible for AWS/GCS/Azure in PROD, MinIO in LOCAL). Keep movie creation JSON-based, add separate endpoint for image upload.

## Key Files & Context
- `src/models/movie.py`: Add `image_url` field.
- `src/schemas/movie.py`: Update models.
- `src/core/config.py`: Add S3 environment variables.
- `src/services/storage.py`: New `aioboto3` service.
- `src/api/v1/endpoints/upload.py`: Add generic `POST /upload/` endpoint.
- `compose.yml` / `docker-compose.app.yml`: Add MinIO service and bucket init container.

## Implementation Steps
1. **Infra (LOCAL)**
   - Add `minio` and `minio-init` to `docker-compose.app.yml`.
2. **Config & Models**
   - Add S3 vars to `.env.example` and `Settings`.
   - Add `image_url: Optional[str] = Field(default=None)` to `Movie` SQLModel.
   - Generate Alembic migration.
3. **Storage Service**
   - Add `aioboto3` to `requirements.txt`.
   - Implement `upload_file(file_bytes, filename, content_type, folder)` in `src/services/storage.py`.
4. **API Endpoint**
   - Add new `src/api/v1/endpoints/upload.py` with `POST /upload/` accepting `UploadFile` and optional `folder` param.
   - Validate image type.
   - Upload via storage service, return public URL.
   - Client updates entity (e.g. `Movie`) via existing `PUT` endpoints.

## Verification
- Spin up MinIO locally.
- Create movie.
- Upload image via Swagger UI.
- Verify object in MinIO bucket.
- Verify URL in DB.
