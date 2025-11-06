from abc import ABC, abstractmethod
from typing import List

from domain.student import Student
from domain.distribution import StudentDistribution, InstituteWeights, ScoredStudent


class IStudentRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Student]:
        pass


class IDistributionRepository(ABC):
    @abstractmethod
    async def get_students(self) -> List[StudentDistribution]:
        pass

    @abstractmethod
    async def get_institute_weights(self) -> List[InstituteWeights]:
        pass

    @abstractmethod
    async def save_ranking(self, students: List[ScoredStudent]) -> None:
        pass
