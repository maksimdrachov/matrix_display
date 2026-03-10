"""Helpers for loading vendored dependencies."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_stupidartnet_on_path() -> None:
    """Expose the vendored stupidArtnet package when running from source."""
    try:
        import stupidArtnet  # noqa: F401
        return
    except ImportError:
        vendor_root = Path(__file__).resolve().parents[2] / "vendor" / "stupidArtnet"
        if not vendor_root.exists():
            raise
        sys.path.insert(0, str(vendor_root))
        import stupidArtnet  # noqa: F401
