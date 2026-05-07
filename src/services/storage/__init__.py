from .s3 import S3StorageProvider

# Aquí aplicamos DIP: El sistema usa la implementación de S3 por defecto,
# pero podría cambiarse fácilmente en un solo lugar.
storage_service = S3StorageProvider()
