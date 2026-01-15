"""
ClinVar integration stub.
"""


class ClinVarClient:
    """Client for ClinVar database."""

    def __init__(self, cache_dir):
        self.cache_dir = cache_dir

    def download_latest(self):
        """Download latest ClinVar data."""
        # Stub implementation
        pass
