# Claude Code Prompt: doc2md MCP Server (Python)

Copy and paste everything below the line into Claude Code.

---

Build a production-ready MCP (Model Context Protocol) server in Python called `doc2md` that converts PDF, DOCX, and PPTX files into clean, structured Markdown files written to disk — designed to be used as a format normalization layer so the resulting `.md` files can be added as resources to other MCP servers, RAG pipelines, and knowledge bases.

## Core Design Principle

**The primary output of every conversion is a `.md` file written to disk.** This is not a "return markdown as a string" tool — it is a "produce a usable .md` file on the filesystem" tool. The written files should be clean, self-contained, and ready to be referenced as MCP resources or ingested by downstream systems without any further processing.

## Project Requirements

### Core Architecture
- **Language:** Python 3.11+
- **MCP SDK:** Use `mcp` (the official Python MCP SDK, install via `pip install mcp`)
- **Transport:** Support both `stdio` and `sse` transports
- **Package manager:** `uv` preferred, `pip` as fallback
- **Build/packaging:** `pyproject.toml` with setuptools or hatchling

### Key Python Dependencies
- `pymupdf` (aka `fitz`) — PDF text and structure extraction (preferred over `pdfplumber`/`pdf-parse` for Python; handles complex layouts well)
- `python-docx` — DOCX parsing
- `python-pptx` — PPTX parsing
- `pydantic` — input validation and type safety (instead of zod)
- `pyyaml` — YAML frontmatter generation
- `mcp` — MCP server SDK

### MCP Tools to Expose

All tools share these common input parameters:
- `output_dir: str | None` — Directory to write the output `.md` file. Defaults to the same directory as the source file. If the source is provided as base64, defaults to the current working directory.
- `output_file_name: str | None` — Custom output filename. Defaults to the source filename with `.md` extension (e.g., `report.pdf` → `report.md`). If a file with that name already exists, append a timestamp suffix to avoid overwrites (e.g., `report_1707840000.md`).
- `overwrite: bool` — If True, overwrite existing files instead of appending a timestamp. Defaults to False.

All tools return the **absolute path to the written `.md` file** as the primary result, so other MCP servers or agents can immediately use it.

---

1. **`convert_pdf_to_markdown`**
   - Input: `{ file_path: str }` OR `{ base64_content: str, file_name: str }` + common params above
   - Use `pymupdf` for text, table, and structure extraction
   - Preserve headings, paragraphs, lists, tables (convert to proper Markdown tables)
   - Extract and describe images as `![image description](image_N.png)` placeholders
   - Preserve page breaks as `---` horizontal rules with `<!-- Page N -->` comments
   - Handle multi-column layouts by reading left-to-right, top-to-bottom
   - Handle scanned/image-only PDFs gracefully with a warning in the output and metadata

2. **`convert_docx_to_markdown`**
   - Input: `{ file_path: str }` OR `{ base64_content: str, file_name: str }` + common params above
   - Use `python-docx` for DOCX parsing
   - Preserve all heading levels (H1-H6)
   - Convert Word tables to Markdown tables with alignment
   - Preserve bold, italic, strikethrough, code formatting
   - Convert numbered and bulleted lists (including nested)
   - Preserve hyperlinks
   - Handle footnotes/endnotes as Markdown footnotes `[^1]`
   - Extract embedded images as base64 data URIs or placeholder references
   - Preserve comments as `<!-- Comment: ... -->` blocks

3. **`convert_pptx_to_markdown`**
   - Input: `{ file_path: str }` OR `{ base64_content: str, file_name: str }` + common params above
   - Use `python-pptx` for PPTX parsing
   - Each slide becomes an H2 section: `## Slide N: {title}`
   - Preserve slide titles, body text, bullet points
   - Convert tables in slides to Markdown tables
   - Include speaker notes under each slide as a blockquote: `> **Speaker Notes:** ...`
   - Describe images/charts as descriptive placeholders
   - Preserve slide order

4. **`convert_auto`**
   - Input: `{ file_path: str }` OR `{ base64_content: str, file_name: str, mime_type: str | None }` + common params above
   - Auto-detect file type from extension or MIME type and route to the correct converter
   - Return a clear error for unsupported file types

5. **`batch_convert`**
   - Input: `{ file_paths: list[str], output_dir: str | None }` + `overwrite: bool`
   - Convert multiple files, writing each `.md` file to `output_dir` (defaults to each source file's own directory if not specified)
   - Continue on individual file failures, reporting per-file errors
   - Return a list of results with paths to all successfully written files

### Output Format (all tools)

Every tool writes the `.md` file to disk AND returns this structured result:

```json
{
  "success": true,
  "output_path": "/absolute/path/to/report.md",
  "file_name": "report.md",
  "source_file": "report.pdf",
  "metadata": {
    "source_format": "pdf",
    "page_count": 12,
    "word_count": 4500,
    "has_images": true,
    "image_count": 3,
    "conversion_warnings": ["Page 5 contained a scanned image that could not be OCR'd"]
  }
}
```

The `output_path` is the most important field — it's what other MCP servers will use to access the file.

### Markdown Output Quality Standards

The written `.md` files must be:
- **Self-contained** — no external dependencies, readable as-is
- **Frontmatter included** — every file starts with YAML frontmatter containing source filename, source format, conversion date, page/slide count, and any warnings:
  ```yaml
  ---
  source: report.pdf
  format: pdf
  converted: 2025-02-13T12:00:00Z
  pages: 12
  word_count: 4500
  ---
  ```
- **Clean and well-structured** — proper heading hierarchy, no orphaned formatting, no garbage characters
- **Chunking-friendly** — use consistent heading levels so downstream RAG systems can split on `##` boundaries and get semantically meaningful sections
- **Complete** — lose NOTHING from the source document that can be represented as text

### Project Structure

```
doc2md/
├── src/
│   └── doc2md/
│       ├── __init__.py
│       ├── __main__.py           # Entry point: python -m doc2md
│       ├── server.py             # MCP server setup, tool registration, transport config
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── pdf.py            # PDF converter
│       │   ├── docx.py           # DOCX converter
│       │   ├── pptx.py           # PPTX converter
│       │   ├── auto.py           # Auto-detect router
│       │   └── batch.py          # Batch converter
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── markdown.py       # Shared MD formatting helpers (tables, lists, frontmatter)
│       │   ├── file_handler.py   # File reading, base64 decoding, output writing, path resolution
│       │   └── metadata.py       # Metadata extraction helpers
│       └── models.py             # Pydantic models for inputs, outputs, metadata
├── tests/
│   ├── __init__.py
│   ├── test_pdf.py
│   ├── test_docx.py
│   ├── test_pptx.py
│   ├── conftest.py               # Shared fixtures, test file generators
│   └── fixtures/                 # Small test files for each format
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── pyproject.toml
├── LICENSE                       # MIT License (full text, year 2025, copyright holder: benguy1000)
└── README.md
```

### README.md

Write a comprehensive README.md that includes:

1. **Project title and badges** — name, license badge, Docker badge, PyPI version badge
2. **One-line description** — "An MCP server that converts PDF, DOCX, and PPTX files into clean Markdown files on disk — ready for use as resources in other MCP servers."
3. **Why this exists** — brief explanation of the problem: LLM toolchains and MCP servers work best with plain text/Markdown, but organizations have documents in binary formats. This bridges the gap by normalizing everything to `.md` files on the filesystem.
4. **Quick start**
   - pip/uv: `uvx doc2md` or `pip install doc2md`
   - Docker: `docker run -v $(pwd):/data benguy1000/doc2md`
5. **MCP client configuration examples** with copy-pasteable JSON for:
   - Claude Desktop (`claude_desktop_config.json`)
   - Claude Code
   - Cursor
   - Generic MCP client
6. **Tool documentation** — every tool with:
   - Description
   - Full input schema
   - Example input
   - Example output (showing the `output_path`)
7. **Common workflows** — show practical examples:
   - "Convert a folder of sales decks to Markdown for a knowledge base MCP"
   - "Pipe converted docs into a vector database"
   - "Use with Claude Desktop to convert and then query documents"
8. **Configuration** — environment variables (`TRANSPORT`, `PORT`, `DEFAULT_OUTPUT_DIR`)
9. **Docker usage** — how to mount volumes so output files are accessible on the host
10. **Contributing** — brief guide
11. **License** — MIT

### LICENSE

Include the full MIT License text:
- Year: 2025
- Copyright holder: benguy1000

### Dockerfile

Use a multi-stage build:

**Stage 1 (build):**
- FROM python:3.11-slim
- Install uv or pip, copy source, install dependencies

**Stage 2 (production):**
- FROM python:3.11-slim
- Copy only the installed package and dependencies
- Set working directory to `/data` (mount point for user files)
- Support env vars: `TRANSPORT=stdio|sse` (default: stdio), `PORT=3000`, `DEFAULT_OUTPUT_DIR=/data/output`
- ENTRYPOINT runs the server: `python -m doc2md`

**docker-compose.yml:**
- Mount current directory as `/data` so the server can read source files and write `.md` output files back to the host filesystem
- Set sensible defaults

### Error Handling
- Every tool must catch all exceptions and return structured error responses — never crash the server
- Include meaningful error messages: file not found, corrupt file, unsupported format, password-protected file, permission denied on output directory
- Validate that `output_dir` exists and is writable before attempting conversion
- Log errors to stderr using Python's `logging` module (not stdout/print, to avoid corrupting stdio transport)

### Code Quality
- Full type hints on every function (use modern Python type syntax: `str | None`, `list[str]`)
- Add docstrings to all public functions
- Use Pydantic models for all tool input/output validation
- Add unit tests using `pytest` for each converter with fixture files
- Create small test fixture files programmatically in `conftest.py` if needed (use `python-docx`, `python-pptx`, and `pymupdf` to generate minimal test files)
- Tests should verify both the returned metadata AND that the `.md` file was actually written to disk with correct content
- Use `ruff` for linting and formatting

## Deployment Steps

After building and testing the project locally:

1. **Initialize git repo and push to GitHub:**
   ```
   gh repo create benguy1000/doc2md --public --source=. --push --description "MCP server that converts PDF, DOCX, PPTX to Markdown files on disk"
   ```
   If the repo already exists:
   ```
   git remote add origin https://github.com/benguy1000/doc2md.git
   git branch -M main
   git push -u origin main
   ```

2. **Build and push Docker image:**
   ```
   docker build -t benguy1000/doc2md:latest .
   docker tag benguy1000/doc2md:latest benguy1000/doc2md:v1.0.0
   docker login
   docker push benguy1000/doc2md:latest
   docker push benguy1000/doc2md:v1.0.0
   ```
   If I'm not logged into Docker Hub, prompt me to run `docker login` first.

3. **Verify everything works:**
   - Run `pytest` and confirm all tests pass
   - Run the MCP server locally with stdio and test converting a sample file — confirm the `.md` file appears on disk
   - Run the Docker container with a volume mount and confirm the `.md` file appears on the host filesystem
   - Verify the written `.md` files have correct frontmatter and clean formatting

## Important Notes
- The PRIMARY deliverable of every tool is a `.md` file on disk — the JSON response is secondary metadata
- Do NOT skip any converter — implement all three (PDF, DOCX, PPTX) fully
- Do NOT use placeholder/stub implementations — every tool must actually work end-to-end
- Content fidelity is paramount: the Markdown output should lose NOTHING that can be represented as text
- The output files must be immediately usable as MCP resources — no manual cleanup needed
- Use Python naming conventions throughout (snake_case for functions/variables, PascalCase for classes)
- Ask me before making major architectural decisions that deviate from this spec
