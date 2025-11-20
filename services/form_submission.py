"""Service for processing form submissions."""

from typing import Dict, Any

from typing import Dict, Any

from core.logging import get_logger
from domain.form import YandexFormAnswer
from repositories.interfaces import IDistributionRepository

logger = get_logger(__name__)


class FormSubmissionService:
    """Service for processing and saving form submissions."""

    def __init__(self, repository: IDistributionRepository):
        """Initialize service with repository."""
        self.repository = repository

    async def process_yandex_form_submission(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Yandex Form submission and save to Google Sheets."""
        try:
            logger.info("Processing Yandex Form submission")
            
            form_answer = YandexFormAnswer.from_yandex_form_data(form_data)
            
            if not form_answer.fio:
                raise ValueError("ФИО is required")
            if not form_answer.gender:
                raise ValueError("Пол is required")
            if not form_answer.institute:
                raise ValueError("Институт is required")
            
            student_data = form_answer.to_student_distribution_dict()
            await self.repository.add_student(student_data)
            
            logger.info(f"Successfully processed and saved student: {form_answer.fio}")
            
            return {
                "success": True,
                "message": f"Студент {form_answer.fio} успешно добавлен",
                "student_data": student_data
            }
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                "success": False,
                "message": f"Ошибка валидации: {str(e)}",
                "error": "validation_error"
            }
        except Exception as e:
            logger.error(f"Error processing form submission: {str(e)}")
            return {
                "success": False,
                "message": f"Ошибка обработки: {str(e)}",
                "error": "processing_error"
            }

