from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json

from core.logging import get_logger
from di.services import get_student_service, get_calculation_service, get_form_submission_service
from services.student import StudentService
from services.calculation import CalculationService
from services.form_submission import FormSubmissionService

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
async def receive_form_submission(
    request: Request,
    service: FormSubmissionService = Depends(get_form_submission_service)
):
    """Endpoint for receiving Yandex Form submissions."""
    try:
        body = await request.json()
        headers = dict(request.headers)
        
        logger.info("=" * 80)
        logger.info("📝 ПОЛУЧЕНЫ ДАННЫЕ ОТ ЯНДЕКС ФОРМЫ")
        logger.info("=" * 80)
        logger.info(f"Метод запроса: {request.method}")
        logger.info(f"Заголовки: {json.dumps(headers, ensure_ascii=False, indent=2)}")
        logger.info("Данные формы:")
        logger.info(json.dumps(body, ensure_ascii=False, indent=2))
        logger.info("=" * 80)
        
        result = await service.process_yandex_form_submission(body)
        
        if result["success"]:
            logger.info(f"✅ Успешно обработано: {result.get('message', '')}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=result
            )
        else:
            logger.warning(f"⚠️ Ошибка обработки: {result.get('message', '')}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=result
            )
        
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": f"Ошибка парсинга JSON: {str(e)}",
                "error": "json_decode_error"
            }
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": f"Внутренняя ошибка сервера: {str(e)}",
                "error": "internal_error"
            }
        )
