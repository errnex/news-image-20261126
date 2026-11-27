#!/usr/bin/env python3
"""Entry point: copy the repository's entry.png to the output directory.

Reads MAKEFUN_OUTPUT_DIR (default /output) and copies entry.png byte for
byte to <out>/entry.png. Standard library only, no network, deterministic.
"""
import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
