from fastapi import APIRouter, Depends
from pydantic import BaseModel

from di.services import get_student_service, get_calculation_service
from services.student import StudentService
from services.calculation import CalculationService

router = APIRouter()


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
