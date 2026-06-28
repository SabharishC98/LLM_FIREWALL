"""
API Middleware — Authentication & Rate Limiting

Validates X-API-Key header on every request.
Applies rate limiting via Redis.
"""

import logging
from typing import Optional

from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader

from src.db import mongo, redis as redis_db
from src.utils.hashing import hash_api_key

logger = logging.getLogger("llm_firewall.middleware")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def validate_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header),
) -> dict:
    """
    Validate the API key from X-API-Key header.
    Returns the key document from MongoDB.
    Raises HTTPException on auth failure.
    """
    # Check if key is in URL params (security violation)
    client_host = request.client.host if request.client else "unknown"
    if request.query_params.get("api_key") or request.query_params.get("apikey"):
        logger.warning(f"API key in URL params from {client_host}")
        raise HTTPException(
            status_code=401,
            detail="API key must be in X-API-Key header, not URL parameters",
        )

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Validate format
    if not api_key.startswith("fw_live_") or len(api_key) != 72:
        raise HTTPException(status_code=401, detail="Invalid API key format")

    # Look up in database
    key_hash = hash_api_key(api_key)
    keys_collection = mongo.get_keys_collection()
    
    key_doc = await keys_collection.find_one({"key_hash": key_hash})
    
    if not key_doc:
        raise HTTPException(status_code=401, detail="API key not found")

    if not key_doc.get("is_active", False):
        raise HTTPException(status_code=401, detail="API key has been revoked")

    # Check rate limits
    rate_status = await redis_db.check_rate_limit(
        api_key_id=str(key_doc["_id"])
    )

    if not rate_status.allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "limit_type": rate_status.limit_type,
                "retry_after_seconds": rate_status.retry_after_seconds,
            },
            headers={
                "Retry-After": str(rate_status.retry_after_seconds),
                "X-RateLimit-Limit": str(rate_status.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(rate_status.reset_at),
            },
        )

    # Update last_used_at
    from datetime import datetime, timezone
    await keys_collection.update_one(
        {"_id": key_doc["_id"]},
        {"$set": {"last_used_at": datetime.now(timezone.utc)}},
    )

    # Attach rate limit info for response headers
    request.state.rate_limit = rate_status
    request.state.api_key_doc = key_doc

    return key_doc


async def optional_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header),
) -> Optional[dict]:
    """
    Optional API key validation for endpoints that work
    with or without auth (e.g., /health).
    """
    if not api_key:
        return None
    return await validate_api_key(request, api_key)
