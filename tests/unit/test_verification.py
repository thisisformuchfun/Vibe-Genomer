"""
Unit tests for verification module.
"""

import pytest
from vibe_genomer.verification import (
    CoordinateValidator,
    VariantValidator,
    ConstraintValidator,
    ValidationSeverity,
    CompositeValidator,
)
from vibe_genomer.utils.exceptions import CoordinateValidationError


class TestCoordinateValidator:
    """Test the CoordinateValidator class."""

    def test_validator_creation(self):
        """Test creating a CoordinateValidator."""
        validator = CoordinateValidator(genome_build="hg38")
        assert validator.genome_build == "hg38"
        assert validator.strict_mode is True

    def test_valid_chromosome(self):
        """Test valid chromosome names."""
        validator = CoordinateValidator(genome_build="hg38")

        # Test with 'chr' prefix
        result = validator.validate_chromosome("chr1")
        assert result.is_valid is True

        # Test without 'chr' prefix
        result = validator.validate_chromosome("1")
        assert result.is_valid is True

        # Test X chromosome
        result = validator.validate_chromosome("chrX")
        assert result.is_valid is True

    def test_invalid_chromosome(self):
        """Test invalid chromosome names."""
        validator = CoordinateValidator(genome_build="hg38")

        result = validator.validate_chromosome("chr99")
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.CRITICAL

    def test_valid_position(self):
        """Test valid genomic positions."""
        validator = CoordinateValidator(genome_build="hg38")

        result = validator.validate_position("chr1", 1000000)
        assert result.is_valid is True

    def test_position_exceeds_chromosome_length(self):
        """Test position exceeding chromosome length."""
        validator = CoordinateValidator(genome_build="hg38")

        # chr1 length is ~248M bp
        result = validator.validate_position("chr1", 999999999)
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.CRITICAL

    def test_negative_position(self):
        """Test negative positions are invalid."""
        validator = CoordinateValidator(genome_build="hg38")

        result = validator.validate_position("chr1", -100)
        assert result.is_valid is False

    def test_valid_interval(self):
        """Test valid genomic intervals."""
        validator = CoordinateValidator(genome_build="hg38")

        result = validator.validate_interval("chr1", 1000000, 2000000)
        assert result.is_valid is True
        assert result.details["length"] == 1000001  # Inclusive

    def test_interval_start_greater_than_end(self):
        """Test interval where start > end."""
        validator = CoordinateValidator(genome_build="hg38")

        result = validator.validate_interval("chr1", 2000000, 1000000)
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.CRITICAL

    def test_parse_region_string(self):
        """Test parsing region strings."""
        validator = CoordinateValidator(genome_build="hg38")

        # Test interval
        chrom, start, end = validator.parse_region_string("chr1:1000-2000")
        assert chrom == "chr1"
        assert start == 1000
        assert end == 2000

        # Test single position
        chrom, start, end = validator.parse_region_string("chr1:1000")
        assert chrom == "chr1"
        assert start == 1000
        assert end is None

    def test_parse_invalid_region_string(self):
        """Test parsing invalid region strings."""
        validator = CoordinateValidator(genome_build="hg38")

        with pytest.raises(CoordinateValidationError):
            validator.parse_region_string("invalid_format")

    def test_validate_with_region_string(self):
        """Test validation using region string."""
        validator = CoordinateValidator(genome_build="hg38")

        result = validator.validate(region="chr1:1000000-2000000")
        assert result.is_valid is True

    def test_hg19_genome_build(self):
        """Test using hg19 genome build."""
        validator = CoordinateValidator(genome_build="hg19")

        result = validator.validate_position("chr1", 1000000)
        assert result.is_valid is True
        assert validator.genome_build == "hg19"

    def test_validation_history(self):
        """Test validation history tracking."""
        validator = CoordinateValidator(genome_build="hg38")

        validator.validate(region="chr1:1000")
        validator.validate(region="chr99:1000")  # Invalid

        history = validator.get_validation_history()
        assert len(history) == 2

        failed = validator.get_failed_validations()
        assert len(failed) == 1


class TestVariantValidator:
    """Test the VariantValidator class."""

    def test_validator_creation(self):
        """Test creating a VariantValidator."""
        validator = VariantValidator(genome_build="hg38")
        assert validator.coordinate_validator.genome_build == "hg38"

    def test_valid_dna_sequence(self):
        """Test valid DNA sequences."""
        validator = VariantValidator()

        result = validator.validate_dna_sequence("ACGT")
        assert result.is_valid is True

        result = validator.validate_dna_sequence("acgt")  # Lowercase
        assert result.is_valid is True

    def test_invalid_dna_sequence(self):
        """Test invalid DNA sequences."""
        validator = VariantValidator()

        result = validator.validate_dna_sequence("ACGTX")  # Invalid base
        assert result.is_valid is False
        assert result.severity == ValidationSeverity.HIGH

    def test_empty_sequence(self):
        """Test empty sequences are invalid."""
        validator = VariantValidator()

        result = validator.validate_dna_sequence("")
        assert result.is_valid is False

    def test_iupac_codes(self):
        """Test IUPAC ambiguity codes."""
        validator = VariantValidator(allow_iupac=False)

        result = validator.validate_dna_sequence("ACGTR")  # R is IUPAC
        assert result.is_valid is False

        # Now allow IUPAC
        validator = VariantValidator(allow_iupac=True)
        result = validator.validate_dna_sequence("ACGTR")
        assert result.is_valid is True

    def test_classify_variant_type(self):
        """Test variant type classification."""
        validator = VariantValidator()

        # SNV
        assert validator.classify_variant_type("A", "G") == "SNV"

        # Insertion
        assert validator.classify_variant_type("A", "ATG") == "insertion"

        # Deletion
        assert validator.classify_variant_type("ATG", "A") == "deletion"

        # MNV
        assert validator.classify_variant_type("AT", "GC") == "MNV"

    def test_validate_variant_alleles(self):
        """Test validating REF and ALT alleles."""
        validator = VariantValidator()

        # Valid SNV
        result = validator.validate_variant_alleles("A", "G")
        assert result.is_valid is True
        assert result.details["variant_type"] == "SNV"

        # Valid insertion
        result = validator.validate_variant_alleles("A", "ATG")
        assert result.is_valid is True
        assert result.details["variant_type"] == "insertion"

    def test_validate_variant_alleles_invalid(self):
        """Test invalid variant alleles."""
        validator = VariantValidator()

        # Invalid REF
        result = validator.validate_variant_alleles("X", "G")
        assert result.is_valid is False

        # Invalid ALT
        result = validator.validate_variant_alleles("A", "X")
        assert result.is_valid is False

    def test_validate_vcf_variant(self):
        """Test validating complete VCF variants."""
        validator = VariantValidator(genome_build="hg38")

        result = validator.validate_vcf_variant(
            chrom="chr1",
            pos=1000000,
            ref="A",
            alt="G",
            qual=100.0
        )
        assert result.is_valid is True

    def test_validate_vcf_variant_invalid_coordinates(self):
        """Test VCF variant with invalid coordinates."""
        validator = VariantValidator(genome_build="hg38")

        result = validator.validate_vcf_variant(
            chrom="chr99",  # Invalid chromosome
            pos=1000000,
            ref="A",
            alt="G"
        )
        assert result.is_valid is False

    def test_validate_hgvs_notation(self):
        """Test HGVS notation validation."""
        validator = VariantValidator()

        # Valid genomic HGVS
        result = validator.validate_hgvs_notation("NC_000001.11:g.100000A>G")
        assert result.is_valid is True

        # Valid coding HGVS
        result = validator.validate_hgvs_notation("NM_000546.5:c.215C>G")
        assert result.is_valid is True

        # Invalid HGVS
        result = validator.validate_hgvs_notation("invalid_hgvs")
        assert result.is_valid is False


class TestConstraintValidator:
    """Test the ConstraintValidator class."""

    def test_validator_creation(self):
        """Test creating a ConstraintValidator."""
        validator = ConstraintValidator()
        assert validator.strict_mode is True

    def test_valid_gc_content(self):
        """Test valid GC content."""
        validator = ConstraintValidator()

        result = validator.validate_gc_content(0.42)
        assert result.is_valid is True

        result = validator.validate_gc_content(0.0)
        assert result.is_valid is True

        result = validator.validate_gc_content(1.0)
        assert result.is_valid is True

    def test_invalid_gc_content(self):
        """Test invalid GC content."""
        validator = ConstraintValidator()

        # Negative
        result = validator.validate_gc_content(-0.1)
        assert result.is_valid is False

        # Percentage (42% instead of 0.42)
        result = validator.validate_gc_content(42.0)
        assert result.is_valid is False
        assert "percentage" in result.message.lower()

    def test_valid_phred_score(self):
        """Test valid PHRED scores."""
        validator = ConstraintValidator()

        result = validator.validate_phred_score(30)
        assert result.is_valid is True

        result = validator.validate_phred_score(0)
        assert result.is_valid is True

    def test_invalid_phred_score(self):
        """Test invalid PHRED scores."""
        validator = ConstraintValidator()

        # Negative
        result = validator.validate_phred_score(-5)
        assert result.is_valid is False

        # Too high (without allowing it)
        result = validator.validate_phred_score(100)
        assert result.is_valid is False

        # Allow high scores
        result = validator.validate_phred_score(100, allow_high=True)
        assert result.is_valid is True

    def test_valid_coverage(self):
        """Test valid coverage values."""
        validator = ConstraintValidator()

        result = validator.validate_coverage(30.5)
        assert result.is_valid is True

        result = validator.validate_coverage(0)
        assert result.is_valid is True

    def test_invalid_coverage(self):
        """Test invalid coverage values."""
        validator = ConstraintValidator()

        result = validator.validate_coverage(-10)
        assert result.is_valid is False

    def test_high_coverage_warning(self):
        """Test warning for very high coverage."""
        validator = ConstraintValidator()

        result = validator.validate_coverage(15000)
        assert result.is_valid is True  # Still valid but warns
        assert result.severity == ValidationSeverity.LOW

    def test_valid_mapping_quality(self):
        """Test valid mapping quality."""
        validator = ConstraintValidator()

        result = validator.validate_mapping_quality(60)
        assert result.is_valid is True

        result = validator.validate_mapping_quality(0)
        assert result.is_valid is True

    def test_invalid_mapping_quality(self):
        """Test invalid mapping quality."""
        validator = ConstraintValidator()

        result = validator.validate_mapping_quality(-1)
        assert result.is_valid is False

        result = validator.validate_mapping_quality(256)
        assert result.is_valid is False

    def test_vcf_quality(self):
        """Test VCF quality scores."""
        validator = ConstraintValidator()

        result = validator.validate_vcf_quality(100.5)
        assert result.is_valid is True

        result = validator.validate_vcf_quality(-1)
        assert result.is_valid is False

    def test_allele_frequency(self):
        """Test allele frequency validation."""
        validator = ConstraintValidator()

        result = validator.validate_allele_frequency(0.42)
        assert result.is_valid is True

        # Percentage format
        result = validator.validate_allele_frequency(42.0)
        assert result.is_valid is False

    def test_read_length(self):
        """Test read length validation."""
        validator = ConstraintValidator()

        result = validator.validate_read_length(150)
        assert result.is_valid is True

        result = validator.validate_read_length(0)
        assert result.is_valid is False

        # Warn for unusual lengths
        result = validator.validate_read_length(10)
        assert result.is_valid is True
        assert result.severity == ValidationSeverity.LOW

    def test_insert_size(self):
        """Test insert size validation."""
        validator = ConstraintValidator()

        result = validator.validate_insert_size(400)
        assert result.is_valid is True

        result = validator.validate_insert_size(-100)
        assert result.is_valid is False

    def test_validate_dispatcher(self):
        """Test the main validate method dispatcher."""
        validator = ConstraintValidator()

        # Test GC content
        result = validator.validate("gc_content", 0.42)
        assert result.is_valid is True

        # Test PHRED score
        result = validator.validate("phred_score", 30)
        assert result.is_valid is True

        # Test unknown constraint type
        result = validator.validate("unknown_type", 100)
        assert result.is_valid is False


class TestCompositeValidator:
    """Test the CompositeValidator class."""

    def test_composite_validator_all_pass(self):
        """Test composite validator when all checks pass."""
        coord_validator = CoordinateValidator(genome_build="hg38")
        constraint_validator = ConstraintValidator()

        composite = CompositeValidator(
            validators=[coord_validator, constraint_validator]
        )

        # This will validate coordinates
        result = coord_validator.validate(region="chr1:1000")
        assert result.is_valid is True

    def test_composite_validator_some_fail(self):
        """Test composite validator when some checks fail."""
        coord_validator = CoordinateValidator(genome_build="hg38")

        composite = CompositeValidator(validators=[coord_validator])

        # Validate invalid coordinates
        result = composite.validate(region="chr99:1000")
        assert result.is_valid is False
