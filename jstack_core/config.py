"""Strict project configuration; no executable discovery or network access."""
from copy import deepcopy
from .storage import JstackError, read_json, safe_path

PLAYBOOKS = ("feature", "bug-fix", "refactor", "perf", "prototype", "verification", "shipping", "lightweight")
BUDGETS = {
    "cheap": {"investigation_passes": 1, "repair_attempts": 1, "max_children": 0, "context_files_hint": 4},
    "normal": {"investigation_passes": 2, "repair_attempts": 2, "max_children": 1, "context_files_hint": 10},
    "deep": {"investigation_passes": 4, "repair_attempts": 3, "max_children": 3, "context_files_hint": 20},
}
DEFAULT = {
    "version": 1,
    "budget": "normal",
    "agents": {"enabled": False, "max_children": 1},
    "verification": {"timeout_seconds": 120, "checks": []},
}


def object_keys(value, allowed, label):
    if not isinstance(value, dict):
        raise JstackError(f"{label} must be an object")
    unknown = set(value) - set(allowed)
    if unknown:
        raise JstackError(f"Unknown {label} fields: {', '.join(sorted(unknown))}")


def integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise JstackError(f"{label} must be an integer from {low} to {high}")


def validate(raw):
    object_keys(raw, DEFAULT, "config")
    if type(raw.get("version")) is not int or raw["version"] != 1:
        raise JstackError("config.version must be 1")
    result = deepcopy(DEFAULT)
    if "budget" in raw:
        if not isinstance(raw["budget"], str) or raw["budget"] not in BUDGETS:
            raise JstackError("config.budget must be cheap, normal or deep")
        result["budget"] = raw["budget"]
    if "agents" in raw:
        agents = raw["agents"]
        object_keys(agents, ("enabled", "max_children"), "agents")
        if "enabled" in agents and type(agents["enabled"]) is not bool:
            raise JstackError("agents.enabled must be boolean")
        if "max_children" in agents:
            integer(agents["max_children"], 0, 3, "agents.max_children")
        result["agents"].update(agents)
    if "verification" in raw:
        ver = raw["verification"]
        object_keys(ver, ("timeout_seconds", "checks"), "verification")
        if "timeout_seconds" in ver:
            integer(ver["timeout_seconds"], 1, 3600, "verification.timeout_seconds")
        checks = ver.get("checks", [])
        if not isinstance(checks, list):
            raise JstackError("verification.checks must be an array")
        seen = set()
        for check in checks:
            object_keys(check, ("name", "argv", "required", "timeout_seconds"), "check")
            name = check.get("name")
            if not isinstance(name, str) or not name.strip() or len(name) > 80 or name in seen:
                raise JstackError("Checks need unique, nonempty names of at most 80 characters")
            seen.add(name)
            argv = check.get("argv")
            if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x and "\0" not in x for x in argv):
                raise JstackError(f"{name}: argv must be a nonempty array of nonempty strings")
            if "required" in check and type(check["required"]) is not bool:
                raise JstackError(f"{name}: required must be boolean")
            if "timeout_seconds" in check:
                integer(check["timeout_seconds"], 1, 3600, f"{name}.timeout_seconds")
        result["verification"].update(ver)
    return result


def load(project):
    return validate(read_json(safe_path(project, ".jstack/config.json")))
