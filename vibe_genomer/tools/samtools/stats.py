"""
Samtools stats wrapper.

Computes statistics for BAM/SAM/CRAM files.
"""

from typing import Dict, Any, List
from pathlib import Path

from ..base import BioinformaticsTool, ToolResult
from ...utils import ToolError


class SamtoolsStats(BioinformaticsTool):
    """Wrapper for samtools stats command."""

    @property
    def binary_name(self) -> str:
        return "samtools"

    @property
    def description(self) -> str:
        return "Compute statistics for SAM/BAM/CRAM files"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate parameters."""
        if "input_file" not in params:
            raise ToolError("input_file parameter is required")

        input_file = Path(params["input_file"])
        if not input_file.exists():
            raise ToolError(f"Input file not found: {input_file}")

        return True

    def build_command(self, params: Dict[str, Any]) -> List[str]:
        """Build samtools stats command."""
        cmd = [self.binary_name, "stats"]

        # Coverage (histogram)
        if params.get("coverage", False):
            cmd.append("-c")

        # Target regions (BED file)
        if target_bed := params.get("target_bed"):
            cmd.extend(["-t", str(target_bed)])

        # Reference FASTA (for GC stats)
        if reference := params.get("reference"):
            cmd.extend(["-r", str(reference)])

        # Number of threads
        if threads := params.get("threads"):
            cmd.extend(["-@", str(threads)])

        # Input file
        cmd.append(str(params["input_file"]))

        return cmd

    def parse_output(self, result: ToolResult) -> Dict[str, Any]:
        """Parse samtools stats output into structured data."""
        stats = {
            "raw_total_sequences": 0,
            "reads_mapped": 0,
            "reads_unmapped": 0,
            "average_quality": 0.0,
            "insert_size_average": 0.0,
            "error_rate": 0.0,
        }

        for line in result.stdout.split("\n"):
            line = line.strip()

            if line.startswith("SN"):
                # Summary number
                parts = line.split("\t")
                if len(parts) >= 3:
                    key = parts[1].strip().rstrip(":")
                    value = parts[2].strip()

                    if "raw total sequences" in key.lower():
                        stats["raw_total_sequences"] = int(value)
                    elif "reads mapped" in key.lower() and "reads mapped and" not in key.lower():
                        stats["reads_mapped"] = int(value)
                    elif "reads unmapped" in key.lower():
                        stats["reads_unmapped"] = int(value)
                    elif "average quality" in key.lower():
                        stats["average_quality"] = float(value)
                    elif "insert size average" in key.lower():
                        stats["insert_size_average"] = float(value)
                    elif "error rate" in key.lower():
                        stats["error_rate"] = float(value)

        return stats
