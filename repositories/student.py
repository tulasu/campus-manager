import asyncio

import gspread
from typing import List

from domain.student import Student
from repositories.interfaces import IStudentRepository


class StudentRepository(IStudentRepository):
    def __init__(self, db: gspread.Spreadsheet, sheet_name: str = "students"):
        self.db = db
        self.sheet_name = sheet_name

    async def get_all(self) -> List[Student]:
        def fetch_data():
            sheet = self.db.worksheet(self.sheet_name)
            return sheet.get_all_records()  # List[Dict]

        records = await asyncio.to_thread(fetch_data)

        students = []
        for row in records:
            try:
                student = Student(**row)
                students.append(student)
            except Exception as e:
                print(f"Ошибка при парсинге строки {row}: {e}")
        return students

