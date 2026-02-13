"""Auto-detect file type and route to the correct converter."""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path

from doc2md.models import ConversionResult
from doc2md.tools.docx import convert_docx_to_markdown
from doc2md.tools.pdf import convert_pdf_to_markdown
from doc2md.tools.pptx import convert_pptx_to_markdown

logger = logging.getLogger(__name__)

EXTENSION_MAP = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".pptx": "pptx",
}

MIME_MAP = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
}

CONVERTERS = {
    "pdf": convert_pdf_to_markdown,
    "docx": convert_docx_to_markdown,
    "pptx": convert_pptx_to_markdown,
}


def _detect_format(
    file_path: str | None = None,
    file_name: str | None = None,
    mime_type: str | None = None,
) -> str | None:
    """Detect file format from extension or MIME type."""
    # Try MIME type first
    if mime_type and mime_type in MIME_MAP:
        return MIME_MAP[mime_type]

    # Try file extension
    name = file_name or file_path
    if name:
        ext = Path(name).suffix.lower()
        if ext in EXTENSION_MAP:
            return EXTENSION_MAP[ext]

    # Try guessing MIME type
    if name:
        guessed, _ = mimetypes.guess_type(name)
        if guessed and guessed in MIME_MAP:
            return MIME_MAP[guessed]

    return None


def convert_auto(
    file_path: str | None = None,
    base64_content: str | None = None,
    file_name: str | None = None,
    mime_type: str | None = None,
    output_dir: str | None = None,
    output_file_name: str | None = None,
    overwrite: bool = False,
) -> ConversionResult:
    """Auto-detect file type and convert to Markdown."""
    fmt = _detect_format(file_path, file_name, mime_type)

    if not fmt:
        source = file_name or file_path or "unknown"
        return ConversionResult(
            success=False,
            source_file=source,
            error=f"Unsupported file type. Supported formats: PDF, DOCX, PPTX. "
            f"File: {source}",
        )

    converter = CONVERTERS[fmt]
    return converter(
        file_path=file_path,
        base64_content=base64_content,
        file_name=file_name,
        output_dir=output_dir,
        output_file_name=output_file_name,
        overwrite=overwrite,
    )
