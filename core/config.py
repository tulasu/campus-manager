"""Application configuration settings."""

from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Any


class Settings(BaseSettings):
    """Application settings."""

    google_service_account: str = Field(
        default="service_account.json",
        description="Path to Google service account JSON file"
    )
    google_sheet_id: str = Field(
        description="Google Sheet ID for campus management"
    )
    db_connection_url: str = Field(
        default="sqlite:///database.db",
        description="Database connection URL"
    )

    # Application settings
    app_name: str = Field(default="Campus Manager", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Google Sheets settings
    students_sheet_index: int = Field(default=0, description="Index of students sheet")
    weights_sheet_index: int = Field(default=1, description="Index of weights sheet")
    results_sheet_index: int = Field(default=2, description="Index of results sheet")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("google_sheet_id")
    @classmethod
    def validate_sheet_id(cls, v: str) -> str:
        """Validate Google Sheet ID format."""
        if not v or len(v) < 10:
            raise ValueError("Google Sheet ID must be a valid non-empty string")
        return v

    @field_validator("students_sheet_index", "weights_sheet_index", "results_sheet_index")
    @classmethod
    def validate_sheet_indices(cls, v: int) -> int:
        """Validate sheet indices are non-negative."""
        if v < 0:
            raise ValueError("Sheet indices must be non-negative")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
