"""
Base classes for biological validation.

This module provides the foundational classes for all validators.
All validators must inherit from BiologicalValidator.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation failures."""

    CRITICAL = "critical"  # Wrong coordinates = wrong patient implications
    HIGH = "high"          # Mismatched REF allele = technical artifact
    MEDIUM = "medium"      # Missing annotation = incomplete report
    LOW = "low"            # Formatting inconsistencies = aesthetics


@dataclass
class ValidationResult:
    """Result of a validation check."""

    is_valid: bool
    severity: ValidationSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

    def __str__(self) -> str:
        """String representation of validation result."""
        status = "✓ PASS" if self.is_valid else "❌ FAIL"
        return f"{status} [{self.severity.value.upper()}]: {self.message}"


class BiologicalValidator(ABC):
    """
    Base class for all biological validators.

    All validators must implement the validate() method to check
    biological constraints and return detailed validation results.
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, fail on any validation error.
                        If False, only fail on CRITICAL errors.
        """
        self.strict_mode = strict_mode
        self._validation_history: List[ValidationResult] = []

    @abstractmethod
    def validate(self, *args, **kwargs) -> ValidationResult:
        """
        Validate biological data.

        This method must be implemented by all subclasses.

        Returns:
            ValidationResult with status and details
        """
        pass

    def should_fail(self, result: ValidationResult) -> bool:
        """
        Determine if a validation result should cause failure.

        Args:
            result: The validation result to check

        Returns:
            True if the result should cause a failure
        """
        if self.strict_mode:
            return not result.is_valid
        else:
            # In non-strict mode, only CRITICAL failures matter
            return not result.is_valid and result.severity == ValidationSeverity.CRITICAL

    def record_validation(self, result: ValidationResult) -> None:
        """
        Record a validation result in history.

        Args:
            result: The validation result to record
        """
        self._validation_history.append(result)

    def get_validation_history(self) -> List[ValidationResult]:
        """
        Get all validation results from this session.

        Returns:
            List of validation results
        """
        return self._validation_history.copy()

    def get_failed_validations(self) -> List[ValidationResult]:
        """
        Get only failed validation results.

        Returns:
            List of failed validation results
        """
        return [r for r in self._validation_history if not r.is_valid]

    def clear_history(self) -> None:
        """Clear the validation history."""
        self._validation_history.clear()


class CompositeValidator(BiologicalValidator):
    """
    Validator that combines multiple validators.

    Useful for running a suite of validation checks.
    """

    def __init__(self, validators: List[BiologicalValidator], strict_mode: bool = True):
        """
        Initialize the composite validator.

        Args:
            validators: List of validators to run
            strict_mode: If True, fail on any validation error
        """
        super().__init__(strict_mode=strict_mode)
        self.validators = validators

    def validate(self, *args, **kwargs) -> ValidationResult:
        """
        Run all validators and aggregate results.

        Returns:
            Aggregated validation result
        """
        results = []

        for validator in self.validators:
            result = validator.validate(*args, **kwargs)
            results.append(result)
            self.record_validation(result)

        # Aggregate results
        all_valid = all(r.is_valid for r in results)
        failed_results = [r for r in results if not r.is_valid]

        if all_valid:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.LOW,
                message="All validation checks passed",
                details={"total_checks": len(results)}
            )
        else:
            # Get the highest severity from failed checks
            max_severity = max((r.severity for r in failed_results),
                             key=lambda s: ["low", "medium", "high", "critical"].index(s.value))

            return ValidationResult(
                is_valid=False,
                severity=max_severity,
                message=f"{len(failed_results)}/{len(results)} validation checks failed",
                details={
                    "total_checks": len(results),
                    "failed_checks": len(failed_results),
                    "failures": [str(r) for r in failed_results]
                },
                suggestions=["Review failed checks for details"]
            )
