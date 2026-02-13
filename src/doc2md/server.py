"""MCP server for doc2md — converts PDF, DOCX, PPTX to Markdown."""

from __future__ import annotations

from fastmcp import FastMCP

from doc2md.tools.auto import convert_auto as _convert_auto
from doc2md.tools.batch import batch_convert as _batch_convert
from doc2md.tools.docx import convert_docx_to_markdown as _convert_docx
from doc2md.tools.pdf import convert_pdf_to_markdown as _convert_pdf
from doc2md.tools.pptx import convert_pptx_to_markdown as _convert_pptx

mcp = FastMCP(
    "doc2md",
    instructions=(
        "doc2md converts PDF, DOCX, and PPTX files to clean Markdown on disk. "
        "Each tool accepts either a file_path OR base64_content + file_name. "
        "If you get a file-not-found error (common in Docker/sandboxed environments), "
        "retry with base64_content instead of file_path. "
        "When no output_dir is specified, output goes to the source file's directory "
        "(file_path mode) or the current working directory (base64 mode)."
    ),
)


@mcp.tool
def convert_pdf_to_markdown(
    file_path: str | None = None,
    base64_content: str | None = None,
    file_name: str | None = None,
    output_dir: str | None = None,
    output_file_name: str | None = None,
    overwrite: bool = False,
) -> dict:
    """Convert a PDF to Markdown. Preserves headings, paragraphs, lists, tables, and page breaks.

    Provide file_path for local files, or base64_content + file_name when the file
    is not directly accessible (e.g. in Docker or sandboxed environments).
    """
    result = _convert_pdf(
        file_path=file_path,
        base64_content=base64_content,
        file_name=file_name,
        output_dir=output_dir,
        output_file_name=output_file_name,
        overwrite=overwrite,
    )
    return result.model_dump()


@mcp.tool
def convert_docx_to_markdown(
    file_path: str | None = None,
    base64_content: str | None = None,
    file_name: str | None = None,
    output_dir: str | None = None,
    output_file_name: str | None = None,
    overwrite: bool = False,
) -> dict:
    """Convert a DOCX to Markdown. Preserves headings, formatting, tables, lists, hyperlinks, footnotes, and comments.

    Provide file_path for local files, or base64_content + file_name when the file
    is not directly accessible (e.g. in Docker or sandboxed environments).
    """
    result = _convert_docx(
        file_path=file_path,
        base64_content=base64_content,
        file_name=file_name,
        output_dir=output_dir,
        output_file_name=output_file_name,
        overwrite=overwrite,
    )
    return result.model_dump()


@mcp.tool
def convert_pptx_to_markdown(
    file_path: str | None = None,
    base64_content: str | None = None,
    file_name: str | None = None,
    output_dir: str | None = None,
    output_file_name: str | None = None,
    overwrite: bool = False,
) -> dict:
    """Convert a PPTX to Markdown. Each slide becomes an H2 section with title, body, tables, and speaker notes.

    Provide file_path for local files, or base64_content + file_name when the file
    is not directly accessible (e.g. in Docker or sandboxed environments).
    """
    result = _convert_pptx(
        file_path=file_path,
        base64_content=base64_content,
        file_name=file_name,
        output_dir=output_dir,
        output_file_name=output_file_name,
        overwrite=overwrite,
    )
    return result.model_dump()


@mcp.tool
def convert_auto(
    file_path: str | None = None,
    base64_content: str | None = None,
    file_name: str | None = None,
    mime_type: str | None = None,
    output_dir: str | None = None,
    output_file_name: str | None = None,
    overwrite: bool = False,
) -> dict:
    """Auto-detect file type (PDF, DOCX, PPTX) and convert to Markdown.

    Provide file_path for local files, or base64_content + file_name when the file
    is not directly accessible (e.g. in Docker or sandboxed environments).
    """
    result = _convert_auto(
        file_path=file_path,
        base64_content=base64_content,
        file_name=file_name,
        mime_type=mime_type,
        output_dir=output_dir,
        output_file_name=output_file_name,
        overwrite=overwrite,
    )
    return result.model_dump()


@mcp.tool
def batch_convert(
    file_paths: list[str],
    output_dir: str | None = None,
    overwrite: bool = False,
) -> dict:
    """Convert multiple files (PDF, DOCX, PPTX) to Markdown in batch. Continues on individual file failures."""
    result = _batch_convert(
        file_paths=file_paths,
        output_dir=output_dir,
        overwrite=overwrite,
    )
    return result.model_dump()
