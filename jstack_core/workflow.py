"""Session-scoped mode, deterministic routing, and auditable task contracts."""
import re
import uuid
from copy import deepcopy
from .config import BUDGETS, PLAYBOOKS, load
from .storage import JstackError, atomic_write, json_bytes, now, read_json, record_path


ROUTES = (
    ("prototype", r"\b(prototype|spike|proof of concept|throwaway)\b|프로토타입|시제품"),
    ("perf", r"\b(performance|latency|benchmark|slow|profil[ei]|optimi[sz]e)\b|성능|느려|최적화"),
    ("bug-fix", r"\b(bug|broken|crash|regression|fix|fails?|error)\b|버그|오류|고장"),
    ("refactor", r"\b(refactor|restructure|deduplicate|behavior.preserving)\b|리팩터|리팩토"),
    ("shipping", r"^\s*(ship|release|publish|deploy|push|merge)\b|^\s*(배포|출시)"),
    ("verification", r"^\s*(verify|validate|check|review|test|audit)\b|^\s*(검증|확인|테스트)"),
    ("lightweight", r"\b(typo|copy edit|padding|spacing|rename label)\b|오타|문구 수정|여백"),
)
RISK = r"\b(auth|authentication|authorization|payment|billing|migration|production|secret|permission|delete data)\b|인증|결제|마이그레이션|운영 데이터"


def route(task, explicit="auto"):
    if not isinstance(task, str) or not task.strip():
        raise JstackError("A nonempty task is required")
    if explicit != "auto":
        if explicit not in PLAYBOOKS:
            raise JstackError(f"Unknown playbook: {explicit}")
        return {"playbook": explicit, "confidence": "high", "reason": "Explicit selection"}
    matches = [name for name, pattern in ROUTES if re.search(pattern, task, re.I)]
    choice = matches[0] if matches else "feature"
    if choice == "lightweight" and re.search(RISK, task, re.I):
        choice = "feature"
    return {"playbook": choice, "confidence": "moderate" if len(matches) == 1 else "low",
            "reason": "Keyword heuristic; inspect task intent" if matches else "No specific signal; feature is a provisional default",
            "candidates": matches}


def mode(project, action, session_id=None, budget=None, host=None):
    cfg = load(project)
    if action == "on" and session_id is None:
        session_id = uuid.uuid4().hex[:12]
    if not session_id:
        raise JstackError("Use --session with the ID from this conversation; no global active session exists")
    path = record_path(project, "sessions", session_id)
    if action == "on":
        existing = read_json(path) if path.exists() else {}
        if host and existing.get("host") and existing["host"] != host:
            raise JstackError("Session host differs; create a new session for the other host")
        state = {"version": 1, "id": session_id, "active": True,
                 "host": host or existing.get("host", "generic"),
                 "budget": budget or existing.get("budget", cfg["budget"]),
                 "updated_at": now()}
        if state["budget"] not in BUDGETS:
            raise JstackError("Unknown budget")
        atomic_write(path, json_bytes(state))
        return state
    state = read_json(path)
    if action == "off":
        state.update(active=False, updated_at=now())
        atomic_write(path, json_bytes(state))
    return state


def plan(project, task, playbook="auto", budget=None, session_id=None, acceptance=None,
         children=0, reason=None, independent=False, agents_available=False):
    cfg = load(project)
    if session_id:
        session = read_json(record_path(project, "sessions", session_id))
        if not session.get("active"):
            raise JstackError("This session is off; re-enable it or omit --session for a one-off task")
        budget = budget or session["budget"]
    budget = budget or cfg["budget"]
    if budget not in BUDGETS:
        raise JstackError("Unknown budget")
    limits = deepcopy(BUDGETS[budget])
    ceiling = min(limits["max_children"], cfg["agents"]["max_children"]) if cfg["agents"]["enabled"] else 0
    if type(children) is not int or not 0 <= children <= ceiling:
        raise JstackError(f"Requested {children} child agents; effective ceiling is {ceiling}. No automatic budget escalation.")
    if children and not (reason and reason.strip() and independent and agents_available):
        raise JstackError("Fanout requires --reason, --independent, and --agents-available; otherwise stay sequential")
    if not acceptance or not all(isinstance(x, str) and x.strip() for x in acceptance):
        raise JstackError("Define at least one observable acceptance condition with --accept before implementation")
    selection = route(task, playbook)
    if children and selection["playbook"] == "lightweight":
        raise JstackError("The lightweight playbook does not use child agents")
    warnings = []
    if re.search(RISK, task, re.I):
        warnings.append("High-impact change: identify a rollback and verify affected boundaries. Budget remains unchanged.")
    if not cfg["verification"]["checks"]:
        warnings.append("No checks configured. Add meaningful checks; empty verification cannot pass.")
    result = {
        "version": 1, "id": uuid.uuid4().hex[:12], "created_at": now(), "task": task,
        "session": session_id, "route": selection, "budget": budget, "limits": limits,
        "acceptance": acceptance, "fanout": {"requested": children, "ceiling": ceiling,
        "reason": reason if children else None, "execution": "host-managed; this CLI never spawns agents"},
        "verification": cfg["verification"], "warnings": warnings,
    }
    atomic_write(record_path(project, "tasks", result["id"]), json_bytes(result))
    return result


def add_evidence(project, task_id, kind, claim, source, confidence):
    read_json(record_path(project, "tasks", task_id))
    if not claim.strip() or not source.strip():
        raise JstackError("Evidence needs both a claim and an inspectable source")
    result = {"id": uuid.uuid4().hex[:12], "task": task_id, "created_at": now(),
              "kind": kind, "claim": claim, "source": source, "confidence": confidence,
              "provenance": "operator-supplied; not independently verified by jstack"}
    atomic_write(record_path(project, "evidence", result["id"]), json_bytes(result))
    return result
