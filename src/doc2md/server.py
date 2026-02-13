"""MCP server setup, tool registration, and transport configuration."""

from __future__ import annotations

import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from doc2md.tools.auto import convert_auto
from doc2md.tools.batch import batch_convert
from doc2md.tools.docx import convert_docx_to_markdown
from doc2md.tools.pdf import convert_pdf_to_markdown
from doc2md.tools.pptx import convert_pptx_to_markdown

logger = logging.getLogger(__name__)

server = Server("doc2md")


TOOLS = [
    Tool(
        name="convert_pdf_to_markdown",
        description=(
            "Convert a PDF file to clean, structured Markdown and write it to disk. "
            "Preserves headings, paragraphs, lists, tables, and page breaks. "
            "Returns the absolute path to the written .md file. "
            "If file_path is not accessible (e.g. sandboxed/Docker), use base64_content instead."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the PDF file. Optional if base64_content is provided.",
                },
                "base64_content": {
                    "type": "string",
                    "description": "Base64-encoded PDF content. Use this when the file is not directly accessible (e.g. in Docker or sandboxed environments).",
                },
                "file_name": {
                    "type": "string",
                    "description": "Original filename (required with base64_content)",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory for the output .md file",
                },
                "output_file_name": {
                    "type": "string",
                    "description": "Custom output filename",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing files",
                    "default": False,
                },
            },
        },
    ),
    Tool(
        name="convert_docx_to_markdown",
        description=(
            "Convert a DOCX file to clean, structured Markdown and write it to disk. "
            "Preserves headings, formatting, tables, lists, hyperlinks, footnotes, and comments. "
            "Returns the absolute path to the written .md file. "
            "If file_path is not accessible (e.g. sandboxed/Docker), use base64_content instead."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the DOCX file. Optional if base64_content is provided.",
                },
                "base64_content": {
                    "type": "string",
                    "description": "Base64-encoded DOCX content. Use this when the file is not directly accessible (e.g. in Docker or sandboxed environments).",
                },
                "file_name": {
                    "type": "string",
                    "description": "Original filename (required with base64_content)",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory for the output .md file",
                },
                "output_file_name": {
                    "type": "string",
                    "description": "Custom output filename",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing files",
                    "default": False,
                },
            },
        },
    ),
    Tool(
        name="convert_pptx_to_markdown",
        description=(
            "Convert a PPTX file to clean, structured Markdown and write it to disk. "
            "Each slide becomes an H2 section with title, body text, tables, and speaker notes. "
            "Returns the absolute path to the written .md file. "
            "If file_path is not accessible (e.g. sandboxed/Docker), use base64_content instead."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the PPTX file. Optional if base64_content is provided.",
                },
                "base64_content": {
                    "type": "string",
                    "description": "Base64-encoded PPTX content. Use this when the file is not directly accessible (e.g. in Docker or sandboxed environments).",
                },
                "file_name": {
                    "type": "string",
                    "description": "Original filename (required with base64_content)",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory for the output .md file",
                },
                "output_file_name": {
                    "type": "string",
                    "description": "Custom output filename",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing files",
                    "default": False,
                },
            },
        },
    ),
    Tool(
        name="convert_auto",
        description=(
            "Auto-detect file type (PDF, DOCX, PPTX) and convert to Markdown. "
            "Routes to the appropriate converter based on file extension or MIME type. "
            "Returns the absolute path to the written .md file. "
            "If file_path is not accessible (e.g. sandboxed/Docker), use base64_content instead."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the source file. Optional if base64_content is provided.",
                },
                "base64_content": {
                    "type": "string",
                    "description": "Base64-encoded file content. Use this when the file is not directly accessible (e.g. in Docker or sandboxed environments).",
                },
                "file_name": {
                    "type": "string",
                    "description": "Original filename (required with base64_content)",
                },
                "mime_type": {
                    "type": "string",
                    "description": "MIME type for format detection",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory for the output .md file",
                },
                "output_file_name": {
                    "type": "string",
                    "description": "Custom output filename",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing files",
                    "default": False,
                },
            },
        },
    ),
    Tool(
        name="batch_convert",
        description=(
            "Convert multiple files (PDF, DOCX, PPTX) to Markdown in batch. "
            "Continues on individual file failures, reporting per-file errors. "
            "Returns a list of results with paths to all successfully written files."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "file_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of absolute paths to source files",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory for all output .md files",
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing files",
                    "default": False,
                },
            },
            "required": ["file_paths"],
        },
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available conversion tools."""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls by routing to the appropriate converter."""
    import json

    try:
        if name == "convert_pdf_to_markdown":
            result = convert_pdf_to_markdown(**arguments)
        elif name == "convert_docx_to_markdown":
            result = convert_docx_to_markdown(**arguments)
        elif name == "convert_pptx_to_markdown":
            result = convert_pptx_to_markdown(**arguments)
        elif name == "convert_auto":
            result = convert_auto(**arguments)
        elif name == "batch_convert":
            result = batch_convert(**arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))]

    except Exception as e:
        logger.error("Tool call failed: %s - %s", name, e)
        error_result = {"success": False, "error": str(e)}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def run_stdio():
    """Run the server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


async def run_sse(host: str = "0.0.0.0", port: int = 3000):
    """Run the server with SSE transport."""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route
    import uvicorn

    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())

    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request._send)

    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ],
    )

    config = uvicorn.Config(app, host=host, port=port)
    s = uvicorn.Server(config)
    await s.serve()
