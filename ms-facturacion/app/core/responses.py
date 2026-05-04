from datetime import datetime, timezone
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from app.core.middleware import get_current_request_id

DataT = TypeVar("DataT")


class StandardResponse(BaseModel, Generic[DataT]):
    request_id: str = Field(default_factory=get_current_request_id)
    success: bool
    data: Optional[DataT] = None
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def build_success_response(data: Any, message: str = "Operacion exitosa") -> StandardResponse:
    return StandardResponse(success=True, data=data, message=message)


def build_error_response(message: str, data: Any = None) -> StandardResponse:
    return StandardResponse(success=False, data=data, message=message)
