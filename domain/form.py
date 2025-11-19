"""Domain models for form submissions."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class FormSubmission(BaseModel):
    """Model for form submission data from external sources (e.g., Yandex Forms)."""
    
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Form submission data as key-value pairs"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="HTTP headers from the request"
    )
    method: Optional[str] = Field(
        default=None,
        description="HTTP method used for submission"
    )
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for flexibility

