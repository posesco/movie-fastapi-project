import os
import aiofiles
from pathlib import Path
from .base import StorageProvider
from src.core.config import settings

class LocalStorageProvider(StorageProvider):
    """Storage provider that saves files to the local filesystem."""

    def __init__(self):
        self.base_path = Path(settings.local_storage_path)
        self.public_url = "/static"
        # Ensure the directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self, 
        file_bytes: bytes, 
        key: str, 
        content_type: str
    ) -> str:
        """Saves file to local path and returns the URL."""
        file_path = self.base_path / key
        
        # Ensure parent directories for the key exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, mode="wb") as f:
            await f.write(file_bytes)

        return f"{self.public_url}/{key}"

    async def delete_file(self, key: str) -> None:
        """Deletes file from local path."""
        file_path = self.base_path / key
        if file_path.exists():
            file_path.unlink()
