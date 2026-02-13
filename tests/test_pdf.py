"""Tests for PDF converter."""

from __future__ import annotations

import base64
from pathlib import Path

from doc2md.tools.pdf import convert_pdf_to_markdown


def test_convert_pdf_basic(sample_pdf: Path, tmp_output_dir: Path):
    """Test basic PDF to markdown conversion."""
    result = convert_pdf_to_markdown(
        file_path=str(sample_pdf),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    assert result.output_path is not None
    assert result.file_name == "test_sample.md"
    assert result.source_file == "test_sample.pdf"
    assert result.metadata is not None
    assert result.metadata.source_format == "pdf"
    assert result.metadata.page_count == 2

    # Verify file was actually written
    md_path = Path(result.output_path)
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")

    # Check frontmatter
    assert content.startswith("---\n")
    assert "source: test_sample.pdf" in content
    assert "format: pdf" in content

    # Check page markers
    assert "<!-- Page 1 -->" in content
    assert "<!-- Page 2 -->" in content


def test_convert_pdf_base64(sample_pdf: Path, tmp_output_dir: Path):
    """Test PDF conversion from base64 input."""
    b64 = base64.b64encode(sample_pdf.read_bytes()).decode("ascii")

    result = convert_pdf_to_markdown(
        base64_content=b64,
        file_name="encoded.pdf",
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    assert result.file_name == "encoded.md"
    assert Path(result.output_path).exists()


def test_convert_pdf_custom_output_name(sample_pdf: Path, tmp_output_dir: Path):
    """Test PDF conversion with custom output filename."""
    result = convert_pdf_to_markdown(
        file_path=str(sample_pdf),
        output_dir=str(tmp_output_dir),
        output_file_name="custom_name.md",
    )

    assert result.success is True
    assert result.file_name == "custom_name.md"
    assert Path(result.output_path).exists()


def test_convert_pdf_no_overwrite(sample_pdf: Path, tmp_output_dir: Path):
    """Test that duplicate filenames get a timestamp suffix."""
    result1 = convert_pdf_to_markdown(
        file_path=str(sample_pdf),
        output_dir=str(tmp_output_dir),
    )
    result2 = convert_pdf_to_markdown(
        file_path=str(sample_pdf),
        output_dir=str(tmp_output_dir),
    )

    assert result1.success and result2.success
    assert result1.output_path != result2.output_path
    assert Path(result1.output_path).exists()
    assert Path(result2.output_path).exists()


def test_convert_pdf_overwrite(sample_pdf: Path, tmp_output_dir: Path):
    """Test that overwrite=True replaces existing files."""
    result1 = convert_pdf_to_markdown(
        file_path=str(sample_pdf),
        output_dir=str(tmp_output_dir),
    )
    result2 = convert_pdf_to_markdown(
        file_path=str(sample_pdf),
        output_dir=str(tmp_output_dir),
        overwrite=True,
    )

    assert result1.success and result2.success
    assert result1.output_path == result2.output_path


def test_convert_pdf_file_not_found(tmp_output_dir: Path):
    """Test error handling for missing file."""
    result = convert_pdf_to_markdown(
        file_path="/nonexistent/path/file.pdf",
        output_dir=str(tmp_output_dir),
    )

    assert result.success is False
    assert result.error is not None
    assert "not found" in result.error.lower() or "no such file" in result.error.lower()


def test_convert_pdf_word_count(sample_pdf: Path, tmp_output_dir: Path):
    """Test that word count is populated."""
    result = convert_pdf_to_markdown(
        file_path=str(sample_pdf),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    assert result.metadata.word_count > 0
