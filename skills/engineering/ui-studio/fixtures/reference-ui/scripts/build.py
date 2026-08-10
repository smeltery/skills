#!/usr/bin/env python3
"""Create the disposable fixture's static production output."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist"
if OUTPUT.exists():
    shutil.rmtree(OUTPUT)
shutil.copytree(ROOT / "public", OUTPUT)
print(f"Built {OUTPUT}")
