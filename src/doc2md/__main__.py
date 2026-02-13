"""Entry point for doc2md MCP server: python -m doc2md"""

from __future__ import annotations

import asyncio
import logging
import os
import sys


def main():
    """Run the doc2md MCP server."""
    # Configure logging to stderr to avoid corrupting stdio transport
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    transport = os.environ.get("TRANSPORT", "stdio").lower()
    port = int(os.environ.get("PORT", "3000"))

    if transport == "sse":
        from doc2md.server import run_sse

        asyncio.run(run_sse(port=port))
    else:
        from doc2md.server import run_stdio

        asyncio.run(run_stdio())


if __name__ == "__main__":
    main()
