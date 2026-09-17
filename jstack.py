#!/usr/bin/env python3
"""Run jstack from a checkout or a project-local installation."""
import sys
sys.dont_write_bytecode = True
from jstack_core.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
