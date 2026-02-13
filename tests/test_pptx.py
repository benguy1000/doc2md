"""Tests for PPTX converter."""

from __future__ import annotations

import base64
from pathlib import Path

from doc2md.tools.pptx import convert_pptx_to_markdown


def test_convert_pptx_basic(sample_pptx: Path, tmp_output_dir: Path):
    """Test basic PPTX to markdown conversion."""
    result = convert_pptx_to_markdown(
        file_path=str(sample_pptx),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    assert result.output_path is not None
    assert result.file_name == "test_sample.md"
    assert result.source_file == "test_sample.pptx"
    assert result.metadata is not None
    assert result.metadata.source_format == "pptx"
    assert result.metadata.slide_count == 3

    # Verify file was written
    md_path = Path(result.output_path)
    assert md_path.exists()
    content = md_path.read_text(encoding="utf-8")

    # Check frontmatter
    assert content.startswith("---\n")
    assert "source: test_sample.pptx" in content
    assert "format: pptx" in content


def test_convert_pptx_slides(sample_pptx: Path, tmp_output_dir: Path):
    """Test that slide structure is preserved."""
    result = convert_pptx_to_markdown(
        file_path=str(sample_pptx),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    content = Path(result.output_path).read_text(encoding="utf-8")

    assert "## Slide 1:" in content
    assert "## Slide 2:" in content
    assert "Presentation Title" in content


def test_convert_pptx_speaker_notes(sample_pptx: Path, tmp_output_dir: Path):
    """Test that speaker notes are included."""
    result = convert_pptx_to_markdown(
        file_path=str(sample_pptx),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    content = Path(result.output_path).read_text(encoding="utf-8")

    assert "**Speaker Notes:**" in content
    assert "speaker notes for slide 2" in content


def test_convert_pptx_tables(sample_pptx: Path, tmp_output_dir: Path):
    """Test that slide tables are converted."""
    result = convert_pptx_to_markdown(
        file_path=str(sample_pptx),
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    content = Path(result.output_path).read_text(encoding="utf-8")

    assert "Header A" in content
    assert "Cell 1" in content


def test_convert_pptx_base64(sample_pptx: Path, tmp_output_dir: Path):
    """Test PPTX conversion from base64."""
    b64 = base64.b64encode(sample_pptx.read_bytes()).decode("ascii")

    result = convert_pptx_to_markdown(
        base64_content=b64,
        file_name="encoded.pptx",
        output_dir=str(tmp_output_dir),
    )

    assert result.success is True
    assert Path(result.output_path).exists()


def test_convert_pptx_file_not_found(tmp_output_dir: Path):
    """Test error handling for missing file."""
    result = convert_pptx_to_markdown(
        file_path="/nonexistent/file.pptx",
        output_dir=str(tmp_output_dir),
    )

    assert result.success is False
    assert result.error is not None
