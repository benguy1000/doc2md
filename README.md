# doc2md

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/docker/v/benguy1000/doc2md?label=Docker)](https://hub.docker.com/r/benguy1000/doc2md)
[![PyPI](https://img.shields.io/pypi/v/doc2md)](https://pypi.org/project/doc2md/)

An MCP server that converts PDF, DOCX, and PPTX files into clean Markdown files on disk — ready for use as resources in other MCP servers.

## Why This Exists

LLM toolchains, RAG pipelines, and MCP servers work best with plain text and Markdown. But organizations have years of documents locked in binary formats — PDFs, Word docs, and PowerPoint decks. **doc2md** bridges the gap by normalizing everything to `.md` files on the filesystem, so they can be immediately referenced as MCP resources, ingested into vector databases, or added to knowledge bases without any manual cleanup.

## Quick Start

### pip / uv

```bash
# Install with pip
pip install doc2md

# Or with uv
uvx doc2md
```

### Docker

```bash
docker run -v $(pwd):/data benguy1000/doc2md
```

## MCP Client Configuration

### Claude Desktop (local Python)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "doc2md": {
      "command": "python",
      "args": ["-m", "doc2md"],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

### Claude Desktop (Docker)

If you run Claude Desktop with Docker-based MCP servers, mount your files directory so the container can access them:

```json
{
  "mcpServers": {
    "doc2md": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-v", "/path/to/your/files:/data",
        "benguy1000/doc2md"
      ]
    }
  }
}
```

> **Note:** In sandboxed or Docker environments, host file paths (e.g. `/mnt/user-data/uploads/`) may not be accessible inside the container. If a file path doesn't resolve, use `base64_content` and `file_name` parameters instead — the LLM will automatically switch to this approach when it receives a path-not-found diagnostic.

### Claude Code

Add to your project's `.mcp.json` or global MCP config:

```json
{
  "mcpServers": {
    "doc2md": {
      "command": "python",
      "args": ["-m", "doc2md"]
    }
  }
}
```

> **Working directory:** Claude Code launches MCP servers with your project directory as CWD. When using `base64_content` without an `output_dir`, the converted `.md` file is written to your project directory. Use `output_dir` to control where output lands.

### Cursor

```json
{
  "mcpServers": {
    "doc2md": {
      "command": "python",
      "args": ["-m", "doc2md"],
      "transport": "stdio"
    }
  }
}
```

### Generic MCP Client (Docker + SSE)

```json
{
  "mcpServers": {
    "doc2md": {
      "url": "http://localhost:3000/sse",
      "transport": "sse"
    }
  }
}
```

## Tools

### `convert_pdf_to_markdown`

Convert a PDF file to structured Markdown. Preserves headings, paragraphs, lists, tables, and page breaks.

**Input:**

```json
{
  "file_path": "/path/to/report.pdf",
  "output_dir": "/path/to/output",
  "overwrite": false
}
```

**Output:**

```json
{
  "success": true,
  "output_path": "/path/to/output/report.md",
  "file_name": "report.md",
  "source_file": "report.pdf",
  "metadata": {
    "source_format": "pdf",
    "page_count": 12,
    "word_count": 4500,
    "has_images": true,
    "image_count": 3,
    "conversion_warnings": []
  }
}
```

### `convert_docx_to_markdown`

Convert a DOCX file to Markdown. Preserves headings, formatting (bold, italic, strikethrough), tables, lists, hyperlinks, footnotes, and comments.

**Input:**

```json
{
  "file_path": "/path/to/document.docx",
  "output_dir": "/path/to/output"
}
```

**Output:**

```json
{
  "success": true,
  "output_path": "/path/to/output/document.md",
  "file_name": "document.md",
  "source_file": "document.docx",
  "metadata": {
    "source_format": "docx",
    "page_count": 1,
    "word_count": 2300,
    "has_images": false,
    "image_count": 0,
    "conversion_warnings": []
  }
}
```

### `convert_pptx_to_markdown`

Convert a PPTX file to Markdown. Each slide becomes an H2 section with title, body text, tables, and speaker notes.

**Input:**

```json
{
  "file_path": "/path/to/deck.pptx",
  "output_dir": "/path/to/output"
}
```

**Output:**

```json
{
  "success": true,
  "output_path": "/path/to/output/deck.md",
  "file_name": "deck.md",
  "source_file": "deck.pptx",
  "metadata": {
    "source_format": "pptx",
    "slide_count": 20,
    "word_count": 1800,
    "has_images": true,
    "image_count": 5,
    "conversion_warnings": []
  }
}
```

### `convert_auto`

Auto-detect file type from extension or MIME type and route to the correct converter.

**Input:**

```json
{
  "file_path": "/path/to/any-document.pdf",
  "output_dir": "/path/to/output"
}
```

### `batch_convert`

Convert multiple files at once. Continues on individual failures.

**Input:**

```json
{
  "file_paths": [
    "/path/to/report.pdf",
    "/path/to/notes.docx",
    "/path/to/slides.pptx"
  ],
  "output_dir": "/path/to/output"
}
```

**Output:**

```json
{
  "results": [
    { "success": true, "output_path": "/path/to/output/report.md", "..." : "..." },
    { "success": true, "output_path": "/path/to/output/notes.md", "..." : "..." },
    { "success": true, "output_path": "/path/to/output/slides.md", "..." : "..." }
  ],
  "total": 3,
  "successful": 3,
  "failed": 0
}
```

### Base64 Input (all single-file tools)

All single-file tools also accept base64-encoded content instead of a file path:

```json
{
  "base64_content": "JVBERi0xLjQK...",
  "file_name": "report.pdf",
  "output_dir": "/path/to/output"
}
```

## Common Workflows

### Convert a folder of sales decks to Markdown for a knowledge base

```bash
# Using batch_convert with all PPTX files in a directory
python -c "
from doc2md.tools.batch import batch_convert
from pathlib import Path

files = [str(f) for f in Path('/data/sales-decks').glob('*.pptx')]
result = batch_convert(files, output_dir='/data/knowledge-base')
print(f'Converted {result.successful}/{result.total} files')
"
```

### Pipe converted docs into a vector database

1. Use doc2md to convert all documents to `.md` files
2. Point your RAG pipeline's document loader at the output directory
3. The clean Markdown with consistent heading hierarchy makes chunking reliable

### Use with Claude Desktop to convert and then query documents

1. Configure doc2md as an MCP server in Claude Desktop
2. Ask Claude: "Convert /path/to/quarterly-report.pdf to markdown"
3. The `.md` file is written to disk and can be referenced in follow-up queries

## Configuration

| Environment Variable   | Description                                | Default        |
| ---------------------- | ------------------------------------------ | -------------- |
| `TRANSPORT`            | Transport mode: `stdio` or `sse`           | `stdio`        |
| `PORT`                 | Port for SSE transport                     | `3000`         |
| `DEFAULT_OUTPUT_DIR`   | Default directory for output files         | Source file dir |

## Docker Usage

Mount your files directory so doc2md can read source files and write output:

```bash
# stdio mode (for MCP clients)
docker run -v $(pwd):/data benguy1000/doc2md

# SSE mode (for network access)
docker run -p 3000:3000 -v $(pwd):/data -e TRANSPORT=sse benguy1000/doc2md
```

Output `.md` files will appear in the mounted directory on your host filesystem.

## Contributing

1. Clone the repo
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`
4. Lint: `ruff check src/ tests/`
5. Format: `ruff format src/ tests/`

## License

[MIT](LICENSE) — Copyright (c) 2025 benguy1000
