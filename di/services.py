from fastapi import Depends

from di.repositories import get_student_repository
from repositories.interfaces import IStudentRepository
from services.student import StudentService


def get_student_service(
        repo: IStudentRepository = Depends(get_student_repository),
) -> StudentService:
    return StudentService(repo)