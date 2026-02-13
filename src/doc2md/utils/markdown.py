"""Shared Markdown formatting helpers for tables, lists, and frontmatter."""

from __future__ import annotations

from datetime import datetime, timezone

import yaml


def generate_frontmatter(
    source: str,
    fmt: str,
    pages: int | None = None,
    slides: int | None = None,
    word_count: int = 0,
    warnings: list[str] | None = None,
) -> str:
    """Generate YAML frontmatter block."""
    data: dict = {
        "source": source,
        "format": fmt,
        "converted": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if pages is not None:
        data["pages"] = pages
    if slides is not None:
        data["slides"] = slides
    if word_count:
        data["word_count"] = word_count
    if warnings:
        data["warnings"] = warnings

    frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{frontmatter}---\n"


def format_table(headers: list[str], rows: list[list[str]], alignments: list[str] | None = None) -> str:
    """Convert a table to Markdown format.

    Args:
        headers: Column header strings.
        rows: List of row data (each row is a list of cell strings).
        alignments: Optional list of 'left', 'center', or 'right' per column.
    """
    if not headers and not rows:
        return ""

    num_cols = len(headers) if headers else (len(rows[0]) if rows else 0)
    if num_cols == 0:
        return ""

    # Ensure headers exist
    if not headers:
        headers = ["" for _ in range(num_cols)]

    # Build separator
    if alignments:
        sep_parts = []
        for i, align in enumerate(alignments):
            if i >= num_cols:
                break
            if align == "center":
                sep_parts.append(":---:")
            elif align == "right":
                sep_parts.append("---:")
            else:
                sep_parts.append("---")
        while len(sep_parts) < num_cols:
            sep_parts.append("---")
    else:
        sep_parts = ["---"] * num_cols

    lines = []
    lines.append("| " + " | ".join(h.replace("|", "\\|") for h in headers) + " |")
    lines.append("| " + " | ".join(sep_parts) + " |")
    for row in rows:
        # Pad row to match columns
        padded = list(row) + [""] * (num_cols - len(row))
        lines.append("| " + " | ".join(c.replace("|", "\\|") for c in padded[:num_cols]) + " |")

    return "\n".join(lines)


def clean_text(text: str) -> str:
    """Clean text of garbage characters and normalize whitespace."""
    # Remove null bytes and other control chars (keep newlines, tabs)
    cleaned = "".join(c for c in text if c == "\n" or c == "\t" or (ord(c) >= 32))
    return cleaned


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())
