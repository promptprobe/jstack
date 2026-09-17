"""Project-local host adapters with owned-file updates and conflict checks."""
import re
import shutil
import sys
from pathlib import Path
from . import __version__
from .config import DEFAULT, load, validate
from .storage import JstackError, atomic_write, digest, json_bytes, read_json, safe_path

HOSTS = {"codex": (".agents/skills", "AGENTS.md"), "claude": (".claude/skills", "CLAUDE.md")}
START, END = "<!-- jstack:start -->", "<!-- jstack:end -->"
PATTERN = re.compile(re.escape(START) + r"[\s\S]*?" + re.escape(END))


def bundle_root():
    return Path(__file__).resolve().parent.parent


def block(text):
    return START + "\n" + text.rstrip() + "\n" + END


def instruction(host):
    invocation = "$jstack-mode" if host == "codex" else "/jstack-mode"
    return block(f"""## jstack
Use the project jstack skill when the user invokes `{invocation}` or asks for jstack.
Once activated, keep its active state and budget in this conversation until the
user turns it off. Default to skill-only operation, even with the helper installed.
Recorded sessions are opt-in; never adopt another session from disk.
After lost context, explain the gap and restart on explicit invocation.
Read `.jstack/config.json` and the installed jstack-mode skill when activated.
Respect existing project instructions and the user's scope. Merely installing
jstack does not activate it, authorize publication, or permit extra agents.
For explicitly requested recorded operation, read the skill's references/runner.md
and run `python3 .jstack/jstack.py` from the project root.
""")


def edit_block(project, name, replacement, prior):
    path = safe_path(project, name)
    old = path.read_bytes() if path.exists() else b""
    try:
        content = old.decode("utf-8")
    except UnicodeError as exc:
        raise JstackError(f"{name} is not UTF-8; no files changed") from exc
    matches = list(PATTERN.finditer(content))
    if content.count(START) != len(matches) or content.count(END) != len(matches) or len(matches) > 1:
        raise JstackError(f"Malformed jstack markers in {name}")
    if matches:
        matched = matches[0].group()
        if name not in prior or digest(matched.encode()) != prior[name]:
            raise JstackError(f"Locally modified or unowned jstack block in {name}; preserve it and resolve manually")
        return PATTERN.sub(lambda _: replacement or "", content).encode()
    if name in prior:
        raise JstackError(f"Managed jstack block missing from {name}; resolve manually")
    return (content + ("\n\n" if content else "") + replacement + "\n").encode() if replacement else old


def apply_changes(project, changes):
    """Rollback completed writes on ordinary I/O failure. Not crash-transactional."""
    before = {}
    for name in changes:
        path = safe_path(project, name)
        if path.exists() and not path.is_file():
            raise JstackError(f"Expected a regular file: {name}")
        before[name] = path.read_bytes() if path.exists() else None
    changed = []
    try:
        for name, data in changes.items():
            if before[name] == data:
                continue
            path = safe_path(project, name)
            changed.append(name)
            if data is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, data)
    except OSError:
        for name in reversed(changed):
            path = safe_path(project, name)
            if before[name] is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, before[name])
        raise
    return changed


def manifest(project):
    path = safe_path(project, ".jstack/install.json")
    if not path.exists():
        return {"version": 1, "hosts": [], "files": {}, "blocks": {}}
    value = read_json(path)
    if not isinstance(value, dict) or value.get("version") != 1 or not all(isinstance(value.get(k), dict) for k in ("files", "blocks")):
        raise JstackError("Invalid installation manifest")
    if not isinstance(value.get("hosts"), list) or any(h not in HOSTS for h in value["hosts"]):
        raise JstackError("Invalid host list in installation manifest")
    for name in value["files"]:
        if not (name.startswith(".jstack/jstack_core/") or name == ".jstack/jstack.py" or
                any(name.startswith(prefix + "/jstack-mode/") for prefix, _ in HOSTS.values())):
            raise JstackError(f"Unexpected managed file in manifest: {name}")
        safe_path(project, name)
    if set(value["blocks"]) - {"AGENTS.md", "CLAUDE.md", ".gitignore"}:
        raise JstackError("Unexpected instruction file in manifest")
    return value


def owned_files_clean(project, old):
    for name, expected in old["files"].items():
        path = safe_path(project, name)
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise JstackError(f"Managed file changed or missing: {name}. Save your edits and resolve before setup/uninstall.")


def setup(project, host="both", dry_run=False):
    source = bundle_root()
    if not (source / "skills/jstack-mode/SKILL.md").is_file():
        raise JstackError("Run setup from a complete jstack checkout, not an installed runtime")
    old = manifest(project)
    owned_files_clean(project, old)
    selected = list(HOSTS) if host == "both" else [host]
    hosts = sorted(set(old["hosts"] + selected))
    files = {".jstack/jstack.py": (source / "jstack.py").read_bytes()}
    for path in sorted((source / "jstack_core").glob("*.py")):
        files[f".jstack/jstack_core/{path.name}"] = path.read_bytes()
    for target_host in hosts:
        prefix = HOSTS[target_host][0] + "/jstack-mode/"
        for path in sorted((source / "skills/jstack-mode").rglob("*")):
            if path.is_file():
                files[prefix + path.relative_to(source / "skills/jstack-mode").as_posix()] = path.read_bytes()
        files[prefix + "references/host.md"] = (source / f"adapters/{target_host}.md").read_bytes()
    for name, data in files.items():
        path = safe_path(project, name)
        if path.exists() and name not in old["files"]:
            raise JstackError(f"Unowned file already exists: {name}; setup will not overwrite it")
    changes = {name: None for name in set(old["files"]) - set(files)}
    changes.update(files)
    blocks = dict(old["blocks"])
    for target_host in hosts:
        name = HOSTS[target_host][1]
        contents = instruction(target_host)
        changes[name] = edit_block(project, name, contents, old["blocks"])
        blocks[name] = digest(contents.encode())
    ignore = block("# Session state and captured output remain local.\n.jstack/local/\n.jstack/write.lock\n.jstack/**/__pycache__/")
    changes[".gitignore"] = edit_block(project, ".gitignore", ignore, old["blocks"])
    blocks[".gitignore"] = digest(ignore.encode())
    cfg = safe_path(project, ".jstack/config.json")
    if cfg.exists():
        validate(read_json(cfg))
    else:
        changes[".jstack/config.json"] = json_bytes(DEFAULT)
    new = {"version": 1, "release": __version__, "hosts": hosts,
           "files": {name: digest(data) for name, data in files.items()}, "blocks": blocks}
    changes[".jstack/install.json"] = json_bytes(new)
    if dry_run:
        return {"dry_run": True, "hosts": hosts, "paths": sorted(changes)}
    changed = apply_changes(project, changes)
    return {"release": __version__, "hosts": hosts, "changed": changed,
            "next": "Configure checks in .jstack/config.json, then invoke jstack-mode in your host"}


def uninstall(project, dry_run=False):
    old = manifest(project)
    if not old["files"]:
        raise JstackError("No managed jstack installation found")
    owned_files_clean(project, old)
    changes = {name: None for name in old["files"]}
    for name in old["blocks"]:
        if name != ".gitignore":
            changes[name] = edit_block(project, name, None, old["blocks"])
    # Keep ownership of the privacy block so a later reinstall is safe.
    changes[".jstack/install.json"] = json_bytes({"version": 1, "hosts": [], "files": {},
                                                  "blocks": {".gitignore": old["blocks"][".gitignore"]}})
    if not dry_run:
        apply_changes(project, changes)
    return {"dry_run": dry_run, "removed": sorted(changes),
            "preserved": [".jstack/config.json", ".jstack/local/", ".gitignore privacy block", "user-added files"]}


def doctor(project):
    cfg = load(project)
    old = manifest(project)
    problems = []
    try:
        owned_files_clean(project, old)
        for name in old["blocks"]:
            edit_block(project, name, None, old["blocks"])
    except JstackError as exc:
        problems.append(str(exc))
    if not old["files"]:
        problems.append("No managed installation found")
    if not any(c.get("required", True) for c in cfg["verification"]["checks"]):
        problems.append("No required verification checks configured")
    return {"ok": not problems, "release": __version__, "python": sys.version.split()[0],
            "hosts_installed": old["hosts"], "host_binaries": {h: shutil.which(h) for h in HOSTS},
            "problems": problems, "note": "File/config inspection only; this does not test live host behavior"}
