"""
Samtools view wrapper.

Used for viewing and converting SAM/BAM/CRAM files.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from ..base import BioinformaticsTool
from ...utils import ToolError


class SamtoolsView(BioinformaticsTool):
    """Wrapper for samtools view command."""

    @property
    def binary_name(self) -> str:
        return "samtools"

    @property
    def description(self) -> str:
        return "View and convert SAM/BAM/CRAM files"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate parameters."""
        if "input_file" not in params:
            raise ToolError("input_file parameter is required")

        input_file = Path(params["input_file"])
        if not input_file.exists():
            raise ToolError(f"Input file not found: {input_file}")

        return True

    def build_command(self, params: Dict[str, Any]) -> List[str]:
        """Build samtools view command."""
        cmd = [self.binary_name, "view"]

        # Output format
        if params.get("output_bam", False):
            cmd.append("-b")  # BAM output
        elif params.get("output_cram", False):
            cmd.append("-C")  # CRAM output
        # Default is SAM

        # Output to file
        if output_file := params.get("output_file"):
            cmd.extend(["-o", str(output_file)])

        # Include header
        if params.get("with_header", False):
            cmd.append("-h")

        # Region filtering
        if region := params.get("region"):
            # Region will be added after input file
            pass

        # Quality filtering
        if min_mapq := params.get("min_mapq"):
            cmd.extend(["-q", str(min_mapq)])

        # Flag filtering
        if require_flags := params.get("require_flags"):
            cmd.extend(["-f", str(require_flags)])

        if exclude_flags := params.get("exclude_flags"):
            cmd.extend(["-F", str(exclude_flags)])

        # Number of threads
        if threads := params.get("threads"):
            cmd.extend(["-@", str(threads)])

        # Input file
        cmd.append(str(params["input_file"]))

        # Region (must come after input file)
        if region := params.get("region"):
            cmd.append(region)

        return cmd

    def parse_output(self, result) -> str:
        """Parse samtools view output."""
        # If output file was specified, return the path
        # Otherwise return stdout
        return result.stdout if result.stdout else "Output written to file"


class SamtoolsViewBuilder:
    """
    Fluent builder for samtools view commands.

    Example:
        >>> view = SamtoolsViewBuilder()
        >>>     .input("sample.bam")
        >>>     .region("chr1:1000-2000")
        >>>     .min_mapq(30)
        >>>     .with_header()
        >>>     .build()
    """

    def __init__(self):
        self.params = {}

    def input(self, file_path: str) -> "SamtoolsViewBuilder":
        """Set input file."""
        self.params["input_file"] = file_path
        return self

    def output(self, file_path: str) -> "SamtoolsViewBuilder":
        """Set output file."""
        self.params["output_file"] = file_path
        return self

    def region(self, region: str) -> "SamtoolsViewBuilder":
        """Set region to extract (e.g., chr1:1000-2000)."""
        self.params["region"] = region
        return self

    def min_mapq(self, mapq: int) -> "SamtoolsViewBuilder":
        """Set minimum mapping quality."""
        self.params["min_mapq"] = mapq
        return self

    def with_header(self) -> "SamtoolsViewBuilder":
        """Include SAM header in output."""
        self.params["with_header"] = True
        return self

    def output_bam(self) -> "SamtoolsViewBuilder":
        """Output as BAM format."""
        self.params["output_bam"] = True
        return self

    def threads(self, n: int) -> "SamtoolsViewBuilder":
        """Set number of threads."""
        self.params["threads"] = n
        return self

    def build(self) -> Dict[str, Any]:
        """Build parameters dictionary."""
        return self.params
