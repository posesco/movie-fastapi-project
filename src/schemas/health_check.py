from pydantic import BaseModel
from datetime import datetime


class HealthCheck(BaseModel):
    status: str
    version: str
    db_status: str
    timestamp: datetime
