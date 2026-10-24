from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, check_db_connection

router = APIRouter(prefix="/api", tags=["Health"])


@router.get(
    "/health",
    summary="Application Health Check",
    description="Returns the operational status of the API server and verifies the database connection.",
    responses={
        200: {
            "description": "System is healthy and database is connected.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "app_name": "Student Skill Gap Analyzer",
                        "environment": "development",
                        "database": "connected",
                        "timestamp": "2026-10-24T15:30:00Z",
                    }
                }
            },
        },
        503: {
            "description": "Service is degraded; database connection failed.",
        },
    },
)
def health_check(db: Session = Depends(get_db)):
    is_db_connected = check_db_connection(db)

    payload = {
        "status": "healthy" if is_db_connected else "degraded",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "database": "connected" if is_db_connected else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if not is_db_connected:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload,
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=payload,
    )
