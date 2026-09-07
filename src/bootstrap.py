"""Ensure src/ is on sys.path for pipeline imports."""

import sys
from pathlib import Path


def setup_src_path() -> None:
    """Add the src directory to sys.path if not already present."""
    src = Path(__file__).resolve().parent
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
