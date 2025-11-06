"""Business logic for campus distribution calculation."""

from typing import List, Dict, Optional

from core.exceptions import CalculationError, DataValidationError
from core.logging import get_logger
from domain.distribution import (
    StudentDistribution,
    InstituteWeights,
    NormalizedStudent,
    ScoredStudent
)
from repositories.interfaces import IDistributionRepository

logger = get_logger(__name__)


class CalculationService:
    """Service for calculating campus distribution rankings."""

    DISTANCE_NORMALIZATION_FACTOR = 500.0

    def __init__(self, repository: IDistributionRepository) -> None:
        """Initialize calculation service."""
        self.repository = repository

    async def calculate_distribution(self) -> List[ScoredStudent]:
        """
        Calculate complete student distribution ranking.

        Returns:
            List of students sorted by priority and score
        """
        try:
            logger.info("Starting campus distribution calculation")

            # 1. Retrieve raw data
            raw_students = await self._retrieve_student_data()
            raw_weights = await self._retrieve_weight_data()

            # 2. Process data
            normalized_students = self._normalize_student_data(raw_students)
            weights_dict = self._create_weights_dictionary(raw_weights)

            # 3. Calculate scores
            scored_students = self._calculate_student_scores(normalized_students, weights_dict)

            # 4. Sort and rank
            ranked_students = self._rank_students(scored_students)

            # 5. Save results
            await self._save_results(ranked_students)

            logger.info(f"Successfully calculated distribution for {len(ranked_students)} students")
            return ranked_students

        except Exception as e:
            logger.error(f"Calculation failed: {str(e)}")
            raise CalculationError(f"Distribution calculation failed: {str(e)}")

    async def _retrieve_student_data(self) -> List[StudentDistribution]:
        """Retrieve and validate student data."""
        logger.info("Retrieving student data")
        students = await self.repository.get_students()

        if not students:
            raise DataValidationError("No student data available for processing")

        logger.info(f"Retrieved {len(students)} student records")
        return students

    async def _retrieve_weight_data(self) -> List[InstituteWeights]:
        """Retrieve and validate institute weight data."""
        logger.info("Retrieving institute weights")
        weights = await self.repository.get_institute_weights()

        if not weights:
            raise DataValidationError("No weight data available for processing")

        logger.info(f"Retrieved weights for {len(weights)} institutes")
        return weights

    def _normalize_student_data(self, students: List[StudentDistribution]) -> List[NormalizedStudent]:
        """Convert raw student data to normalized format."""
        logger.debug(f"Normalizing {len(students)} student records")

        normalized = []
        for student in students:
            try:
                normalized_student = NormalizedStudent(
                    fio=student.fio,
                    gender=student.gender,
                    institute=student.institute,
                    svo=bool(student.svo),
                    chaes=bool(student.chaes),
                    disability=bool(student.disability),
                    smoking=bool(student.smoking),
                    distance=student.distance / self.DISTANCE_NORMALIZATION_FACTOR,
                    large_family=bool(student.large_family)
                )
                normalized.append(normalized_student)
            except Exception as e:
                logger.warning(f"Failed to normalize student {student.fio}: {e}")

        if not normalized:
            raise DataValidationError("No valid student records after normalization")

        logger.debug(f"Successfully normalized {len(normalized)} student records")
        return normalized

    def _create_weights_dictionary(self, weights: List[InstituteWeights]) -> Dict[str, InstituteWeights]:
        """Create a dictionary mapping institute names to their weights."""
        logger.debug(f"Creating weights dictionary for {len(weights)} institutes")

        weights_dict = {}
        missing_weights = []

        for weight in weights:
            if weight.institute:
                weights_dict[weight.institute] = weight
            else:
                missing_weights.append(weight)

        if missing_weights:
            logger.warning(f"Found {len(missing_weights)} weight records without institute names")

        logger.debug(f"Created weights dictionary with {len(weights_dict)} entries")
        return weights_dict

    def _calculate_student_scores(
        self,
        students: List[NormalizedStudent],
        weights: Dict[str, InstituteWeights]
    ) -> List[ScoredStudent]:
        """Calculate scores for all students."""
        logger.debug(f"Calculating scores for {len(students)} students")

        scored_students = []
        calculation_errors = 0

        for student in students:
            try:
                scored_student = self._calculate_single_student_score(student, weights)
                scored_students.append(scored_student)
            except Exception as e:
                calculation_errors += 1
                logger.warning(f"Failed to calculate score for student {student.fio}: {e}")

        if calculation_errors > 0:
            logger.warning(f"Score calculation failed for {calculation_errors} students")

        if not scored_students:
            raise CalculationError("No student scores could be calculated")

        logger.debug(f"Successfully calculated scores for {len(scored_students)} students")
        return scored_students

    def _calculate_single_student_score(
        self,
        student: NormalizedStudent,
        weights: Dict[str, InstituteWeights]
    ) -> ScoredStudent:
        """Calculate score for a single student."""
        institute_weights = weights.get(student.institute)
        if not institute_weights:
            raise ValueError(f"No weights found for institute: {student.institute}")

        # Calculate individual scores
        svo_score = int(student.svo) * institute_weights.svo_weight
        chaes_score = int(student.chaes) * institute_weights.chaes_weight
        disability_score = int(student.disability) * institute_weights.disability_weight
        smoking_score = int(student.smoking) * 1  # Fixed weight for smoking
        distance_score = student.distance * institute_weights.distance_weight
        large_family_score = int(student.large_family) * institute_weights.large_family_weight

        # Calculate total score
        total_score = (
            institute_weights.institute_score +
            svo_score + chaes_score + disability_score +
            smoking_score + distance_score + large_family_score
        )

        # Determine priority status
        priority = student.svo or student.chaes or student.disability

        return ScoredStudent(
            fio=student.fio,
            gender=student.gender,
            institute_score=institute_weights.institute_score,
            svo_score=svo_score,
            chaes_score=chaes_score,
            disability_score=disability_score,
            smoking_score=smoking_score,
            distance_score=distance_score,
            large_family_score=large_family_score,
            total_score=total_score,
            priority=priority
        )

    def _rank_students(self, students: List[ScoredStudent]) -> List[ScoredStudent]:
        """Sort students by priority and score."""
        logger.debug(f"Ranking {len(students)} students")

        # Separate by priority
        priority_students = [s for s in students if s.priority]
        regular_students = [s for s in students if not s.priority]

        # Sort each group by total score (descending)
        priority_students.sort(key=lambda x: x.total_score, reverse=True)
        regular_students.sort(key=lambda x: x.total_score, reverse=True)

        # Combine: priority students first
        ranked = priority_students + regular_students

        # Log top results
        if ranked:
            logger.info("Top 3 students:")
            for i, student in enumerate(ranked[:3], 1):
                logger.info(
                    f"  {i}. {student.fio}: {student.total_score:.2f} points "
                    f"(priority: {student.priority}, institute: {student.institute_score})"
                )

        logger.info(f"Ranked {len(ranked)} students "
                   f"({len(priority_students)} priority, {len(regular_students)} regular)")
        return ranked

    async def _save_results(self, students: List[ScoredStudent]) -> None:
        """Save calculation results to repository."""
        logger.info(f"Saving results for {len(students)} students")
        await self.repository.save_ranking(students)
        logger.info("Results successfully saved")