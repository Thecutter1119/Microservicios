from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.api.schemas.response import StandardResponse
from app.infrastructure.database import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health", response_model=StandardResponse)
async def health(request: Request) -> StandardResponse:
    request_id = getattr(request.state, "request_id", "DOM-unknown")
    db_ok = check_database_connection()
    return StandardResponse(
        request_id=request_id,
        success=True,
        data={"status": "ok", "database": "connected" if db_ok else "not_connected"},
        message="Service is healthy" if db_ok else "Service is running but database is not connected",
        timestamp=datetime.now(timezone.utc),
    )
