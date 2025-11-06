from fastapi import Depends

from di.gspread import GspreadDep
from repositories.student import StudentRepository
from repositories.distribution import DistributionRepository
from repositories.interfaces import IStudentRepository, IDistributionRepository


def get_student_repository(gspread_client: GspreadDep) -> IStudentRepository:
    return StudentRepository(gspread_client)


def get_distribution_repository(gspread_client: GspreadDep) -> IDistributionRepository:
    return DistributionRepository(gspread_client)
