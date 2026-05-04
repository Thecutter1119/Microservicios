from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    success: bool
    data: Any
    message: str
    timestamp: datetime
