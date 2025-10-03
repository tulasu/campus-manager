from fastapi import APIRouter, Depends

from di.services import get_student_service
from services.student import StudentService

router = APIRouter()


@router.get("/students")
async def get_rows(service: StudentService = Depends(get_student_service)):
    return {"rows": await service.list_students()}
