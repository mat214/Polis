#!/usr/bin/env python3
"""Entry point for Polis CLI."""

import sys
from pathlib import Path

# Ensure the polis package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from polis import main

if __name__ == "__main__":
  main()
