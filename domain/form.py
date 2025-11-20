"""Domain models for form submissions."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator


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


class YandexFormAnswer(BaseModel):
    """Structured model for Yandex Form submission data."""
    
    fio: str = Field(..., description="Student full name")
    gender: str = Field(..., description="Student gender (М/Ж)")
    institute: str = Field(..., description="Student institute")
    svo: bool = Field(default=False, description="SVO status")
    chaes: bool = Field(default=False, description="ChAES status")
    disability: bool = Field(default=False, description="Disability status")
    smoking: bool = Field(default=False, description="Smoking status")
    distance: int = Field(..., description="Distance to university (km)")
    large_family: bool = Field(default=False, description="Large family status")
    
    @classmethod
    def from_yandex_form_data(cls, form_data: Dict[str, Any]) -> "YandexFormAnswer":
        """Parse Yandex Form data structure into YandexFormAnswer."""
        answer_data = form_data.get("answer", {}).get("data", {})
        
        fio = ""
        gender = ""
        institute = ""
        svo = False
        chaes = False
        disability = False
        smoking = False
        distance = 0
        large_family = False
        
        choices_fields = []
        
        for key, answer_value in answer_data.items():
            if not isinstance(answer_value, dict) or "value" not in answer_value:
                continue
                
            value = answer_value["value"]
            question = answer_value.get("question", {})
            answer_type = question.get("answer_type", {}).get("slug", "")
            slug = question.get("slug", "").lower()
            
            if "short_text" in answer_type and "9008962812222652" in key:
                fio = str(value).strip()
            
            elif "choices" in answer_type and isinstance(value, list) and len(value) > 0:
                choice_text = value[0].get("text", "").strip()
                choice_key = value[0].get("key", "").strip() if value[0].get("key") else ""
                choices_fields.append({
                    "text": choice_text,
                    "slug": slug,
                    "key": key,
                    "choice_key": choice_key
                })
            
            elif "boolean" in answer_type:
                bool_value = bool(value) if isinstance(value, bool) else False
                
                if "9008962931857116" in key or "сво" in slug:
                    svo = bool_value
                elif "9008962931965228" in key or "чаэс" in slug or "чернобыл" in slug:
                    chaes = bool_value
                elif "9008962932017656" in key or "инвалид" in slug:
                    disability = bool_value
                elif "9008962932054754" in key or "курен" in slug:
                    smoking = bool_value
                elif "9008962932178744" in key or "многодет" in slug:
                    large_family = bool_value
            
            elif ("integer" in answer_type or "number" in answer_type) and "9008962932109052" in key:
                try:
                    distance = int(value) if isinstance(value, (int, float, str)) else 0
                except (ValueError, TypeError):
                    distance = 0
        
        for choice in choices_fields:
            if "9008962931656396" in choice["key"]:
                choice_text_lower = choice["text"].lower()
                choice_key = choice.get("choice_key", "")
                if "мужск" in choice_text_lower or "9008962931656406" in choice_key:
                    gender = "М"
                    break
                elif "женск" in choice_text_lower or "1763676915652" in choice_key:
                    gender = "Ж"
                    break
        
        for choice in choices_fields:
            if "9008962931754788" in choice["key"]:
                choice_text = choice["text"]
                choice_key = choice.get("choice_key", "")
                if "9008962931754798" in choice_key or "ипмкн" in choice_text.lower():
                    institute = "ИПМКН"
                elif "1763677027754" in choice_key or "ивтс" in choice_text.lower():
                    institute = "ИВТС"
                elif "1763677032100" in choice_key or "горн" in choice_text.lower():
                    institute = "Горный"
                elif "1763677042468" in choice_key or "друг" in choice_text.lower():
                    institute = "Другой"
                else:
                    institute = choice_text
                break
        
        return cls(
            fio=fio,
            gender=gender,
            institute=institute,
            svo=svo,
            chaes=chaes,
            disability=disability,
            smoking=smoking,
            distance=distance,
            large_family=large_family
        )
    
    @field_validator("gender")
    @classmethod
    def normalize_gender(cls, v: str) -> str:
        """Normalize gender to М/Ж format."""
        v_lower = v.lower().strip()
        if "мужск" in v_lower or v == "М":
            return "М"
        elif "женск" in v_lower or v == "Ж":
            return "Ж"
        return v.strip()
    
    @field_validator("institute")
    @classmethod
    def normalize_institute(cls, v: str) -> str:
        """Normalize institute name."""
        v = v.strip()
        if "ипмкн" in v.lower():
            return "ИПМКН"
        elif "ивтс" in v.lower():
            return "ИВТС"
        elif "горн" in v.lower():
            return "Горный"
        else:
            return "Другой"
    
    def to_student_distribution_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for Google Sheets."""
        return {
            "ФИО": self.fio,
            "Пол": self.gender,
            "Институт": self.institute,
            "СВО": 1 if self.svo else 0,
            "ЧАЭС": 1 if self.chaes else 0,
            "Инвалидность": 1 if self.disability else 0,
            "Курение": 1 if self.smoking else 0,
            "Расстояние": self.distance,
            "Многодетная семья": 1 if self.large_family else 0
        }

