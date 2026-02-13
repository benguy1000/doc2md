"""Pydantic models for doc2md tool inputs, outputs, and metadata."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FileInput(BaseModel):
    """Input for a single file conversion via file path."""

    file_path: str = Field(description="Absolute path to the source file")
    output_dir: str | None = Field(
        default=None,
        description="Directory to write the output .md file. Defaults to source file directory.",
    )
    output_file_name: str | None = Field(
        default=None,
        description="Custom output filename. Defaults to source filename with .md extension.",
    )
    overwrite: bool = Field(
        default=False,
        description="If True, overwrite existing files instead of appending a timestamp.",
    )


class Base64Input(BaseModel):
    """Input for a single file conversion via base64 content."""

    base64_content: str = Field(description="Base64-encoded file content")
    file_name: str = Field(description="Original filename (used for naming and format detection)")
    output_dir: str | None = Field(
        default=None,
        description="Directory to write the output .md file. Defaults to current working directory.",
    )
    output_file_name: str | None = Field(
        default=None,
        description="Custom output filename. Defaults to source filename with .md extension.",
    )
    overwrite: bool = Field(
        default=False,
        description="If True, overwrite existing files instead of appending a timestamp.",
    )


class AutoInput(BaseModel):
    """Input for auto-detect conversion."""

    file_path: str | None = Field(default=None, description="Absolute path to the source file")
    base64_content: str | None = Field(default=None, description="Base64-encoded file content")
    file_name: str | None = Field(default=None, description="Original filename")
    mime_type: str | None = Field(default=None, description="MIME type for format detection")
    output_dir: str | None = Field(default=None)
    output_file_name: str | None = Field(default=None)
    overwrite: bool = Field(default=False)


class BatchInput(BaseModel):
    """Input for batch conversion."""

    file_paths: list[str] = Field(description="List of absolute paths to source files")
    output_dir: str | None = Field(
        default=None,
        description="Directory to write all output files. Defaults to each source file's directory.",
    )
    overwrite: bool = Field(default=False)


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
