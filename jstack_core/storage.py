"""Small filesystem boundary shared by setup and task records."""
import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class JstackError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise JstackError(f"Cannot read JSON at {path}: {exc}") from exc


def safe_path(root, relative):
    """Refuse symlink ancestors, including links that currently point inside root."""
    root = Path(root).resolve()
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise JstackError(f"Expected a project-relative path: {relative}")
    current = root
    for part in rel.parts:
        current /= part
        if current.is_symlink():
            raise JstackError(f"Refusing managed symlink: {current}")
    return current


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".jstack-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def record_path(project, kind, record_id):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", record_id):
        raise JstackError("Record IDs must use 1–80 letters, digits, underscores or hyphens")
    return safe_path(project, f".jstack/local/{kind}/{record_id}.json")


@contextmanager
def project_lock(project):
    path = safe_path(project, ".jstack/write.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise JstackError("Another jstack writer holds .jstack/write.lock. If a process crashed, confirm it stopped before removing the lock.") from exc
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        path.unlink(missing_ok=True)
