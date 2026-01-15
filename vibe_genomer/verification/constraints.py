"""
Biological constraint validators.

Encodes biological "sanity checks" that data must satisfy:
- GC content should be 0-1, not percentages
- PHRED scores are typically 0-60
- Coverage values can't be negative
- VCF quality scores can't be negative
"""

from typing import Any, Optional

from .base import BiologicalValidator, ValidationResult, ValidationSeverity


class ConstraintValidator(BiologicalValidator):
    """
    Validates biological constraints and reasonable value ranges.
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize the constraint validator.

        Args:
            strict_mode: If True, fail on any validation error
        """
        super().__init__(strict_mode=strict_mode)

    def validate_gc_content(self, gc_content: float) -> ValidationResult:
        """
        Validate GC content is in valid range [0, 1].

        Args:
            gc_content: GC content as fraction (0-1)

        Returns:
            ValidationResult
        """
        if gc_content < 0 or gc_content > 1:
            # Check if it looks like a percentage (0-100)
            if 0 <= gc_content <= 100:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"GC content should be a fraction (0-1), not percentage. Got {gc_content}",
                    details={"gc_content": gc_content},
                    suggestions=[f"Convert to fraction: {gc_content / 100:.4f}"]
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"GC content must be between 0 and 1. Got {gc_content}",
                    details={"gc_content": gc_content}
                )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.MEDIUM,
            message=f"GC content {gc_content:.4f} is valid",
            details={"gc_content": gc_content}
        )

    def validate_phred_score(self, score: float, allow_high: bool = False) -> ValidationResult:
        """
        Validate PHRED quality score is in reasonable range.

        Args:
            score: PHRED score
            allow_high: If True, allow scores > 60 (some platforms produce higher scores)

        Returns:
            ValidationResult
        """
        if score < 0:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.HIGH,
                message=f"PHRED score cannot be negative. Got {score}",
                details={"score": score}
            )

        if score > 60 and not allow_high:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"PHRED score {score} is unusually high (typically 0-60)",
                details={"score": score},
                suggestions=[
                    "Check if score is correct",
                    "Some platforms (e.g., PacBio) can produce scores > 60",
                    "Use allow_high=True if this is expected"
                ]
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.MEDIUM,
            message=f"PHRED score {score} is valid",
            details={"score": score}
        )

    def validate_coverage(self, coverage: float) -> ValidationResult:
        """
        Validate coverage depth is non-negative.

        Args:
            coverage: Coverage depth

        Returns:
            ValidationResult
        """
        if coverage < 0:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.HIGH,
                message=f"Coverage cannot be negative. Got {coverage}",
                details={"coverage": coverage}
            )

        # Warn if coverage is suspiciously high
        if coverage > 10000:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.LOW,
                message=f"Coverage {coverage}x is very high (possibly multi-mapping or repetitive region)",
                details={"coverage": coverage},
                suggestions=["Verify this is expected for your data"]
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.MEDIUM,
            message=f"Coverage {coverage}x is valid",
            details={"coverage": coverage}
        )

    def validate_mapping_quality(self, mapq: int) -> ValidationResult:
        """
        Validate mapping quality score is in valid range [0, 255].

        Args:
            mapq: Mapping quality score

        Returns:
            ValidationResult
        """
        if mapq < 0 or mapq > 255:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.HIGH,
                message=f"Mapping quality must be 0-255. Got {mapq}",
                details={"mapq": mapq}
            )

        if mapq == 255:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.LOW,
                message="Mapping quality is 255 (unavailable/not applicable)",
                details={"mapq": mapq}
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.MEDIUM,
            message=f"Mapping quality {mapq} is valid",
            details={"mapq": mapq}
        )

    def validate_vcf_quality(self, qual: float) -> ValidationResult:
        """
        Validate VCF quality score is non-negative.

        Args:
            qual: VCF QUAL field value

        Returns:
            ValidationResult
        """
        if qual < 0:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.HIGH,
                message=f"VCF quality score cannot be negative. Got {qual}",
                details={"qual": qual}
            )

        if qual == 0:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.LOW,
                message="VCF quality is 0 (typically means quality unknown)",
                details={"qual": qual}
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.MEDIUM,
            message=f"VCF quality {qual} is valid",
            details={"qual": qual}
        )

    def validate_allele_frequency(self, af: float) -> ValidationResult:
        """
        Validate allele frequency is in valid range [0, 1].

        Args:
            af: Allele frequency

        Returns:
            ValidationResult
        """
        if af < 0 or af > 1:
            # Check if it looks like a percentage
            if 0 <= af <= 100:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"Allele frequency should be a fraction (0-1), not percentage. Got {af}",
                    details={"af": af},
                    suggestions=[f"Convert to fraction: {af / 100:.4f}"]
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.HIGH,
                    message=f"Allele frequency must be between 0 and 1. Got {af}",
                    details={"af": af}
                )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.MEDIUM,
            message=f"Allele frequency {af:.4f} is valid",
            details={"af": af}
        )

    def validate_read_length(self, length: int) -> ValidationResult:
        """
        Validate read length is reasonable.

        Args:
            length: Read length in base pairs

        Returns:
            ValidationResult
        """
        if length <= 0:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.HIGH,
                message=f"Read length must be positive. Got {length}",
                details={"length": length}
            )

        # Warn about unusual lengths
        if length < 25:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.LOW,
                message=f"Read length {length} bp is unusually short",
                details={"length": length},
                suggestions=["Typical short reads: 50-300 bp"]
            )

        if length > 100000:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.LOW,
                message=f"Read length {length:,} bp is very long (possibly long-read sequencing)",
                details={"length": length},
                suggestions=["Typical long reads: 10,000-100,000 bp"]
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.LOW,
            message=f"Read length {length} bp is valid",
            details={"length": length}
        )

    def validate_insert_size(self, insert_size: int) -> ValidationResult:
        """
        Validate paired-end insert size is reasonable.

        Args:
            insert_size: Insert size in base pairs

        Returns:
            ValidationResult
        """
        if insert_size < 0:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.HIGH,
                message=f"Insert size cannot be negative. Got {insert_size}",
                details={"insert_size": insert_size}
            )

        # Warn about unusual insert sizes
        if insert_size < 100:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.LOW,
                message=f"Insert size {insert_size} bp is very small",
                details={"insert_size": insert_size},
                suggestions=["Typical insert size: 300-500 bp for Illumina"]
            )

        if insert_size > 10000:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.LOW,
                message=f"Insert size {insert_size:,} bp is very large",
                details={"insert_size": insert_size},
                suggestions=["Check if this is mate-pair data or chimeric reads"]
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.LOW,
            message=f"Insert size {insert_size} bp is valid",
            details={"insert_size": insert_size}
        )

    def validate(self, constraint_type: str, value: Any, **kwargs) -> ValidationResult:
        """
        Main validation method that dispatches to specific constraint validators.

        Args:
            constraint_type: Type of constraint to validate
                           (gc_content, phred_score, coverage, mapping_quality,
                            vcf_quality, allele_frequency, read_length, insert_size)
            value: Value to validate
            **kwargs: Additional arguments for specific validators

        Returns:
            ValidationResult
        """
        validators = {
            "gc_content": self.validate_gc_content,
            "phred_score": lambda v: self.validate_phred_score(v, **kwargs),
            "coverage": self.validate_coverage,
            "mapping_quality": self.validate_mapping_quality,
            "mapq": self.validate_mapping_quality,  # Alias
            "vcf_quality": self.validate_vcf_quality,
            "qual": self.validate_vcf_quality,  # Alias
            "allele_frequency": self.validate_allele_frequency,
            "af": self.validate_allele_frequency,  # Alias
            "read_length": self.validate_read_length,
            "insert_size": self.validate_insert_size,
        }

        if constraint_type.lower() not in validators:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Unknown constraint type: {constraint_type}",
                details={"constraint_type": constraint_type},
                suggestions=[f"Available types: {', '.join(validators.keys())}"]
            )

        result = validators[constraint_type.lower()](value)
        self.record_validation(result)
        return result
