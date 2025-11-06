"""Domain models for campus distribution system."""

from __future__ import annotations
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, field_validator, model_validator


class Gender(str, Enum):
    """Gender enumeration."""
    MALE = "М"
    FEMALE = "Ж"


class StudentDistribution(BaseModel):
    """Raw student data from Google Sheets."""

    fio: str = Field(..., alias="ФИО", description="Student full name")
    gender: str = Field(..., alias="Пол", description="Student gender")
    institute: str = Field(..., alias="Институт", description="Student institute")
    svo: int = Field(..., alias="СВО", description="SVO status (0 or 1)")
    chaes: int = Field(..., alias="ЧАЭС", description="ChAES status (0 or 1)")
    disability: int = Field(..., alias="Инвалидность", description="Disability status (0 or 1)")
    smoking: int = Field(..., alias="Курение", description="Smoking status (0 or 1)")
    distance: int = Field(..., alias="Расстояние", description="Distance to university (km)")
    large_family: int = Field(..., alias="Многодетная семья", description="Large family status (0 or 1)")

    model_config = dict(populate_by_name=True)

    @field_validator("svo", "chaes", "disability", "smoking", "large_family", mode="before")
    @classmethod
    def cast_binary_to_int(cls, v: Any) -> int:
        """Convert binary values to integers (0 or 1)."""
        if isinstance(v, bool):
            return 1 if v else 0
        if not isinstance(v, int):
            try:
                return max(0, min(1, int(v)))
            except (ValueError, TypeError):
                return 0
        return max(0, min(1, v))

    @field_validator("distance", mode="before")
    @classmethod
    def cast_distance(cls, v: Any) -> int:
        """Convert distance to non-negative integer."""
        if not isinstance(v, int):
            try:
                return max(0, int(v))
            except (ValueError, TypeError):
                return 0
        return max(0, v)

    @field_validator("fio", "institute")
    @classmethod
    def normalize_string_fields(cls, v: str) -> str:
        """Normalize string fields by stripping whitespace."""
        return str(v).strip() if v else ""

    @model_validator(mode="after")
    def validate_student_data(self) -> StudentDistribution:
        """Validate student data consistency."""
        if not self.fio.strip():
            raise ValueError("Student name (FIO) cannot be empty")
        if not self.institute.strip():
            raise ValueError("Institute cannot be empty")
        return self


class InstituteWeights(BaseModel):
    """Institute-specific weights for distribution criteria."""

    institute: str = Field(..., alias="", description="Institute name")
    institute_score: int = Field(..., alias="Баллы за институт", description="Base score for institute")
    svo_weight: int = Field(..., alias="СВО", description="Weight for SVO status")
    chaes_weight: int = Field(..., alias="ЧАЭС", description="Weight for ChAES status")
    disability_weight: int = Field(..., alias="Инвалидность", description="Weight for disability status")
    distance_weight: int = Field(..., alias="Расстояние", description="Weight for distance")
    large_family_weight: int = Field(..., alias="Многодетная семья", description="Weight for large family status")

    model_config = dict(populate_by_name=True)

    @field_validator("institute_score", "svo_weight", "chaes_weight", "disability_weight", "distance_weight", "large_family_weight", mode="before")
    @classmethod
    def cast_to_positive_int(cls, v: Any) -> int:
        """Convert to non-negative integer."""
        if not isinstance(v, int):
            try:
                return max(0, int(v))
            except (ValueError, TypeError):
                return 0
        return max(0, v)

    @field_validator("institute")
    @classmethod
    def normalize_institute_name(cls, v: str) -> str:
        """Normalize institute name."""
        return str(v).strip() if v else ""

    @model_validator(mode="after")
    def validate_weights(self) -> InstituteWeights:
        """Validate weight configuration."""
        if not self.institute.strip():
            raise ValueError("Institute name cannot be empty")
        if self.institute_score < 0:
            raise ValueError("Institute score cannot be negative")
        return self


class NormalizedStudent(BaseModel):
    """Student data with normalized values for calculation."""

    fio: str = Field(..., description="Student full name")
    gender: str = Field(..., description="Student gender")
    institute: str = Field(..., description="Student institute")
    svo: bool = Field(..., description="SVO status")
    chaes: bool = Field(..., description="ChAES status")
    disability: bool = Field(..., description="Disability status")
    smoking: bool = Field(..., description="Smoking status")
    distance: float = Field(..., description="Normalized distance (distance / 500)")
    large_family: bool = Field(..., description="Large family status")

    @model_validator(mode="after")
    def validate_normalized_data(self) -> NormalizedStudent:
        """Validate normalized student data."""
        if not self.fio.strip():
            raise ValueError("Student name cannot be empty")
        if self.distance < 0:
            raise ValueError("Distance cannot be negative")
        return self


class ScoredStudent(BaseModel):
    """Student with calculated scores for distribution ranking."""

    fio: str = Field(..., description="Student full name")
    gender: str = Field(..., description="Student gender")
    institute_score: int = Field(..., description="Base institute score")
    svo_score: int = Field(..., description="Calculated SVO score")
    chaes_score: int = Field(..., description="Calculated ChAES score")
    disability_score: int = Field(..., description="Calculated disability score")
    smoking_score: int = Field(..., description="Calculated smoking score")
    distance_score: float = Field(..., description="Calculated distance score")
    large_family_score: int = Field(..., description="Calculated large family score")
    total_score: float = Field(..., description="Total calculated score")
    priority: bool = Field(..., description="Has priority status (SVO/ChAES/Disability)")

    @model_validator(mode="after")
    def validate_scores(self) -> ScoredStudent:
        """Validate calculated scores."""
        if self.total_score < 0:
            raise ValueError("Total score cannot be negative")
        return self

    def __lt__(self, other: ScoredStudent) -> bool:
        """Compare students for sorting."""
        if self.priority != other.priority:
            return self.priority > other.priority  # Priority students come first
        return self.total_score > other.total_score  # Higher score comes first