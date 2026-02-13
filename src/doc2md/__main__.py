"""Entry point for doc2md MCP server: python -m doc2md"""

from __future__ import annotations

import logging
import os
import sys


def main():
    """Run the doc2md MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    from doc2md.server import mcp

    transport = os.environ.get("TRANSPORT", "stdio").lower()
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
