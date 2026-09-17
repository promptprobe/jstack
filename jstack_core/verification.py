"""Execute explicit argv checks and keep local evidence tied to source content."""
import os
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from .config import load
from .storage import JstackError, atomic_write, digest, json_bytes, now, read_json, record_path, safe_path


def git(project, *args):
    try:
        result = subprocess.run(["git", "-C", str(project), *args], capture_output=True, timeout=20)
        return result.stdout if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def snapshot(project):
    """Hash Git-visible paths, contents and modes; never read ignored files or link targets."""
    top = git(project, "rev-parse", "--show-toplevel")
    if top is None or Path(os.fsdecode(top).strip()).resolve() != project.resolve():
        return {"available": False, "reason": "Verification freshness requires setup at a Git repository root"}
    paths = git(project, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    head = git(project, "rev-parse", "HEAD")
    if paths is None:
        return {"available": False, "reason": "Could not enumerate Git-visible source"}
    entries = []
    try:
        for raw in sorted(set(paths.split(b"\0")) - {b""}):
            name = os.fsdecode(raw)
            if name.startswith(".jstack/local/") or name == ".jstack/write.lock":
                continue
            path = project / name
            if any(parent.is_symlink() for parent in path.parents if parent != project and project in parent.parents):
                return {"available": False, "reason": f"Symlink ancestor prevents source fingerprint: {name}"}
            if path.is_symlink():
                value = "link:" + os.readlink(path)
            elif not path.exists():
                value = "deleted"
            elif path.is_dir():
                return {"available": False, "reason": f"Submodule/directory content is unsupported: {name}"}
            else:
                value = digest(path.read_bytes())
            entries.append([name, value, (path.lstat().st_mode & 0o777) if path.exists() or path.is_symlink() else None])
    except OSError as exc:
        return {"available": False, "reason": f"Could not fingerprint source: {exc}"}
    return {"available": True, "fingerprint": digest(json_bytes(entries)),
            "head": head.decode().strip() if head else None, "files": len(entries),
            "scope": "Git-visible files excluding .jstack/local and lock; ignored files, link targets and external services are outside scope"}


def records(project, kind, task_id):
    folder = safe_path(project, f".jstack/local/{kind}")
    result = []
    if folder.exists():
        for path in sorted(folder.glob("*.json")):
            safe_path(project, path.relative_to(project))
            item = read_json(path)
            if item.get("task") == task_id:
                result.append(item)
    return sorted(result, key=lambda x: x["created_at"])


def execute(check, project, timeout):
    argv = [sys.executable if value == "{python}" else value for value in check["argv"]]
    start = time.monotonic()
    result = {"name": check["name"], "argv": argv, "required": check.get("required", True),
              "started_at": now(), "timeout_seconds": timeout}
    # Spool command output to disk, then retain only a bounded tail in the receipt.
    with tempfile.TemporaryFile() as output:
        try:
            process = subprocess.Popen(argv, cwd=project, stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=(os.name == "posix"))
            try:
                code = process.wait(timeout=timeout)
                status = "passed" if code == 0 else "failed"
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                code = process.wait()
                status = "timeout"
        except OSError as exc:
            output.write(str(exc).encode("utf-8"))
            code, status = None, "error"
        output.seek(0, os.SEEK_END)
        size = output.tell()
        output.seek(max(0, size - 16000))
        result.update(status=status, exit_code=code, duration_seconds=round(time.monotonic() - start, 3),
                      output_tail=output.read().decode("utf-8", errors="replace"), output_truncated=size > 16000)
    return result


def verify(project, task_id, phase="final"):
    task = read_json(record_path(project, "tasks", task_id))
    cfg = load(project)
    if cfg["verification"] != task["verification"]:
        raise JstackError("Verification config changed since planning. Create a new task contract before running checks.")
    prior = [r for r in records(project, "runs", task_id) if r["phase"] == phase]
    ceiling = 1 if phase == "baseline" else 1 + task["limits"]["repair_attempts"]
    if len(prior) >= ceiling:
        raise JstackError(f"{phase} verification allowance exhausted ({ceiling} runs). Report evidence and choose the next scope with the user.")
    before = snapshot(project)
    checks = [execute(check, project, check.get("timeout_seconds", cfg["verification"]["timeout_seconds"]))
              for check in cfg["verification"]["checks"]]
    after = snapshot(project)
    required = [c for c in checks if c["required"]]
    stable = before.get("available") and after.get("available") and before["fingerprint"] == after["fingerprint"]
    passed = bool(required) and all(c["status"] == "passed" for c in required) and bool(stable)
    result = {"version": 1, "id": uuid.uuid4().hex[:12], "task": task_id, "phase": phase,
              "created_at": now(), "checks": checks, "source_before": before, "source_after": after,
              "source_stable": bool(stable), "local_checks_passed": passed,
              "meaning": "Local command outcomes only; acceptance, CI and deployment require separate evidence"}
    atomic_write(record_path(project, "runs", result["id"]), json_bytes(result))
    return result


def report(project, task_id):
    task = read_json(record_path(project, "tasks", task_id))
    runs = records(project, "runs", task_id)
    final = [r for r in runs if r["phase"] == "final"]
    latest = final[-1] if final else None
    current = snapshot(project)
    config_matches = load(project)["verification"] == task["verification"]
    fresh = bool(config_matches and latest and current.get("available") and latest["source_after"].get("available")
                 and current["fingerprint"] == latest["source_after"]["fingerprint"])
    if latest is None:
        status = "unverified"
    elif not fresh:
        status = "stale_or_unknown"
    elif latest["local_checks_passed"]:
        status = "local_checks_passed"
    else:
        status = "local_checks_failed_or_incomplete"
    return {"task": task, "status": status, "fresh": fresh, "current_source": current, "runs": runs,
            "evidence": records(project, "evidence", task_id),
            "acceptance_status": "not automatically evaluated",
            "ci_status": "unknown unless independently checked", "deployment_status": "unknown unless independently checked"}


def markdown(value):
    task = value["task"]
    lines = [f"# jstack evidence — {task['id']}", "", task["task"], "",
             f"**Status:** {value['status']}", f"**Budget / playbook:** {task['budget']} / {task['route']['playbook']}",
             f"**Acceptance:** {value['acceptance_status']}", f"**CI:** {value['ci_status']}",
             f"**Deployment:** {value['deployment_status']}", "", "## Acceptance conditions", ""]
    lines.extend(f"- {item}" for item in task["acceptance"])
    lines.extend(["", "## Executed local checks", ""])
    for run in value["runs"]:
        lines.append(f"- {run['id']} ({run['phase']}): source stable = {run['source_stable']}")
        for check in run["checks"]:
            lines.append(f"  - {check['name']}: {check['status']} (exit {check['exit_code']}, {check['duration_seconds']}s)")
    if not value["runs"]:
        lines.append("No checks executed.")
    lines.extend(["", "## Supplied observations", ""])
    for item in value["evidence"]:
        lines.append(f"- [{item['confidence']}] {item['kind']}: {item['claim']} — {item['source']} ({item['provenance']})")
    if not value["evidence"]:
        lines.append("None supplied.")
    lines.extend(["", "Local check results do not establish acceptance, successful CI, or a working deployment.", ""])
    return "\n".join(lines)
