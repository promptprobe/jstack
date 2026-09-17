#!/usr/bin/env python3
"""Dependency-free repository validation; no model calls or remote writes."""
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jstack_core.config import PLAYBOOKS, validate


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ is required")
    for path in ROOT.rglob("*.py"):
        if ".git" not in path.parts:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in (ROOT / "examples").glob("*.json"):
        validate(json.loads(path.read_text(encoding="utf-8")))
    json.loads((ROOT / "schemas/config.schema.json").read_text(encoding="utf-8"))
    skill = ROOT / "skills/jstack-mode/SKILL.md"
    content = skill.read_text(encoding="utf-8")
    assert content.startswith("---\nname: jstack-mode\ndescription: ")
    assert len(content.encode()) < 9000, "Keep the entry skill small; use on-demand references"
    for name in PLAYBOOKS:
        assert (skill.parent / f"references/playbooks/{name}.md").is_file()
    for doc in ROOT.rglob("*.md"):
        if ".git" in doc.parts:
            continue
        for link in re.findall(r"\]\(([^)\s]+)\)", doc.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = link.split("#", 1)[0]
            assert (doc.parent / target).exists(), f"Broken local link: {doc.relative_to(ROOT)} -> {target}"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, env=env, check=True)
    subprocess.run([sys.executable, "scripts/smoke.py"], cwd=ROOT, env=env, check=True)
    print(f"Validated Python syntax, example configs, skill layout ({len(content.encode())} bytes), local links, tests and installed CLI smoke flow.")


if __name__ == "__main__":
    main()
