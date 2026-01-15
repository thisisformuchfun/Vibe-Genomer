"""
Genomic coordinate validation.

Ensures genomic coordinates make biological sense:
- Chromosome exists in the reference genome
- Position is within chromosome bounds
- Start < End for intervals
- Coordinates match the specified build (hg19/hg38/etc)
"""

from typing import Optional, Dict, Any, Tuple
import re

from .base import BiologicalValidator, ValidationResult, ValidationSeverity
from ..utils.exceptions import CoordinateValidationError


# Reference genome chromosome lengths (bp)
# Data from UCSC Genome Browser
REFERENCE_GENOMES = {
    "hg38": {
        "chr1": 248956422, "chr2": 242193529, "chr3": 198295559,
        "chr4": 190214555, "chr5": 181538259, "chr6": 170805979,
        "chr7": 159345973, "chr8": 145138636, "chr9": 138394717,
        "chr10": 133797422, "chr11": 135086622, "chr12": 133275309,
        "chr13": 114364328, "chr14": 107043718, "chr15": 101991189,
        "chr16": 90338345, "chr17": 83257441, "chr18": 80373285,
        "chr19": 58617616, "chr20": 64444167, "chr21": 46709983,
        "chr22": 50818468, "chrX": 156040895, "chrY": 57227415,
        "chrM": 16569,
        # Aliases without 'chr' prefix
        "1": 248956422, "2": 242193529, "3": 198295559,
        "4": 190214555, "5": 181538259, "6": 170805979,
        "7": 159345973, "8": 145138636, "9": 138394717,
        "10": 133797422, "11": 135086622, "12": 133275309,
        "13": 114364328, "14": 107043718, "15": 101991189,
        "16": 90338345, "17": 83257441, "18": 80373285,
        "19": 58617616, "20": 64444167, "21": 46709983,
        "22": 50818468, "X": 156040895, "Y": 57227415,
        "M": 16569, "MT": 16569,
    },
    "hg19": {
        "chr1": 249250621, "chr2": 243199373, "chr3": 198022430,
        "chr4": 191154276, "chr5": 180915260, "chr6": 171115067,
        "chr7": 159138663, "chr8": 146364022, "chr9": 141213431,
        "chr10": 135534747, "chr11": 135006516, "chr12": 133851895,
        "chr13": 115169878, "chr14": 107349540, "chr15": 102531392,
        "chr16": 90354753, "chr17": 81195210, "chr18": 78077248,
        "chr19": 59128983, "chr20": 63025520, "chr21": 48129895,
        "chr22": 51304566, "chrX": 155270560, "chrY": 59373566,
        "chrM": 16571,
        # Aliases
        "1": 249250621, "2": 243199373, "3": 198022430,
        "4": 191154276, "5": 180915260, "6": 171115067,
        "7": 159138663, "8": 146364022, "9": 141213431,
        "10": 135534747, "11": 135006516, "12": 133851895,
        "13": 115169878, "14": 107349540, "15": 102531392,
        "16": 90354753, "17": 81195210, "18": 78077248,
        "19": 59128983, "20": 63025520, "21": 48129895,
        "22": 51304566, "X": 155270560, "Y": 59373566,
        "M": 16571, "MT": 16571,
    },
    "grch38": "hg38",  # Alias
    "grch37": "hg19",  # Alias
}


class CoordinateValidator(BiologicalValidator):
    """
    Validates genomic coordinates against reference genome builds.

    Checks:
    1. Chromosome exists
    2. Positions are within bounds
    3. Start <= End for intervals
    4. Coordinates are positive
    """

    def __init__(self, genome_build: str = "hg38", strict_mode: bool = True):
        """
        Initialize the coordinate validator.

        Args:
            genome_build: Reference genome build (hg38, hg19, grch38, grch37)
            strict_mode: If True, fail on any validation error
        """
        super().__init__(strict_mode=strict_mode)

        # Resolve aliases
        if genome_build.lower() in REFERENCE_GENOMES:
            build = REFERENCE_GENOMES[genome_build.lower()]
            if isinstance(build, str):
                genome_build = build

        self.genome_build = genome_build.lower()

        if self.genome_build not in REFERENCE_GENOMES:
            raise ValueError(
                f"Unknown genome build: {genome_build}. "
                f"Supported builds: {', '.join(k for k in REFERENCE_GENOMES.keys() if isinstance(REFERENCE_GENOMES[k], dict))}"
            )

        self.chr_lengths = REFERENCE_GENOMES[self.genome_build]

    def normalize_chromosome(self, chrom: str) -> str:
        """
        Normalize chromosome name (e.g., '1' -> 'chr1', 'chr1' -> 'chr1').

        Args:
            chrom: Chromosome name

        Returns:
            Normalized chromosome name
        """
        chrom = str(chrom).strip()

        # If it starts with 'chr', return as-is
        if chrom.startswith("chr"):
            return chrom

        # Otherwise, add 'chr' prefix
        return f"chr{chrom}"

    def validate_chromosome(self, chrom: str) -> ValidationResult:
        """
        Validate that a chromosome exists in the reference genome.

        Args:
            chrom: Chromosome name

        Returns:
            ValidationResult
        """
        chrom_norm = self.normalize_chromosome(chrom)

        # Check if chromosome exists (try both formats)
        if chrom_norm in self.chr_lengths or chrom in self.chr_lengths:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.CRITICAL,
                message=f"Chromosome {chrom} exists in {self.genome_build}",
                details={"chromosome": chrom, "normalized": chrom_norm}
            )
        else:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Chromosome {chrom} does not exist in {self.genome_build}",
                details={"chromosome": chrom, "genome_build": self.genome_build},
                suggestions=[
                    f"Valid chromosomes: {', '.join(sorted(set(str(c).replace('chr', '') for c in self.chr_lengths.keys() if isinstance(c, str) and c.startswith('chr'))))}",
                    "Check chromosome naming convention (with/without 'chr' prefix)"
                ]
            )

    def validate_position(self, chrom: str, pos: int) -> ValidationResult:
        """
        Validate that a position is within chromosome bounds.

        Args:
            chrom: Chromosome name
            pos: Position (1-based)

        Returns:
            ValidationResult
        """
        # First validate chromosome exists
        chrom_result = self.validate_chromosome(chrom)
        if not chrom_result.is_valid:
            return chrom_result

        # Check position is positive
        if pos < 1:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Position must be >= 1, got {pos}",
                details={"chromosome": chrom, "position": pos},
                suggestions=["Genomic coordinates are 1-based"]
            )

        # Get chromosome length (try both naming conventions)
        chrom_norm = self.normalize_chromosome(chrom)
        chr_length = self.chr_lengths.get(chrom_norm) or self.chr_lengths.get(chrom)

        if pos > chr_length:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Position {pos} exceeds chromosome {chrom} length ({chr_length:,} bp)",
                details={
                    "chromosome": chrom,
                    "position": pos,
                    "chr_length": chr_length,
                    "genome_build": self.genome_build
                },
                suggestions=[
                    f"Valid range for {chrom}: 1-{chr_length:,}",
                    "Check if coordinates match the genome build"
                ]
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.CRITICAL,
            message=f"Position {chrom}:{pos} is valid",
            details={
                "chromosome": chrom,
                "position": pos,
                "chr_length": chr_length
            }
        )

    def validate_interval(self, chrom: str, start: int, end: int) -> ValidationResult:
        """
        Validate a genomic interval.

        Args:
            chrom: Chromosome name
            start: Start position (1-based, inclusive)
            end: End position (1-based, inclusive)

        Returns:
            ValidationResult
        """
        # Validate start position
        start_result = self.validate_position(chrom, start)
        if not start_result.is_valid:
            return start_result

        # Validate end position
        end_result = self.validate_position(chrom, end)
        if not end_result.is_valid:
            return end_result

        # Check start <= end
        if start > end:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Start position ({start}) must be <= end position ({end})",
                details={
                    "chromosome": chrom,
                    "start": start,
                    "end": end
                },
                suggestions=["Swap start and end positions"]
            )

        interval_length = end - start + 1
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.CRITICAL,
            message=f"Interval {chrom}:{start}-{end} is valid ({interval_length:,} bp)",
            details={
                "chromosome": chrom,
                "start": start,
                "end": end,
                "length": interval_length
            }
        )

    def parse_region_string(self, region: str) -> Tuple[str, int, Optional[int]]:
        """
        Parse a region string like 'chr1:1000-2000' or 'chr1:1000'.

        Args:
            region: Region string

        Returns:
            Tuple of (chromosome, start, end) where end is None for single positions

        Raises:
            CoordinateValidationError: If region format is invalid
        """
        # Match patterns like: chr1:1000-2000, chr1:1000, 1:1000-2000, etc.
        pattern = r'^(.+?):(\d+)(?:-(\d+))?$'
        match = re.match(pattern, region)

        if not match:
            raise CoordinateValidationError(
                f"Invalid region format: {region}",
                details={"expected_format": "chr:start-end or chr:pos"}
            )

        chrom = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3)) if match.group(3) else None

        return chrom, start, end

    def validate(self, region: Optional[str] = None,
                 chrom: Optional[str] = None,
                 start: Optional[int] = None,
                 end: Optional[int] = None) -> ValidationResult:
        """
        Main validation method. Accepts either a region string or separate coordinates.

        Args:
            region: Region string like 'chr1:1000-2000'
            chrom: Chromosome name
            start: Start position
            end: End position (optional, for intervals)

        Returns:
            ValidationResult
        """
        # Parse region string if provided
        if region:
            try:
                chrom, start, end = self.parse_region_string(region)
            except CoordinateValidationError as e:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=str(e),
                    details=e.details
                )

        # Validate based on what we have
        if chrom and start and end:
            result = self.validate_interval(chrom, start, end)
        elif chrom and start:
            result = self.validate_position(chrom, start)
        elif chrom:
            result = self.validate_chromosome(chrom)
        else:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message="No coordinates provided",
                suggestions=["Provide region string or chrom/start/end"]
            )

        self.record_validation(result)
        return result
