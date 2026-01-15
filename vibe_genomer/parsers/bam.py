"""
BAM (Binary Alignment Map) parser.

Parses BAM/SAM files using pysam with biological awareness.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass

from .base import GenomicFileParser


@dataclass
class BAMHeader:
    """BAM file header information."""

    version: str
    sort_order: Optional[str]
    references: List[Dict[str, Any]]
    read_groups: List[Dict[str, Any]]
    programs: List[Dict[str, Any]]


@dataclass
class BAMAlignment:
    """Represents a single alignment from BAM."""

    query_name: str
    reference_name: str
    reference_start: int
    reference_end: int
    mapping_quality: int
    is_paired: bool
    is_proper_pair: bool
    is_unmapped: bool
    is_reverse: bool
    cigar: Optional[str]
    sequence: str
    qualities: Optional[List[int]]
    tags: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert alignment to dictionary."""
        return {
            "query_name": self.query_name,
            "reference_name": self.reference_name,
            "reference_start": self.reference_start,
            "reference_end": self.reference_end,
            "mapping_quality": self.mapping_quality,
            "is_paired": self.is_paired,
            "is_proper_pair": self.is_proper_pair,
            "is_unmapped": self.is_unmapped,
            "is_reverse": self.is_reverse,
            "cigar": self.cigar,
            "sequence": self.sequence,
            "tags": self.tags,
        }


class BAMParser(GenomicFileParser):
    """
    Parse BAM/SAM files with biological awareness.

    Features:
    - Streaming parser (doesn't load full file)
    - Understands alignment properties
    - Can extract specific regions
    - Works with both BAM and SAM formats

    Requires pysam to be installed.
    """

    def __init__(self):
        super().__init__()
        self._check_pysam()

    def _check_pysam(self):
        """Check if pysam is available."""
        try:
            import pysam

            self.pysam = pysam
        except ImportError:
            raise ImportError(
                "pysam is required for BAM parsing. Install with: pip install pysam"
            )

    def parse(self, file_path: Path) -> BAMHeader:
        """
        Parse BAM file and return header information.

        Args:
            file_path: Path to BAM/SAM file

        Returns:
            BAM header information
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"BAM file not found: {file_path}")

        # Open BAM file
        with self.pysam.AlignmentFile(str(file_path), "rb") as bam:
            header = self._parse_header(bam)

        return header

    def parse_alignments(
        self,
        file_path: Path,
        region: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Iterator[BAMAlignment]:
        """
        Stream alignments from BAM file.

        Args:
            file_path: Path to BAM file
            region: Optional region to extract (e.g., "chr1:1000-2000")
            limit: Optional limit on number of alignments

        Yields:
            BAMAlignment objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"BAM file not found: {file_path}")

        count = 0
        with self.pysam.AlignmentFile(str(file_path), "rb") as bam:
            # Fetch alignments
            if region:
                alignments = bam.fetch(region=region)
            else:
                alignments = bam.fetch(until_eof=True)

            for read in alignments:
                alignment = self._parse_alignment(read)
                yield alignment

                count += 1
                if limit and count >= limit:
                    break

    def _parse_header(self, bam) -> BAMHeader:
        """Parse BAM header."""
        header_dict = bam.header.to_dict()

        version = header_dict.get("HD", {}).get("VN", "unknown")
        sort_order = header_dict.get("HD", {}).get("SO")

        # Parse reference sequences
        references = []
        for ref in header_dict.get("SQ", []):
            references.append(
                {
                    "name": ref.get("SN"),
                    "length": ref.get("LN"),
                    "species": ref.get("SP"),
                    "assembly": ref.get("AS"),
                }
            )

        # Parse read groups
        read_groups = header_dict.get("RG", [])

        # Parse programs
        programs = header_dict.get("PG", [])

        return BAMHeader(
            version=version,
            sort_order=sort_order,
            references=references,
            read_groups=read_groups,
            programs=programs,
        )

    def _parse_alignment(self, read) -> BAMAlignment:
        """Parse a single alignment."""
        # Get CIGAR string
        cigar = None
        if read.cigarstring:
            cigar = read.cigarstring

        # Get tags as dictionary
        tags = dict(read.get_tags())

        return BAMAlignment(
            query_name=read.query_name,
            reference_name=read.reference_name if not read.is_unmapped else "*",
            reference_start=read.reference_start if not read.is_unmapped else -1,
            reference_end=read.reference_end if not read.is_unmapped else -1,
            mapping_quality=read.mapping_quality,
            is_paired=read.is_paired,
            is_proper_pair=read.is_proper_pair,
            is_unmapped=read.is_unmapped,
            is_reverse=read.is_reverse,
            cigar=cigar,
            sequence=read.query_sequence if read.query_sequence else "",
            qualities=read.query_qualities.tolist()
            if read.query_qualities is not None
            else None,
            tags=tags,
        )

    def get_summary(self, file_path: Path, sample_size: int = 10000) -> Dict[str, Any]:
        """
        Get summary statistics about BAM file.

        Args:
            file_path: Path to BAM file
            sample_size: Number of reads to sample for statistics

        Returns:
            Summary dictionary with read counts, mapping stats, etc.
        """
        header = self.parse(file_path)

        # Sample alignments for statistics
        total_sampled = 0
        mapped_count = 0
        paired_count = 0
        proper_pair_count = 0
        reverse_count = 0
        total_mapq = 0

        for alignment in self.parse_alignments(file_path, limit=sample_size):
            total_sampled += 1
            if not alignment.is_unmapped:
                mapped_count += 1
                total_mapq += alignment.mapping_quality
            if alignment.is_paired:
                paired_count += 1
            if alignment.is_proper_pair:
                proper_pair_count += 1
            if alignment.is_reverse:
                reverse_count += 1

        # Calculate statistics
        mapping_rate = (
            (mapped_count / total_sampled * 100) if total_sampled > 0 else 0
        )
        avg_mapq = (total_mapq / mapped_count) if mapped_count > 0 else 0
        paired_rate = (paired_count / total_sampled * 100) if total_sampled > 0 else 0

        return {
            "version": header.version,
            "sort_order": header.sort_order,
            "num_references": len(header.references),
            "references": [ref["name"] for ref in header.references],
            "num_read_groups": len(header.read_groups),
            "sample_size": total_sampled,
            "mapped_reads": mapped_count,
            "mapping_rate_percent": round(mapping_rate, 2),
            "paired_reads": paired_count,
            "paired_rate_percent": round(paired_rate, 2),
            "proper_pairs": proper_pair_count,
            "average_mapping_quality": round(avg_mapq, 2),
        }

    def get_coverage(
        self, file_path: Path, region: str, bin_size: int = 100
    ) -> List[int]:
        """
        Get coverage depth for a region.

        Args:
            file_path: Path to BAM file
            region: Region string (e.g., "chr1:1000-2000")
            bin_size: Size of bins for coverage calculation

        Returns:
            List of coverage values
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"BAM file not found: {file_path}")

        with self.pysam.AlignmentFile(str(file_path), "rb") as bam:
            # Parse region
            if ":" in region:
                chrom, coords = region.split(":")
                start, end = map(int, coords.split("-"))
            else:
                raise ValueError("Region must be in format 'chr:start-end'")

            # Get coverage
            coverage = []
            for pos in range(start, end, bin_size):
                count = bam.count(chrom, pos, min(pos + bin_size, end))
                coverage.append(count)

            return coverage
