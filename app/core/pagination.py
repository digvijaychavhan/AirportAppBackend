"""
Pagination Request Dependency & Parameters
Adheres to backend-api-design-contracts standards.
"""

from fastapi import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Encapsulates validated limit and offset parameters."""
    limit: int = Field(default=50, ge=1, le=200, description="Maximum number of items to return (1-200)")
    offset: int = Field(default=0, ge=0, description="Zero-based index offset for items to skip")


def get_pagination_params(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return (1-200)"),
    offset: int = Query(0, ge=0, description="Zero-based index offset for items to skip")
) -> PaginationParams:
    """FastAPI query dependency providing standard limit/offset pagination parameters."""
    return PaginationParams(limit=limit, offset=offset)
