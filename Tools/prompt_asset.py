#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
SRC_TEXT = str(SRC)
if SRC_TEXT in sys.path:
    sys.path.remove(SRC_TEXT)
sys.path.insert(0, SRC_TEXT)

from rkp.prompt_asset import *  # noqa: F403
from rkp.prompt_asset import main


if __name__ == "__main__":
    sys.exit(main())
