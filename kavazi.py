#!/usr/bin/env python3
"""Convenient checkout entry point for the self-contained release tool."""
from pathlib import Path
import runpy
import sys

scripts = Path(__file__).resolve().parent / "skills/kavazi-method/scripts"
sys.path.insert(0, str(scripts))
runpy.run_path(str(scripts / "kavazi.py"), run_name="__main__")
