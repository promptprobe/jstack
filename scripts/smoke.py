#!/usr/bin/env python3
"""Exercise both adapters and the installed CLI in an isolated real Git project."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def smoke():
    with tempfile.TemporaryDirectory(prefix="jstack smoke ") as directory:
        project = Path(directory).resolve()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        subprocess.run(["git", "init", "-q", str(project)], check=True, env=env)
        (project / "AGENTS.md").write_text("Preserve this project's rules.\n", encoding="utf-8")
        (project / "cart.py").write_text("def add(items, item):\n    return items + [item, item]\n", encoding="utf-8")
        (project / "check.py").write_text("from cart import add\nassert add([], 'apple') == ['apple']\n", encoding="utf-8")

        def call(script, *args, expected=0, raw=False):
            result = subprocess.run([sys.executable, str(script), *args], cwd=project, env=env, capture_output=True, text=True)
            if result.returncode != expected:
                raise AssertionError(f"{args}: expected exit {expected}, got {result.returncode}\n{result.stdout}\n{result.stderr}")
            return result.stdout if raw else json.loads(result.stdout)

        call(ROOT / "jstack.py", "setup", "--host", "both")
        cli = project / ".jstack/jstack.py"
        cfg = json.loads((project / ".jstack/config.json").read_text(encoding="utf-8"))
        cfg["verification"]["checks"] = [{"name": "single-add", "argv": ["{python}", "check.py"]}]
        (project / ".jstack/config.json").write_text(json.dumps(cfg), encoding="utf-8")
        call(cli, "doctor")
        codex = call(cli, "mode", "on", "--host", "codex", "--budget", "cheap")
        claude = call(cli, "mode", "on", "--host", "claude", "--budget", "normal")
        assert codex["id"] != claude["id"]
        task = call(cli, "plan", "Fix duplicate cart additions", "--session", codex["id"],
                    "--accept", "One addition produces one item")
        before = call(cli, "verify", "--task", task["id"], "--phase", "baseline", expected=1)
        assert before["checks"][0]["status"] == "failed"
        (project / "cart.py").write_text("def add(items, item):\n    return items + [item]\n", encoding="utf-8")
        after = call(cli, "verify", "--task", task["id"])
        assert after["local_checks_passed"]
        call(cli, "evidence", "--task", task["id"], "--kind", "runtime", "--claim", "Single-add fixture passes",
             "--source", "check.py", "--confidence", "high")
        report = call(cli, "report", "--task", task["id"], "--format", "json")
        assert report["status"] == "local_checks_passed"
        assert report["acceptance_status"] == "not automatically evaluated"
        assert ".jstack/local/" in subprocess.run(["git", "check-ignore", ".jstack/local/tasks/example.json"],
                                                   cwd=project, capture_output=True, text=True).stdout
        # A subsequent edit must invalidate the earlier result.
        (project / "cart.py").write_text("def add(items, item):\n    return items\n", encoding="utf-8")
        assert call(cli, "report", "--task", task["id"], "--format", "json")["status"] == "stale_or_unknown"
        call(cli, "mode", "off", "--session", codex["id"])
        assert call(cli, "mode", "status", "--session", claude["id"])["active"]
        call(cli, "uninstall")
        assert (project / "AGENTS.md").read_text(encoding="utf-8").startswith("Preserve this project's rules.")
        call(ROOT / "jstack.py", "setup", "--host", "both")
        call(cli, "doctor")
        return {"result": "passed", "adapters": ["codex", "claude"],
                "flow": "setup -> separate sessions -> failing baseline -> fix -> passing check -> stale detection -> off -> uninstall -> reinstall",
                "live_host_model_execution": False}


if __name__ == "__main__":
    print(json.dumps(smoke(), indent=2))
