import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/healthz")
def liveness():
    """Liveness probe: Checks if the application process is running and returns metadata."""
    return {
        "status": "ok",
        "message": "Service is alive",
        "pod_name": os.getenv("MY_POD_NAME", "unknown-pod"),
        "node_hostname": os.getenv("MY_NODE_NAME", "unknown-node"),
    }


@router.get("/readyz")
def readiness(db: Session = Depends(get_db)):
    """Readiness probe: Checks if the database is reachable."""
    try:
        # We execute a simple query to ensure the DB connection is active
        db.execute(text("SELECT 1"))
        return {"status": "ready", "message": "Database is connected"}
    except Exception as e:
        # Return 503 Service Unavailable if the DB is down
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
