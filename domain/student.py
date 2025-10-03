from pydantic import BaseModel, Field, field_validator
from typing import Any


class Student(BaseModel):
    timestamp: str = Field(..., alias="Timestamp")
    group_number: str = Field(..., alias="Номер грппы")
    institute: str = Field(..., alias="Институт")
    direction: str = Field(..., alias="Направление")
    exam_score: int = Field(..., alias="Баллы ЕГЭ")
    city: str = Field(..., alias="Город")

    model_config = dict(populate_by_name=True)

    @field_validator("group_number", mode="before")
    @classmethod
    def cast_group_number(cls, v: Any) -> str:
        """
        Приводим к строке, если значение не строка
        """
        if not isinstance(v, str):
            return str(v)
        return v
