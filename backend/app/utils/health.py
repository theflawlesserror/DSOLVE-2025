from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import psutil
import os
from models.database import get_db
from utils.logging import logger

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        logger.info("Database health check successful")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@router.get("/metrics")
async def get_metrics():
    # Get process metrics
    process = psutil.Process(os.getpid())
    
    return {
        "process": {
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "threads": process.num_threads(),
            "connections": process.num_connections()
        },
        "system": {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage('/').total
        }
    } 