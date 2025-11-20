from fastapi import Depends

from di.repositories import get_student_repository, get_distribution_repository
from repositories.interfaces import IStudentRepository, IDistributionRepository
from services.student import StudentService
from services.calculation import CalculationService
from services.form_submission import FormSubmissionService


def get_student_service(
        repo: IStudentRepository = Depends(get_student_repository),
) -> StudentService:
    return StudentService(repo)


def get_calculation_service(
        repo: IDistributionRepository = Depends(get_distribution_repository),
) -> CalculationService:
    return CalculationService(repo)


def get_form_submission_service(
        repo: IDistributionRepository = Depends(get_distribution_repository),
) -> FormSubmissionService:
    return FormSubmissionService(repo)