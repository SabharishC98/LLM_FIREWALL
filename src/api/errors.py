"""
Custom exception handlers for the FastAPI application.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger("llm_firewall.errors")


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": _status_to_error(exc.status_code),
            "detail": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        },
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = exc.errors()
    detail = "; ".join(
        f"{err.get('loc', ['unknown'])[-1]}: {err.get('msg', 'invalid')}"
        for err in errors
    )
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "detail": detail},
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions."""
    logger.exception("Unhandled exception:")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "An unexpected error occurred"},
    )


def _status_to_error(status_code: int) -> str:
    """Map HTTP status code to error string."""
    mapping = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        429: "rate_limit_exceeded",
        500: "internal_error",
        502: "bad_gateway",
        503: "service_unavailable",
    }
    return mapping.get(status_code, "error")
