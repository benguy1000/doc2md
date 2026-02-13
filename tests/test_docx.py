"""Tests for DOCX converter."""

from __future__ import annotations

import base64
from pathlib import Path

from doc2md.tools.docx import convert_docx_to_markdown


def test_convert_docx_basic(sample_docx: Path, tmp_output_dir: Path):
    """Test basic DOCX to markdown conversion."""
    result = convert_docx_to_markdown(
        file_path=str(sample_docx),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    assert result.output_path is not None
    assert result.file_name == "test_sample.md"
    assert result.source_file == "test_sample.docx"
    assert result.metadata is not None
    assert result.metadata.source_format == "docx"

    # Verify file was written
    md_path = Path(result.output_path)
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")

    # Check frontmatter
    assert content.startswith("---\n")
    assert "source: test_sample.docx" in content
    assert "format: docx" in content

    # Check content was preserved
    assert "# Test Document" in content
    assert "## Section Two" in content
    assert "test paragraph" in content


def test_convert_docx_tables(sample_docx: Path, tmp_output_dir: Path):
    """Test that tables are converted to markdown."""
    result = convert_docx_to_markdown(
        file_path=str(sample_docx),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    content = Path(result.output_path).read_text(encoding="utf-8")

    assert "Name" in content
    assert "Value" in content
    assert "Alpha" in content
    assert "100" in content


def test_convert_docx_formatting(sample_docx: Path, tmp_output_dir: Path):
    """Test that bold and italic formatting is preserved."""
    result = convert_docx_to_markdown(
        file_path=str(sample_docx),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    content = Path(result.output_path).read_text(encoding="utf-8")

    assert "**Bold text**" in content
    assert "*italic text*" in content


def test_convert_docx_lists(sample_docx: Path, tmp_output_dir: Path):
    """Test that lists are converted."""
    result = convert_docx_to_markdown(
        file_path=str(sample_docx),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    content = Path(result.output_path).read_text(encoding="utf-8")

    assert "- Item one" in content
    assert "- Item two" in content


def test_convert_docx_base64(sample_docx: Path, tmp_output_dir: Path):
    """Test DOCX conversion from base64."""
    b64 = base64.b64encode(sample_docx.read_bytes()).decode("ascii")

    result = convert_docx_to_markdown(
        base64_content=b64,
        file_name="encoded.docx",
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    assert Path(result.output_path).exists()


def test_convert_docx_file_not_found(tmp_output_dir: Path):
    """Test error handling for missing file."""
    result = convert_docx_to_markdown(
        file_path="/nonexistent/file.docx",
        output_dir=str(tmp_output_dir),
    )

    assert result.success is False
    assert result.error is not None
