"""
FASTQ parser for sequencing reads.

Parses FASTQ files with quality score handling.
"""

from pathlib import Path
from typing import Iterator, Optional, Dict, Any
from dataclasses import dataclass
import gzip

from .base import GenomicFileParser


@dataclass
class FASTQRead:
    """Represents a single read from FASTQ."""

    identifier: str
    sequence: str
    quality: str
    description: Optional[str] = None

    def __post_init__(self):
        """Validate read data."""
        if len(self.sequence) != len(self.quality):
            raise ValueError(
                f"Sequence and quality lengths don't match: "
                f"{len(self.sequence)} vs {len(self.quality)}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert read to dictionary."""
        return {
            "identifier": self.identifier,
            "sequence": self.sequence,
            "quality": self.quality,
            "description": self.description,
            "length": len(self.sequence),
            "avg_quality": self.average_quality(),
        }

    def average_quality(self) -> float:
        """Calculate average Phred quality score."""
        # Convert ASCII to Phred+33
        scores = [ord(q) - 33 for q in self.quality]
        return sum(scores) / len(scores) if scores else 0.0

    def gc_content(self) -> float:
        """Calculate GC content percentage."""
        seq_upper = self.sequence.upper()
        gc_count = seq_upper.count("G") + seq_upper.count("C")
        return (gc_count / len(self.sequence) * 100) if self.sequence else 0.0


class FASTQParser(GenomicFileParser):
    """
    Parse FASTQ files.

    Features:
    - Streaming parser (doesn't load full file)
    - Handles gzipped files
    - Calculates quality metrics
    - Validates read structure
    """

    def __init__(self):
        super().__init__()

    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse FASTQ file and return basic information.

        Args:
            file_path: Path to FASTQ file

        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"FASTQ file not found: {file_path}")

        # Sample first few reads for metadata
        reads_sample = []
        for i, read in enumerate(self.parse_reads(file_path, limit=100)):
            reads_sample.append(read)

        if not reads_sample:
            return {
                "format": "FASTQ",
                "is_empty": True,
            }

        # Analyze sample
        avg_length = sum(len(r.sequence) for r in reads_sample) / len(reads_sample)
        avg_quality = sum(r.average_quality() for r in reads_sample) / len(
            reads_sample
        )
        avg_gc = sum(r.gc_content() for r in reads_sample) / len(reads_sample)

        return {
            "format": "FASTQ",
            "is_empty": False,
            "sample_size": len(reads_sample),
            "average_read_length": round(avg_length, 2),
            "average_quality_score": round(avg_quality, 2),
            "average_gc_content": round(avg_gc, 2),
        }

    def parse_reads(
        self, file_path: Path, limit: Optional[int] = None
    ) -> Iterator[FASTQRead]:
        """
        Stream reads from FASTQ file.

        Args:
            file_path: Path to FASTQ file
            limit: Optional limit on number of reads

        Yields:
            FASTQRead objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"FASTQ file not found: {file_path}")

        count = 0
        with self._open_file(file_path) as f:
            while True:
                # Read 4 lines for each FASTQ entry
                line1 = f.readline()
                if not line1:
                    break

                line2 = f.readline()
                line3 = f.readline()
                line4 = f.readline()

                if not all([line1, line2, line3, line4]):
                    break

                # Parse read
                read = self._parse_read(line1, line2, line3, line4)
                yield read

                count += 1
                if limit and count >= limit:
                    break

    def _open_file(self, file_path: Path):
        """Open file, handling gzipped files."""
        if file_path.suffix == ".gz":
            return gzip.open(file_path, "rt")
        return open(file_path, "r")

    def _parse_read(
        self, line1: str, line2: str, line3: str, line4: str
    ) -> FASTQRead:
        """Parse a single FASTQ read (4 lines)."""
        # Line 1: @identifier description
        if not line1.startswith("@"):
            raise ValueError(f"Invalid FASTQ format: expected '@', got {line1[:10]}")

        header = line1[1:].strip()
        parts = header.split(None, 1)
        identifier = parts[0]
        description = parts[1] if len(parts) > 1 else None

        # Line 2: sequence
        sequence = line2.strip()

        # Line 3: + (optionally identifier again)
        if not line3.startswith("+"):
            raise ValueError(f"Invalid FASTQ format: expected '+', got {line3[:10]}")

        # Line 4: quality scores
        quality = line4.strip()

        return FASTQRead(
            identifier=identifier,
            sequence=sequence,
            quality=quality,
            description=description,
        )

    def get_summary(
        self, file_path: Path, sample_size: int = 10000
    ) -> Dict[str, Any]:
        """
        Get comprehensive summary statistics about FASTQ file.

        Args:
            file_path: Path to FASTQ file
            sample_size: Number of reads to sample

        Returns:
            Summary dictionary with read counts, quality stats, etc.
        """
        total_reads = 0
        total_bases = 0
        total_quality = 0
        total_gc = 0
        length_counts: Dict[int, int] = {}

        min_length = float("inf")
        max_length = 0

        for read in self.parse_reads(file_path, limit=sample_size):
            total_reads += 1
            read_length = len(read.sequence)
            total_bases += read_length
            total_quality += read.average_quality()
            total_gc += read.gc_content()

            # Track length distribution
            length_counts[read_length] = length_counts.get(read_length, 0) + 1

            # Track min/max
            if read_length < min_length:
                min_length = read_length
            if read_length > max_length:
                max_length = read_length

        if total_reads == 0:
            return {
                "format": "FASTQ",
                "is_empty": True,
            }

        # Calculate statistics
        avg_length = total_bases / total_reads
        avg_quality = total_quality / total_reads
        avg_gc = total_gc / total_reads

        return {
            "format": "FASTQ",
            "total_reads_sampled": total_reads,
            "total_bases": total_bases,
            "average_read_length": round(avg_length, 2),
            "min_read_length": min_length,
            "max_read_length": max_length,
            "average_quality_score": round(avg_quality, 2),
            "average_gc_content_percent": round(avg_gc, 2),
            "length_distribution": dict(sorted(length_counts.items())),
        }

    def filter_by_quality(
        self,
        file_path: Path,
        min_quality: float,
        output_path: Optional[Path] = None,
    ) -> Iterator[FASTQRead]:
        """
        Filter reads by minimum average quality score.

        Args:
            file_path: Path to input FASTQ file
            min_quality: Minimum average quality score
            output_path: Optional path to write filtered reads

        Yields:
            Filtered FASTQRead objects
        """
        output_handle = None
        if output_path:
            output_handle = open(output_path, "w")

        try:
            for read in self.parse_reads(file_path):
                if read.average_quality() >= min_quality:
                    if output_handle:
                        output_handle.write(f"@{read.identifier}")
                        if read.description:
                            output_handle.write(f" {read.description}")
                        output_handle.write(f"\n{read.sequence}\n")
                        output_handle.write(f"+\n{read.quality}\n")
                    yield read
        finally:
            if output_handle:
                output_handle.close()
