"""
Universal API Response Contracts & Envelopes
Adheres to backend-api-design-contracts standards.
"""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Generic response envelope for single-resource and success endpoints."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    success: bool = Field(default=True, description="Indicates whether the request completed successfully")
    data: Optional[T] = Field(default=None, description="Primary payload data")
    message: Optional[str] = Field(default=None, description="Optional human-readable informational message")


class ApiErrorResponse(BaseModel):
    """Structured error payload for failed requests and exception handlers."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    success: bool = Field(default=False, description="Always False for error responses")
    error: str = Field(..., description="Machine-readable error code in SCREAMING_SNAKE_CASE")
    message: str = Field(..., description="Human-readable error explanation")
    details: Optional[Any] = Field(default=None, description="Optional detailed diagnostics or field errors")


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated query responses."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    total: int = Field(..., description="Total number of items available across all pages")
    limit: int = Field(..., description="Maximum number of items requested per page")
    offset: int = Field(..., description="Zero-based index offset for current page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response envelope for collection endpoints."""
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    success: bool = Field(default=True, description="Indicates successful retrieval")
    data: List[T] = Field(default_factory=list, description="List of items for the current page")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
