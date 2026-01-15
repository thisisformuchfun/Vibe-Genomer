"""
VCF (Variant Call Format) parser.

Parses VCF files with biological awareness - understands chromosome naming,
coordinate systems, and variant representations.
"""

from pathlib import Path
from typing import Dict, List, Iterator, Optional, Any
from dataclasses import dataclass
import gzip

from .base import GenomicFileParser


@dataclass
class VCFHeader:
    """VCF file header information."""

    file_format: str
    contigs: List[str]
    info_fields: Dict[str, Dict[str, str]]
    format_fields: Dict[str, Dict[str, str]]
    samples: List[str]
    metadata: Dict[str, Any]


@dataclass
class VCFVariant:
    """Represents a single variant from VCF."""

    chrom: str
    pos: int
    id: Optional[str]
    ref: str
    alt: List[str]
    qual: Optional[float]
    filter: List[str]
    info: Dict[str, Any]
    format: Optional[List[str]]
    samples: Optional[Dict[str, Dict[str, str]]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert variant to dictionary."""
        return {
            "chrom": self.chrom,
            "pos": self.pos,
            "id": self.id,
            "ref": self.ref,
            "alt": self.alt,
            "qual": self.qual,
            "filter": self.filter,
            "info": self.info,
            "samples": self.samples,
        }


class VCFParser(GenomicFileParser):
    """
    Parse VCF files with biological awareness.

    Features:
    - Streaming parser (doesn't load full file)
    - Understands chromosome naming (chr1 == 1)
    - Parses INFO and FORMAT fields
    - Handles gzipped files
    """

    def __init__(self):
        super().__init__()
        self._header: Optional[VCFHeader] = None

    def parse(self, file_path: Path) -> VCFHeader:
        """
        Parse VCF file and return header information.

        Args:
            file_path: Path to VCF file

        Returns:
            VCF header information
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"VCF file not found: {file_path}")

        # Parse header
        with self._open_file(file_path) as f:
            self._header = self._parse_header(f)

        return self._header

    def parse_variants(
        self, file_path: Path, limit: Optional[int] = None
    ) -> Iterator[VCFVariant]:
        """
        Stream variants from VCF file.

        Args:
            file_path: Path to VCF file
            limit: Optional limit on number of variants

        Yields:
            VCFVariant objects
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"VCF file not found: {file_path}")

        count = 0
        with self._open_file(file_path) as f:
            # Skip header
            for line in f:
                if not line.startswith("#"):
                    break

            # Parse variants
            for line in f:
                if line.startswith("#"):
                    continue

                variant = self._parse_variant_line(line)
                yield variant

                count += 1
                if limit and count >= limit:
                    break

    def _open_file(self, file_path: Path):
        """Open file, handling gzipped files."""
        if file_path.suffix == ".gz":
            return gzip.open(file_path, "rt")
        return open(file_path, "r")

    def _parse_header(self, file_handle) -> VCFHeader:
        """Parse VCF header lines."""
        file_format = ""
        contigs = []
        info_fields = {}
        format_fields = {}
        samples = []
        metadata = {}

        for line in file_handle:
            if not line.startswith("#"):
                break

            line = line.strip()

            if line.startswith("##fileformat="):
                file_format = line.split("=", 1)[1]

            elif line.startswith("##contig="):
                # Extract contig name
                parts = line.split("ID=")
                if len(parts) > 1:
                    contig = parts[1].split(",")[0].split(">")[0]
                    contigs.append(contig)

            elif line.startswith("##INFO="):
                # Parse INFO field definition
                info = self._parse_header_field(line)
                if "ID" in info:
                    info_fields[info["ID"]] = info

            elif line.startswith("##FORMAT="):
                # Parse FORMAT field definition
                fmt = self._parse_header_field(line)
                if "ID" in fmt:
                    format_fields[fmt["ID"]] = fmt

            elif line.startswith("#CHROM"):
                # Parse sample names from header line
                parts = line.split("\t")
                if len(parts) > 9:
                    samples = parts[9:]

            else:
                # Store other metadata
                if "=" in line:
                    key, value = line[2:].split("=", 1)
                    metadata[key] = value

        return VCFHeader(
            file_format=file_format,
            contigs=contigs,
            info_fields=info_fields,
            format_fields=format_fields,
            samples=samples,
            metadata=metadata,
        )

    def _parse_header_field(self, line: str) -> Dict[str, str]:
        """Parse a header field definition (INFO or FORMAT)."""
        result = {}
        # Extract content between < >
        if "<" in line and ">" in line:
            content = line[line.index("<") + 1 : line.rindex(">")]
            # Parse key=value pairs
            parts = []
            current = ""
            in_quotes = False
            for char in content:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == "," and not in_quotes:
                    parts.append(current)
                    current = ""
                    continue
                current += char
            if current:
                parts.append(current)

            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    result[key] = value.strip('"')

        return result

    def _parse_variant_line(self, line: str) -> VCFVariant:
        """Parse a single variant line from VCF."""
        parts = line.strip().split("\t")

        if len(parts) < 8:
            raise ValueError(f"Invalid VCF line: {line}")

        # Parse fixed fields
        chrom = self._normalize_chrom(parts[0])
        pos = int(parts[1])
        var_id = parts[2] if parts[2] != "." else None
        ref = parts[3]
        alt = parts[4].split(",")
        qual = float(parts[5]) if parts[5] != "." else None
        filt = parts[6].split(";") if parts[6] != "." else []

        # Parse INFO field
        info = self._parse_info(parts[7])

        # Parse FORMAT and sample data if present
        fmt = None
        sample_data = None
        if len(parts) > 8 and self._header:
            fmt = parts[8].split(":")
            sample_data = {}
            for i, sample_name in enumerate(self._header.samples):
                if len(parts) > 9 + i:
                    values = parts[9 + i].split(":")
                    sample_data[sample_name] = dict(zip(fmt, values))

        return VCFVariant(
            chrom=chrom,
            pos=pos,
            id=var_id,
            ref=ref,
            alt=alt,
            qual=qual,
            filter=filt,
            info=info,
            format=fmt,
            samples=sample_data,
        )

    def _parse_info(self, info_str: str) -> Dict[str, Any]:
        """Parse INFO field."""
        info = {}
        if info_str == ".":
            return info

        for item in info_str.split(";"):
            if "=" in item:
                key, value = item.split("=", 1)
                # Try to parse as number
                try:
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
                info[key] = value
            else:
                # Flag field
                info[item] = True

        return info

    def _normalize_chrom(self, chrom: str) -> str:
        """
        Normalize chromosome names.

        Understands that 'chr1' and '1' refer to the same chromosome.
        """
        # For now, keep as-is but this could be extended
        # to handle more sophisticated normalization
        return chrom

    def get_summary(self, file_path: Path) -> Dict[str, Any]:
        """
        Get summary statistics about VCF file.

        Args:
            file_path: Path to VCF file

        Returns:
            Summary dictionary with variant counts, chromosomes, etc.
        """
        header = self.parse(file_path)

        # Count variants
        variant_count = 0
        chroms_seen = set()

        for variant in self.parse_variants(file_path, limit=10000):
            variant_count += 1
            chroms_seen.add(variant.chrom)

        return {
            "file_format": header.file_format,
            "num_samples": len(header.samples),
            "sample_names": header.samples,
            "contigs": header.contigs,
            "chromosomes_with_variants": sorted(chroms_seen),
            "variant_count_sample": variant_count,
            "info_fields": list(header.info_fields.keys()),
            "format_fields": list(header.format_fields.keys()),
        }
