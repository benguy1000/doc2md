"""Batch converter for multiple files."""

from __future__ import annotations

import logging

from doc2md.models import BatchResult, ConversionResult
from doc2md.tools.auto import convert_auto

logger = logging.getLogger(__name__)


def batch_convert(
    file_paths: list[str],
    output_dir: str | None = None,
    overwrite: bool = False,
) -> BatchResult:
    """Convert multiple files, continuing on individual failures."""
    results: list[ConversionResult] = []
    successful = 0
    failed = 0

    for fp in file_paths:
        result = convert_auto(
            file_path=fp,
            output_dir=output_dir,
            overwrite=overwrite,
        )
        results.append(result)
        if result.success:
            successful += 1
        else:
            failed += 1

    return BatchResult(
        results=results,
        total=len(file_paths),
        successful=successful,
        failed=failed,
    )
