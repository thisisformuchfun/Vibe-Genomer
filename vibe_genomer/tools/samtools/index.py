"""
Samtools index wrapper.

Creates index files for BAM/CRAM files.
"""

from typing import Dict, Any, List
from pathlib import Path

from ..base import BioinformaticsTool
from ...utils import ToolError


class SamtoolsIndex(BioinformaticsTool):
    """Wrapper for samtools index command."""

    @property
    def binary_name(self) -> str:
        return "samtools"

    @property
    def description(self) -> str:
        return "Index SAM/BAM/CRAM files"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate parameters."""
        if "input_file" not in params:
            raise ToolError("input_file parameter is required")

        input_file = Path(params["input_file"])
        if not input_file.exists():
            raise ToolError(f"Input file not found: {input_file}")

        # Check file is BAM or CRAM
        if not str(input_file).endswith((".bam", ".cram")):
            raise ToolError("Input file must be BAM or CRAM format")

        return True

    def build_command(self, params: Dict[str, Any]) -> List[str]:
        """Build samtools index command."""
        cmd = [self.binary_name, "index"]

        # BAI vs CSI index
        if params.get("csi", False):
            cmd.append("-c")  # CSI index (for large chromosomes)
        else:
            cmd.append("-b")  # BAI index (default)

        # Number of threads
        if threads := params.get("threads"):
            cmd.extend(["-@", str(threads)])

        # Input file
        cmd.append(str(params["input_file"]))

        # Output index file (optional)
        if output_index := params.get("output_index"):
            cmd.append(str(output_index))

        return cmd

    def parse_output(self, result) -> str:
        """Parse samtools index output."""
        # Index command doesn't produce stdout output
        input_file = Path(result.metadata.get("input_file", ""))
        index_file = f"{input_file}.bai" if not result.metadata.get("csi") else f"{input_file}.csi"
        return f"Index created: {index_file}"
