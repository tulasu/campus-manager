"""Google Sheets repository for campus distribution data."""

import asyncio
from typing import List, Dict, Any

import gspread

from core.config import settings
from core.exceptions import SheetNotFoundError, DataValidationError
from core.logging import get_logger
from domain.distribution import StudentDistribution, InstituteWeights, ScoredStudent
from repositories.interfaces import IDistributionRepository

logger = get_logger(__name__)


class DistributionRepository(IDistributionRepository):
    """Repository for accessing campus distribution data from Google Sheets."""

    def __init__(self, spreadsheet: gspread.Spreadsheet) -> None:
        """Initialize repository with Google Sheets client."""
        self.spreadsheet = spreadsheet
        self.students_sheet_index = settings.students_sheet_index
        self.weights_sheet_index = settings.weights_sheet_index
        self.results_sheet_index = settings.results_sheet_index

    async def get_students(self) -> List[StudentDistribution]:
        """Retrieve all students from the Google Sheets."""
        try:
            logger.info("Retrieving student data from Google Sheets")

            records = await self._fetch_sheet_data(
                self.students_sheet_index,
                "students"
            )

            if not records:
                logger.warning("No student records found")
                return []

            students = await self._parse_student_records(records)
            logger.info(f"Successfully parsed {len(students)} student records")
            return students

        except Exception as e:
            logger.error(f"Failed to retrieve students: {str(e)}")
            raise SheetNotFoundError(f"Unable to retrieve student data: {str(e)}")

    async def get_institute_weights(self) -> List[InstituteWeights]:
        """Retrieve institute weights from Google Sheets."""
        try:
            logger.info("Retrieving institute weights from Google Sheets")

            records = await self._fetch_sheet_data(
                self.weights_sheet_index,
                "weights"
            )

            if not records:
                logger.warning("No weight records found")
                return []

            weights = await self._parse_weight_records(records)
            logger.info(f"Successfully parsed {len(weights)} weight records")
            return weights

        except Exception as e:
            logger.error(f"Failed to retrieve institute weights: {str(e)}")
            raise SheetNotFoundError(f"Unable to retrieve weight data: {str(e)}")

    async def save_ranking(self, students: List[ScoredStudent]) -> None:
        """Save calculated student ranking to Google Sheets."""
        try:
            logger.info(f"Saving ranking for {len(students)} students")

            await self._save_ranking_data(students)

            logger.info("Successfully saved student ranking")

        except Exception as e:
            logger.error(f"Failed to save ranking: {str(e)}")
            raise SheetNotFoundError(f"Unable to save ranking data: {str(e)}")

    async def add_student(self, student_data: Dict[str, Any]) -> None:
        """Add a new student to the students distribution sheet."""
        try:
            logger.info("Adding new student to Google Sheets")

            await self._add_student_data(student_data)

            logger.info("Successfully added student to sheet")

        except Exception as e:
            logger.error(f"Failed to add student: {str(e)}")
            raise SheetNotFoundError(f"Unable to add student data: {str(e)}")

    async def _fetch_sheet_data(self, sheet_index: int, sheet_type: str) -> List[Dict[str, Any]]:
        """Fetch data from a specific Google Sheet."""
        def fetch_data():
            try:
                worksheets = self.spreadsheet.worksheets()
                sheet_names = [ws.title for ws in worksheets]

                logger.debug(f"Available sheets: {sheet_names}")

                if len(worksheets) <= sheet_index:
                    raise SheetNotFoundError(
                        f"Sheet index {sheet_index} not found. "
                        f"Available sheets: {len(worksheets)}"
                    )

                sheet = worksheets[sheet_index]
                logger.debug(f"Working with sheet {sheet_index + 1}: '{sheet.title}'")

                records = sheet.get_all_records()
                logger.debug(f"Retrieved {len(records)} records from {sheet_type} sheet")

                return records

            except gspread.exceptions.SpreadsheetNotFound:
                raise SheetNotFoundError("Google Spreadsheet not found or inaccessible")
            except gspread.exceptions.WorksheetNotFound:
                raise SheetNotFoundError(f"Worksheet at index {sheet_index} not found")
            except Exception as e:
                raise SheetNotFoundError(f"Error accessing sheet: {str(e)}")

        return await asyncio.to_thread(fetch_data)

    async def _parse_student_records(self, records: List[Dict[str, Any]]) -> List[StudentDistribution]:
        """Parse raw records into StudentDistribution objects."""
        students = []
        parse_errors = 0

        for i, record in enumerate(records, 1):
            try:
                student = StudentDistribution(**record)
                students.append(student)
            except Exception as e:
                parse_errors += 1
                logger.debug(f"Failed to parse student record {i}: {e}")
                logger.debug(f"Record data: {record}")

        if parse_errors > 0:
            logger.warning(f"Failed to parse {parse_errors} student records")

        if not students and records:
            raise DataValidationError("No valid student records could be parsed")

        return students

    async def _parse_weight_records(self, records: List[Dict[str, Any]]) -> List[InstituteWeights]:
        """Parse raw records into InstituteWeights objects."""
        weights = []
        parse_errors = 0

        for i, record in enumerate(records, 1):
            try:
                weight = InstituteWeights(**record)
                weights.append(weight)
            except Exception as e:
                parse_errors += 1
                logger.debug(f"Failed to parse weight record {i}: {e}")
                logger.debug(f"Record data: {record}")

        if parse_errors > 0:
            logger.warning(f"Failed to parse {parse_errors} weight records")

        if not weights and records:
            raise DataValidationError("No valid weight records could be parsed")

        return weights

    async def _save_ranking_data(self, students: List[ScoredStudent]) -> None:
        """Save student ranking data to the results sheet."""
        def save_data():
            try:
                worksheets = self.spreadsheet.worksheets()

                if len(worksheets) <= self.results_sheet_index:
                    raise SheetNotFoundError(
                        f"Results sheet index {self.results_sheet_index} not found"
                    )

                sheet = worksheets[self.results_sheet_index]
                logger.debug(f"Saving results to sheet: '{sheet.title}'")

                # Clear existing data
                sheet.clear()
                logger.debug("Cleared existing data from results sheet")

                # Add headers
                headers = [
                    "ФИО", "Пол", "Баллы за институт", "СВО", "ЧАЭС",
                    "Инвалидность", "Курение", "Расстояние", "Многодетная семья",
                    "Общий балл", "Приоритет"
                ]
                sheet.append_row(headers)
                logger.debug("Added headers to results sheet")

                # Add student data
                for i, student in enumerate(students, 1):
                    row = [
                        student.fio,
                        student.gender,
                        student.institute_score,
                        student.svo_score,
                        student.chaes_score,
                        student.disability_score,
                        student.smoking_score,
                        round(student.distance_score, 2),
                        student.large_family_score,
                        round(student.total_score, 2),
                        "Да" if student.priority else "Нет"
                    ]
                    sheet.append_row(row)

                logger.info(f"Saved {len(students)} student records to results sheet")

            except gspread.exceptions.GSpreadException as e:
                raise SheetNotFoundError(f"Google Sheets error: {str(e)}")
            except Exception as e:
                raise SheetNotFoundError(f"Error saving ranking data: {str(e)}")

        await asyncio.to_thread(save_data)

    async def _add_student_data(self, student_data: Dict[str, Any]) -> None:
        """Add student data to the students distribution sheet."""
        def add_data():
            try:
                worksheets = self.spreadsheet.worksheets()

                if len(worksheets) <= self.students_sheet_index:
                    raise SheetNotFoundError(
                        f"Students sheet index {self.students_sheet_index} not found"
                    )

                sheet = worksheets[self.students_sheet_index]
                logger.debug(f"Adding student to sheet: '{sheet.title}'")

                row = [
                    student_data.get("ФИО", ""),
                    student_data.get("Пол", ""),
                    student_data.get("Институт", ""),
                    student_data.get("СВО", 0),
                    student_data.get("ЧАЭС", 0),
                    student_data.get("Инвалидность", 0),
                    student_data.get("Курение", 0),
                    student_data.get("Расстояние", 0),
                    student_data.get("Многодетная семья", 0)
                ]

                sheet.append_row(row)
                logger.debug(f"Added student row: {row}")

            except gspread.exceptions.GSpreadException as e:
                raise SheetNotFoundError(f"Google Sheets error: {str(e)}")
            except Exception as e:
                raise SheetNotFoundError(f"Error adding student data: {str(e)}")

        await asyncio.to_thread(add_data)