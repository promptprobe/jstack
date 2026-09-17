"""Explicit commands; importing this module never performs I/O."""
import argparse
import json
import sys
from pathlib import Path
from . import __version__
from . import install, verification, workflow
from .config import BUDGETS, PLAYBOOKS
from .storage import JstackError, project_lock


def parser():
    root = argparse.ArgumentParser(prog="jstack", description="Local, cost-aware coding workflow contracts and evidence")
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("setup", "uninstall", "doctor", "mode", "plan", "verify", "report", "evidence", "route"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--project", type=Path, default=Path.cwd(), help="Project root (default: current directory)")
        if name in ("setup", "uninstall"):
            cmd.add_argument("--dry-run", action="store_true")
        if name == "setup":
            cmd.add_argument("--host", choices=("codex", "claude", "both"), default="both")
        elif name == "mode":
            cmd.add_argument("action", choices=("on", "off", "status"))
            cmd.add_argument("--session")
            cmd.add_argument("--budget", choices=BUDGETS)
            cmd.add_argument("--host", choices=("codex", "claude", "generic"))
        elif name in ("route", "plan"):
            cmd.add_argument("task")
            cmd.add_argument("--playbook", choices=("auto", *PLAYBOOKS), default="auto")
            if name == "plan":
                cmd.add_argument("--budget", choices=BUDGETS)
                cmd.add_argument("--session")
                cmd.add_argument("--accept", action="append", required=True)
                cmd.add_argument("--agents", type=int, default=0)
                cmd.add_argument("--reason")
                cmd.add_argument("--independent", action="store_true")
                cmd.add_argument("--agents-available", action="store_true")
        elif name in ("verify", "report", "evidence"):
            cmd.add_argument("--task", required=True)
            if name == "verify":
                cmd.add_argument("--phase", choices=("baseline", "final"), default="final")
            elif name == "report":
                cmd.add_argument("--format", choices=("json", "markdown"), default="markdown")
            else:
                cmd.add_argument("--kind", choices=("source", "runtime", "ci", "deployment", "inference"), required=True)
                cmd.add_argument("--claim", required=True)
                cmd.add_argument("--source", required=True)
                cmd.add_argument("--confidence", choices=("high", "moderate", "low", "unknown"), required=True)
    return root


def dispatch(args):
    project = args.project.resolve()
    name = args.command
    if name == "route":
        return workflow.route(args.task, args.playbook), 0
    if not project.is_dir():
        raise JstackError(f"Project directory does not exist: {project}")
    if name == "doctor":
        value = install.doctor(project)
        return value, 0 if value["ok"] else 1
    if name == "report":
        value = verification.report(project, args.task)
        return verification.markdown(value) if args.format == "markdown" else value, 0
    if name == "mode" and args.action == "status":
        return workflow.mode(project, args.action, args.session), 0
    # Dry runs are read-only, including absence of a lock or directories.
    if name in ("setup", "uninstall") and args.dry_run:
        value = install.setup(project, args.host, True) if name == "setup" else install.uninstall(project, True)
        return value, 0
    with project_lock(project):
        if name == "setup":
            return install.setup(project, args.host), 0
        if name == "uninstall":
            return install.uninstall(project), 0
        if name == "mode":
            return workflow.mode(project, args.action, args.session, args.budget, args.host), 0
        if name == "plan":
            return workflow.plan(project, args.task, args.playbook, args.budget, args.session,
                                 args.accept, args.agents, args.reason, args.independent, args.agents_available), 0
        if name == "evidence":
            return workflow.add_evidence(project, args.task, args.kind, args.claim, args.source, args.confidence), 0
        if name == "verify":
            value = verification.verify(project, args.task, args.phase)
            return value, 0 if value["local_checks_passed"] else 1
    raise JstackError(f"Unsupported command: {name}")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        value, code = dispatch(args)
        print(value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False))
        return code
    except (JstackError, OSError, UnicodeError) as exc:
        print(f"jstack: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
