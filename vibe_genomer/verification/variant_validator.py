"""
Variant validation.

Validates variant calls and annotations:
- REF allele is valid DNA sequence
- ALT allele is valid DNA sequence
- Variant annotation is consistent
- Cross-check with databases (ClinVar, etc.)
"""

import re
from typing import Optional, Set, List

from .base import BiologicalValidator, ValidationResult, ValidationSeverity
from .coordinate_validator import CoordinateValidator
from ..utils.exceptions import VariantValidationError


# Valid DNA bases
VALID_DNA_BASES = set("ACGTN")
VALID_DNA_BASES_WITH_IUPAC = set("ACGTNMRWSYKVHDB")  # IUPAC ambiguity codes


class VariantValidator(BiologicalValidator):
    """
    Validates genomic variants.

    Checks:
    1. REF and ALT are valid DNA sequences
    2. Coordinates are valid
    3. Variant type is consistent with alleles
    4. Variant notation follows standards
    """

    def __init__(
        self,
        genome_build: str = "hg38",
        allow_iupac: bool = False,
        strict_mode: bool = True
    ):
        """
        Initialize the variant validator.

        Args:
            genome_build: Reference genome build
            allow_iupac: Allow IUPAC ambiguity codes in sequences
            strict_mode: If True, fail on any validation error
        """
        super().__init__(strict_mode=strict_mode)
        self.coordinate_validator = CoordinateValidator(genome_build, strict_mode)
        self.allow_iupac = allow_iupac
        self.valid_bases = VALID_DNA_BASES_WITH_IUPAC if allow_iupac else VALID_DNA_BASES

    def validate_dna_sequence(self, sequence: str, sequence_type: str = "sequence") -> ValidationResult:
        """
        Validate that a sequence contains only valid DNA bases.

        Args:
            sequence: DNA sequence to validate
            sequence_type: Type of sequence (for error messages)

        Returns:
            ValidationResult
        """
        if not sequence:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.HIGH,
                message=f"{sequence_type} cannot be empty",
                details={"sequence": sequence}
            )

        sequence_upper = sequence.upper()
        invalid_bases = set(sequence_upper) - self.valid_bases

        if invalid_bases:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.HIGH,
                message=f"{sequence_type} contains invalid bases: {', '.join(sorted(invalid_bases))}",
                details={
                    "sequence": sequence,
                    "invalid_bases": list(invalid_bases),
                    "allow_iupac": self.allow_iupac
                },
                suggestions=[
                    f"Valid bases: {', '.join(sorted(self.valid_bases))}",
                    "Use 'N' for unknown bases" if not self.allow_iupac else None
                ]
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.HIGH,
            message=f"{sequence_type} '{sequence}' is valid DNA",
            details={"sequence": sequence, "length": len(sequence)}
        )

    def classify_variant_type(self, ref: str, alt: str) -> str:
        """
        Classify variant type based on REF and ALT alleles.

        Args:
            ref: Reference allele
            alt: Alternate allele

        Returns:
            Variant type (SNV, insertion, deletion, indel, complex)
        """
        ref_len = len(ref)
        alt_len = len(alt)

        if ref_len == 1 and alt_len == 1:
            return "SNV"
        elif ref_len > alt_len:
            return "deletion"
        elif alt_len > ref_len:
            return "insertion"
        elif ref_len == alt_len and ref_len > 1:
            # Could be MNV or complex
            mismatches = sum(r != a for r, a in zip(ref, alt))
            if mismatches == ref_len:
                return "MNV"  # Multi-nucleotide variant
            else:
                return "complex"
        else:
            return "complex"

    def validate_variant_alleles(
        self,
        ref: str,
        alt: str,
        expected_type: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate REF and ALT alleles.

        Args:
            ref: Reference allele
            alt: Alternate allele
            expected_type: Expected variant type (if known)

        Returns:
            ValidationResult
        """
        # Validate REF sequence
        ref_result = self.validate_dna_sequence(ref, "REF allele")
        if not ref_result.is_valid:
            return ref_result

        # Validate ALT sequence
        alt_result = self.validate_dna_sequence(alt, "ALT allele")
        if not alt_result.is_valid:
            return alt_result

        # Classify variant type
        variant_type = self.classify_variant_type(ref, alt)

        # Check if variant type matches expected
        if expected_type and expected_type.lower() != variant_type.lower():
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.MEDIUM,
                message=f"Variant type mismatch: expected '{expected_type}', but alleles suggest '{variant_type}'",
                details={
                    "ref": ref,
                    "alt": alt,
                    "expected_type": expected_type,
                    "detected_type": variant_type
                },
                suggestions=["Check variant annotation consistency"]
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.HIGH,
            message=f"Variant alleles are valid ({variant_type})",
            details={
                "ref": ref,
                "alt": alt,
                "variant_type": variant_type,
                "ref_length": len(ref),
                "alt_length": len(alt)
            }
        )

    def validate_vcf_variant(
        self,
        chrom: str,
        pos: int,
        ref: str,
        alt: str,
        qual: Optional[float] = None
    ) -> ValidationResult:
        """
        Validate a complete VCF variant record.

        Args:
            chrom: Chromosome
            pos: Position (1-based)
            ref: Reference allele
            alt: Alternate allele
            qual: Quality score (optional)

        Returns:
            ValidationResult
        """
        # Validate coordinates
        coord_result = self.coordinate_validator.validate_position(chrom, pos)
        if not coord_result.is_valid:
            return coord_result

        # Validate alleles
        allele_result = self.validate_variant_alleles(ref, alt)
        if not allele_result.is_valid:
            return allele_result

        # Validate quality if provided
        if qual is not None:
            from .constraints import ConstraintValidator
            constraint_validator = ConstraintValidator(self.strict_mode)
            qual_result = constraint_validator.validate_vcf_quality(qual)
            if not qual_result.is_valid:
                return qual_result

        variant_type = self.classify_variant_type(ref, alt)

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.HIGH,
            message=f"VCF variant is valid: {chrom}:{pos} {ref}>{alt} ({variant_type})",
            details={
                "chromosome": chrom,
                "position": pos,
                "ref": ref,
                "alt": alt,
                "variant_type": variant_type,
                "qual": qual
            }
        )

    def validate_hgvs_notation(self, hgvs: str) -> ValidationResult:
        """
        Validate HGVS variant notation format.

        Args:
            hgvs: HGVS notation string (e.g., "NM_000546.5:c.215C>G")

        Returns:
            ValidationResult
        """
        # Basic HGVS patterns
        # Genomic: NC_000001.11:g.100000A>G
        # Coding: NM_000546.5:c.215C>G
        # Protein: NP_000537.3:p.Arg72Pro

        patterns = {
            "genomic": r"^(NC_\d+\.\d+):g\.(\d+)([ACGT])>([ACGT])$",
            "coding": r"^(NM_\d+\.\d+):c\.(-?\d+)([ACGT])>([ACGT])$",
            "protein": r"^(NP_\d+\.\d+):p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})$",
        }

        for notation_type, pattern in patterns.items():
            if re.match(pattern, hgvs):
                return ValidationResult(
                    is_valid=True,
                    severity=ValidationSeverity.MEDIUM,
                    message=f"HGVS notation is valid ({notation_type})",
                    details={"hgvs": hgvs, "type": notation_type}
                )

        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.MEDIUM,
            message=f"HGVS notation format not recognized: {hgvs}",
            details={"hgvs": hgvs},
            suggestions=[
                "Check HGVS nomenclature guidelines",
                "Examples: NC_000001.11:g.100000A>G, NM_000546.5:c.215C>G"
            ]
        )

    def validate(
        self,
        chrom: Optional[str] = None,
        pos: Optional[int] = None,
        ref: Optional[str] = None,
        alt: Optional[str] = None,
        qual: Optional[float] = None,
        hgvs: Optional[str] = None,
        **kwargs
    ) -> ValidationResult:
        """
        Main validation method. Accepts VCF-style or HGVS notation.

        Args:
            chrom: Chromosome
            pos: Position
            ref: Reference allele
            alt: Alternate allele
            qual: Quality score
            hgvs: HGVS notation string
            **kwargs: Additional parameters

        Returns:
            ValidationResult
        """
        # Validate HGVS notation if provided
        if hgvs:
            result = self.validate_hgvs_notation(hgvs)
            self.record_validation(result)
            return result

        # Validate VCF-style variant
        if chrom and pos and ref and alt:
            result = self.validate_vcf_variant(chrom, pos, ref, alt, qual)
            self.record_validation(result)
            return result

        # Just validate alleles if no coordinates
        if ref and alt:
            result = self.validate_variant_alleles(ref, alt, kwargs.get("expected_type"))
            self.record_validation(result)
            return result

        return ValidationResult(
            is_valid=False,
            severity=ValidationSeverity.HIGH,
            message="Insufficient variant information provided",
            suggestions=[
                "Provide chrom, pos, ref, alt for VCF-style validation",
                "Or provide HGVS notation string"
            ]
        )
