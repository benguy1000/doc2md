"""PDF to Markdown converter using PyMuPDF."""

from __future__ import annotations

import logging

import pymupdf

from doc2md.models import ConversionResult
from doc2md.utils.file_handler import (
    cleanup_temp_dir,
    resolve_output_path,
    resolve_source_file,
    write_markdown,
)
from doc2md.utils.markdown import (
    clean_text,
    count_words,
    format_table,
    generate_frontmatter,
)
from doc2md.utils.metadata import build_metadata

logger = logging.getLogger(__name__)


def _extract_page_tables(page: pymupdf.Page) -> list[str]:
    """Extract tables from a page and return as markdown strings."""
    tables_md = []
    try:
        tables = page.find_tables()
        for table in tables:
            data = table.extract()
            if not data or len(data) < 1:
                continue
            headers = [str(c) if c else "" for c in data[0]]
            rows = [[str(c) if c else "" for c in row] for row in data[1:]]
            md = format_table(headers, rows)
            if md:
                tables_md.append(md)
    except Exception as e:
        logger.debug("Table extraction failed on page: %s", e)
    return tables_md


def _extract_page_text(page: pymupdf.Page) -> tuple[str, int]:
    """Extract text from a page, returning (text, image_count)."""
    image_count = 0
    try:
        images = page.get_images(full=True)
        image_count = len(images)
    except Exception:
        pass

    # Get text blocks sorted top-to-bottom, left-to-right
    text = page.get_text("text")
    return clean_text(text).strip(), image_count


def convert_pdf_to_markdown(
    file_path: str | None = None,
    base64_content: str | None = None,
    file_name: str | None = None,
    output_dir: str | None = None,
    output_file_name: str | None = None,
    overwrite: bool = False,
) -> ConversionResult:
    """Convert a PDF file to Markdown and write to disk."""
    temp_dir = None
    try:
        source_path, source_name, temp_dir = resolve_source_file(
            file_path, base64_content, file_name
        )
        is_base64 = base64_content is not None

        doc = pymupdf.open(str(source_path))
        page_count = len(doc)
        warnings: list[str] = []
        total_images = 0
        sections: list[str] = []

        for page_num in range(page_count):
            page = doc[page_num]
            text, img_count = _extract_page_text(page)
            total_images += img_count

            # Check for scanned/image-only page
            if not text.strip() and img_count > 0:
                warnings.append(
                    f"Page {page_num + 1} appears to be a scanned image "
                    "that could not be OCR'd"
                )
                text = f"*[Page {page_num + 1} contains a scanned image with no extractable text]*"

            # Add image placeholders
            if img_count > 0:
                img_refs = []
                for i in range(img_count):
                    img_refs.append(f"![image](image_p{page_num + 1}_{i + 1}.png)")
                text += "\n\n" + "\n".join(img_refs)

            # Extract tables
            tables_md = _extract_page_tables(page)
            if tables_md:
                text += "\n\n" + "\n\n".join(tables_md)

            # Build page section
            page_section = f"<!-- Page {page_num + 1} -->\n\n{text}"
            sections.append(page_section)

        doc.close()

        body = "\n\n---\n\n".join(sections)
        word_count = count_words(body)

        frontmatter = generate_frontmatter(
            source=source_name,
            fmt="pdf",
            pages=page_count,
            word_count=word_count,
            warnings=warnings if warnings else None,
        )

        md_content = frontmatter + "\n" + body + "\n"

        output_path = resolve_output_path(
            source_name, source_path, output_dir, output_file_name, overwrite, is_base64
        )
        write_markdown(output_path, md_content)

        metadata = build_metadata(
            source_format="pdf",
            page_count=page_count,
            word_count=word_count,
            has_images=total_images > 0,
            image_count=total_images,
            warnings=warnings,
        )

        return ConversionResult(
            success=True,
            output_path=str(output_path),
            file_name=output_path.name,
            source_file=source_name,
            metadata=metadata,
        )

    except Exception as e:
        logger.error("PDF conversion failed: %s", e)
        return ConversionResult(
            success=False,
            source_file=file_name or (file_path or "unknown"),
            error=str(e),
        )
    finally:
        cleanup_temp_dir(temp_dir)
