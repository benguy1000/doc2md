"""File reading, base64 decoding, output writing, and path resolution."""

from __future__ import annotations

import base64
import logging
import os
import tempfile
import time
from pathlib import Path

logger = logging.getLogger(__name__)


def resolve_source_file(
    file_path: str | None = None,
    base64_content: str | None = None,
    file_name: str | None = None,
) -> tuple[Path, str, Path | None]:
    """Resolve the source file from either a path or base64 content.

    Returns:
        Tuple of (resolved_path, source_name, temp_dir_or_None).
        If base64, the file is written to a temp dir that should be cleaned up later.
    """
    if file_path:
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
        if not path.is_file():
            raise ValueError(f"Source path is not a file: {file_path}")
        return path, path.name, None

    if base64_content and file_name:
        try:
            data = base64.b64decode(base64_content)
        except Exception as e:
            raise ValueError(f"Invalid base64 content: {e}") from e

        temp_dir = Path(tempfile.mkdtemp(prefix="doc2md_"))
        temp_path = temp_dir / file_name
        temp_path.write_bytes(data)
        return temp_path, file_name, temp_dir

    raise ValueError("Must provide either 'file_path' or both 'base64_content' and 'file_name'")


def resolve_output_path(
    source_name: str,
    source_path: Path,
    output_dir: str | None = None,
    output_file_name: str | None = None,
    overwrite: bool = False,
    is_base64: bool = False,
) -> Path:
    """Resolve the output .md file path.

    Returns the absolute path where the .md file should be written.
    """
    # Determine output directory
    if output_dir:
        out_dir = Path(output_dir).resolve()
    elif is_base64:
        out_dir = Path.cwd()
    else:
        out_dir = source_path.parent

    if not out_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {out_dir}")
    if not os.access(str(out_dir), os.W_OK):
        raise PermissionError(f"Output directory is not writable: {out_dir}")

    # Determine output filename
    if output_file_name:
        md_name = output_file_name
        if not md_name.endswith(".md"):
            md_name += ".md"
    else:
        md_name = Path(source_name).stem + ".md"

    out_path = out_dir / md_name

    # Handle existing files
    if out_path.exists() and not overwrite:
        stem = out_path.stem
        timestamp = int(time.time())
        md_name = f"{stem}_{timestamp}.md"
        out_path = out_dir / md_name

    return out_path


def write_markdown(output_path: Path, content: str) -> None:
    """Write markdown content to the output file."""
    output_path.write_text(content, encoding="utf-8")
    logger.info("Wrote markdown to %s", output_path)


def cleanup_temp_dir(temp_dir: Path | None) -> None:
    """Clean up a temporary directory if it exists."""
    if temp_dir and temp_dir.exists():
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
