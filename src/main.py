"""
AutoJob entry point.
Run with:  python -m src.main
"""
import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gui.app import run_app


if __name__ == "__main__":
    run_app()
