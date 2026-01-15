"""
Knowledge base update command implementation.

Handles downloading and updating reference databases.
"""

from typing import List, TYPE_CHECKING
from rich.progress import Progress, SpinnerColumn, TextColumn

if TYPE_CHECKING:
    from ...utils import Config, VibeLogger


def update_databases(
    databases: List[str],
    config: "Config",
    logger: "VibeLogger",
):
    """
    Update specified genomic knowledge bases.

    Args:
        databases: List of database names to update
        config: Application configuration
        logger: Logger instance
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:

        for db_name in databases:
            task = progress.add_task(f"Updating {db_name}...", total=None)

            try:
                if db_name == "clinvar":
                    _update_clinvar(config, logger)
                elif db_name == "ensembl":
                    _update_ensembl(config, logger)
                elif db_name == "ucsc":
                    _update_ucsc(config, logger)

                progress.update(task, completed=True)
                logger.success(f"{db_name} updated successfully")

            except Exception as e:
                logger.error(f"Failed to update {db_name}: {e}")
                raise


def _update_clinvar(config: "Config", logger: "VibeLogger"):
    """Update ClinVar database."""
    from ...knowledge.clinvar import ClinVarClient

    logger.debug("Updating ClinVar database")

    client = ClinVarClient(cache_dir=config.knowledge.cache_dir)
    client.download_latest()

    logger.info("ClinVar database updated")


def _update_ensembl(config: "Config", logger: "VibeLogger"):
    """Update Ensembl database."""
    from ...knowledge.ensembl import EnsemblClient

    logger.debug("Updating Ensembl database")

    client = EnsemblClient(cache_dir=config.knowledge.cache_dir)
    client.download_latest()

    logger.info("Ensembl database updated")


def _update_ucsc(config: "Config", logger: "VibeLogger"):
    """Update UCSC database."""
    from ...knowledge.ucsc import UCSCClient

    logger.debug("Updating UCSC database")

    client = UCSCClient(cache_dir=config.knowledge.cache_dir)
    client.download_reference_genomes()

    logger.info("UCSC database updated")
