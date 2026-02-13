"""Pydantic models for doc2md tool inputs, outputs, and metadata."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ConversionMetadata(BaseModel):
    """Metadata about a conversion result."""

    source_format: str
    page_count: int | None = None
    slide_count: int | None = None
    word_count: int = 0
    has_images: bool = False
    image_count: int = 0
    conversion_warnings: list[str] = Field(default_factory=list)


class ConversionResult(BaseModel):
    """Result of a single file conversion."""

    success: bool
    output_path: str | None = None
    file_name: str | None = None
    source_file: str
    metadata: ConversionMetadata | None = None
    error: str | None = None


class BatchResult(BaseModel):
    """Result of a batch conversion."""

    results: list[ConversionResult]
    total: int
    successful: int
    failed: int
