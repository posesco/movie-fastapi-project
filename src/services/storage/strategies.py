from enum import Enum
from datetime import datetime

class UploadContext(str, Enum):
    USER_AVATAR = "avatars"
    MOVIE_POSTER = "posters"
    GENERAL = "uploads"

def resolve_path(context: UploadContext, user_id: int, filename: str) -> str:
    """
    Controla la jerarquía de carpetas basándose en el contexto y el usuario.
    Evita que el cliente defina rutas arbitrarias.
    """
    date_path = datetime.now().strftime("%Y/%m")
    return f"{context.value}/user_{user_id}/{date_path}/{filename}"
