"""Error response schema."""
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class StandardErrorResponse(BaseModel):
    error: ErrorDetail
