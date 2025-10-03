from domain.student import Student
from repositories.interfaces import IStudentRepository
from typing import List


class StudentService:
    def __init__(self, repo: IStudentRepository):
        self.repo = repo

    async def list_students(self) -> List[Student]:
        return await self.repo.get_all()