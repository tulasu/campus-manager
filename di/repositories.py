from fastapi import Depends

from di.gspread import GspreadDep
from repositories.student import StudentRepository
from repositories.interfaces import IStudentRepository


def get_student_repository(gspread_client: GspreadDep) -> IStudentRepository:
    return StudentRepository(gspread_client)
