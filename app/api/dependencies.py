# app/api/dependencies.py
"""
FastAPI dependencies and dependency injection
"""
from fastapi import Header, HTTPException
from typing import Optional
import os

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key (optional - for future use)
    Currently allows all requests
    """
    # For MVP, no authentication required
    # In production, implement proper API key validation
    return x_api_key or "development"

def get_max_file_size() -> int:
    """Get maximum file size from environment"""
    return int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024
