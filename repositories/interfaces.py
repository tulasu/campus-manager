from abc import ABC, abstractmethod
from typing import List

from domain.student import Student


class IStudentRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Student]:
        pass
