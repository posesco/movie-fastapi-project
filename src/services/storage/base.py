from abc import ABC, abstractmethod

class StorageProvider(ABC):
    @abstractmethod
    async def upload_file(
        self, 
        file_bytes: bytes, 
        key: str, 
        content_type: str
    ) -> str:
        """
        Sube un archivo al proveedor de almacenamiento.
        Retorna la URL pública del archivo.
        """
        pass

    @abstractmethod
    async def delete_file(self, key: str) -> None:
        """Elimina un archivo del almacenamiento."""
        pass
