"""
Verification Module: Biological Validation Layer

The "Ground Truth" - validates agent outputs against biological constraints.
This is critical because LLM hallucinations in genomics can mean misdiagnoses.

Available Validators:
- CoordinateValidator: Validate genomic coordinates
- VariantValidator: Validate variant calls
- ConstraintValidator: Validate biological constraints
- ReferenceChecker: Cross-check with databases (placeholder)
- CompositeValidator: Combine multiple validators
"""

from .base import (
    BiologicalValidator,
    ValidationResult,
    ValidationSeverity,
    CompositeValidator,
)
from .coordinate_validator import CoordinateValidator
from .variant_validator import VariantValidator
from .constraints import ConstraintValidator
from .reference_checker import ReferenceChecker


__all__ = [
    # Base classes
    "BiologicalValidator",
    "ValidationResult",
    "ValidationSeverity",
    "CompositeValidator",
    # Validators
    "CoordinateValidator",
    "VariantValidator",
    "ConstraintValidator",
    "ReferenceChecker",
]
