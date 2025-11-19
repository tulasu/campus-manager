from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json

from core.logging import get_logger
from di.services import get_student_service, get_calculation_service
from services.student import StudentService
from services.calculation import CalculationService
from domain.form import FormSubmission

router = APIRouter()
logger = get_logger(__name__)


class CalculateResponse(BaseModel):
    success: bool
    message: str
    students_count: int = 0


@router.get("/students")
async def get_rows(service: StudentService = Depends(get_student_service)):
    return {"rows": await service.list_students()}


@router.post("/calculate", response_model=CalculateResponse)
async def calculate_distribution(service: CalculationService = Depends(get_calculation_service)):
    """Запускает расчет распределения студентов"""
    try:
        students = await service.calculate_distribution()
        return CalculateResponse(
            success=True,
            message=f"Распределение успешно рассчитано для {len(students)} студентов",
            students_count=len(students)
        )
    except Exception as e:
        return CalculateResponse(
            success=False,
            message=f"Ошибка при расчете распределения: {str(e)}",
            students_count=0
        )


@router.post("/api/v1/form/submit")
async def receive_form_submission(request: Request):
    """
    Тестовый эндпоинт для приема данных от Яндекс Формы.
    Принимает данные и выводит их в консоль.
    """
    try:
        # Получаем тело запроса
        body = await request.json()
        
        # Получаем заголовки
        headers = dict(request.headers)
        
        # Создаем доменную модель
        form_data = FormSubmission(
            data=body,
            headers=headers,
            method=request.method
        )
        
        # Логируем в консоль
        logger.info("=" * 80)
        logger.info("📝 ПОЛУЧЕНЫ ДАННЫЕ ОТ ЯНДЕКС ФОРМЫ")
        logger.info("=" * 80)
        logger.info(f"Метод запроса: {form_data.method}")
        logger.info(f"Заголовки: {json.dumps(form_data.headers, ensure_ascii=False, indent=2)}")
        logger.info("Данные формы:")
        logger.info(json.dumps(form_data.data, ensure_ascii=False, indent=2))
        logger.info("=" * 80)
        
        # Возвращаем успешный ответ (код 200 для Яндекс Формы)
        return {
            "success": True,
            "message": "Данные успешно получены",
            "received_data": form_data.data
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": f"Ошибка парсинга JSON: {str(e)}"
            }
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": f"Ошибка обработки: {str(e)}"
            }
        )
