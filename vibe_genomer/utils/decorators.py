"""
Utility decorators for Vibe-Genomer.

This module provides decorators for common patterns like retries, caching,
validation, and error handling.
"""

import functools
import time
from typing import Any, Callable, Optional, Type, Union
from pathlib import Path

from .exceptions import VibeGenomerError
from .logging import get_logger


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry

    Example:
        @retry(max_attempts=3, delay=1.0)
        def unstable_api_call():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1

        return wrapper

    return decorator


def log_execution(level: str = "INFO"):
    """
    Log function execution with timing.

    Args:
        level: Log level to use (INFO, DEBUG, etc.)

    Example:
        @log_execution(level="DEBUG")
        def process_data(data):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            func_name = f"{func.__module__}.{func.__name__}"

            logger.debug(f"Executing {func_name}")
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"{func_name} completed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{func_name} failed after {elapsed:.3f}s: {e}")
                raise

        return wrapper

    return decorator


def validate_file_exists(param_name: str = "file_path"):
    """
    Validate that a file exists before executing function.

    Args:
        param_name: Name of the parameter containing the file path

    Example:
        @validate_file_exists("bam_file")
        def process_bam(bam_file: Path):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from .exceptions import InvalidConfigError

            # Get the file path from args or kwargs
            if param_name in kwargs:
                file_path = kwargs[param_name]
            else:
                # Try to find in args based on function signature
                import inspect
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if param_name in params:
                    param_idx = params.index(param_name)
                    if param_idx < len(args):
                        file_path = args[param_idx]
                    else:
                        raise InvalidConfigError(
                            f"Parameter '{param_name}' not found in function call"
                        )
                else:
                    raise InvalidConfigError(
                        f"Parameter '{param_name}' not found in function signature"
                    )

            # Validate file exists
            if isinstance(file_path, (str, Path)):
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"File not found: {path}")
                if not path.is_file():
                    raise ValueError(f"Path is not a file: {path}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def cache_result(cache_dir: Optional[Path] = None, ttl_seconds: Optional[int] = None):
    """
    Cache function results to disk.

    Args:
        cache_dir: Directory to store cache files (defaults to ~/.vibe-genomer/cache)
        ttl_seconds: Time-to-live in seconds (None for no expiration)

    Example:
        @cache_result(ttl_seconds=3600)
        def expensive_computation(param):
            ...
    """
    import pickle
    import hashlib

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from .config import get_config

            # Determine cache directory
            if cache_dir is None:
                config = get_config()
                cache_path = config.config_dir / "cache"
            else:
                cache_path = cache_dir

            cache_path.mkdir(parents=True, exist_ok=True)

            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            cache_file = cache_path / f"{cache_key}.pkl"

            # Check if cached result exists and is valid
            if cache_file.exists():
                if ttl_seconds is None:
                    # No expiration
                    with open(cache_file, "rb") as f:
                        return pickle.load(f)
                else:
                    # Check if cache is still valid
                    age = time.time() - cache_file.stat().st_mtime
                    if age < ttl_seconds:
                        with open(cache_file, "rb") as f:
                            return pickle.load(f)

            # Compute result and cache it
            result = func(*args, **kwargs)
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)

            return result

        return wrapper

    return decorator


def require_tool(tool_name: str):
    """
    Ensure a bioinformatics tool is available before executing function.

    Args:
        tool_name: Name of the required tool (e.g., "samtools", "bedtools")

    Example:
        @require_tool("samtools")
        def process_bam():
            ...
    """
    import shutil

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from .exceptions import ToolNotFoundError

            if not shutil.which(tool_name):
                raise ToolNotFoundError(
                    f"Required tool '{tool_name}' not found in PATH. "
                    f"Please install it before using this function."
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def handle_errors(
    error_type: Type[VibeGenomerError] = VibeGenomerError,
    message: Optional[str] = None,
    log_traceback: bool = True,
):
    """
    Handle errors and convert them to custom exceptions.

    Args:
        error_type: Custom exception type to raise
        message: Custom error message
        log_traceback: Whether to log full traceback

    Example:
        @handle_errors(ToolExecutionError, "Failed to execute tool")
        def run_tool():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger()
            try:
                return func(*args, **kwargs)
            except error_type:
                # Already our custom exception, re-raise
                raise
            except Exception as e:
                error_msg = message or f"Error in {func.__name__}: {e}"

                if log_traceback:
                    logger.exception(error_msg)

                raise error_type(error_msg, details={"original_error": str(e)}) from e

        return wrapper

    return decorator


def genomic_context(func: Callable) -> Callable:
    """
    Log genomic context when function is called.

    Expects function to have parameters: chromosome, start, end, and optionally gene.

    Example:
        @genomic_context
        def analyze_region(chromosome: str, start: int, end: int, gene: str = None):
            ...
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        import inspect

        logger = get_logger()
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Extract genomic coordinates
        chromosome = bound_args.arguments.get("chromosome")
        start = bound_args.arguments.get("start")
        end = bound_args.arguments.get("end")
        gene = bound_args.arguments.get("gene")

        if chromosome and start and end:
            logger.genomic_context(chromosome, start, end, gene)

        return func(*args, **kwargs)

    return wrapper
