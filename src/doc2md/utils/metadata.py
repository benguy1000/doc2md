"""Metadata extraction helpers."""

from __future__ import annotations

from doc2md.models import ConversionMetadata


def build_metadata(
    source_format: str,
    page_count: int | None = None,
    slide_count: int | None = None,
    word_count: int = 0,
    has_images: bool = False,
    image_count: int = 0,
    warnings: list[str] | None = None,
) -> ConversionMetadata:
    """Build a ConversionMetadata instance."""
    return ConversionMetadata(
        source_format=source_format,
        page_count=page_count,
        slide_count=slide_count,
        word_count=word_count,
        has_images=has_images,
        image_count=image_count,
        conversion_warnings=warnings or [],
    )
