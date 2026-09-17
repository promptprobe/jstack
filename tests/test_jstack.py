import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from jstack_core import config, install, verification, workflow
from jstack_core.cli import main
from jstack_core.storage import JstackError, atomic_write, json_bytes, project_lock, read_json, record_path

ROOT = Path(__file__).resolve().parents[1]


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="jstack test ")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.write("check.py", "print('behavior checked')\n")

    def write(self, name, content):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def ready(self, checks=None, budget="normal", agents=False):
        install.setup(self.project)
        cfg = deepcopy(config.DEFAULT)
        cfg["budget"] = budget
        cfg["agents"] = {"enabled": agents, "max_children": 3}
        cfg["verification"]["checks"] = checks if checks is not None else [{"name": "behavior", "argv": ["{python}", "check.py"]}]
        self.write(".jstack/config.json", json.dumps(cfg))
        return cfg

    def task(self, **kwargs):
        return workflow.plan(self.project, "Implement one useful behavior", acceptance=["Fixture shows expected behavior"], **kwargs)

    def tree(self):
        return {p.relative_to(self.project).as_posix(): p.read_bytes() for p in self.project.rglob("*") if p.is_file() and ".git" not in p.parts}


class InstallTests(ProjectTest):
    def test_both_host_layouts_and_idempotence(self):
        self.write("AGENTS.md", "Keep my coding rules.\n")
        self.write("CLAUDE.md", "Keep my Claude rules.\n")
        install.setup(self.project)
        before = self.tree()
        self.assertEqual([], install.setup(self.project)["changed"])
        self.assertEqual(before, self.tree())
        for path, host in ((".agents", "Codex"), (".claude", "Claude Code")):
            base = self.project / path / "skills/jstack-mode"
            self.assertTrue((base / "SKILL.md").is_file())
            self.assertIn(host, (base / "references/host.md").read_text())
        self.assertTrue((self.project / "AGENTS.md").read_text().startswith("Keep my coding rules.\n"))

    def test_incremental_host_install(self):
        install.setup(self.project, "codex")
        self.assertFalse((self.project / ".claude").exists())
        install.setup(self.project, "claude")
        self.assertEqual(["claude", "codex"], install.manifest(self.project)["hosts"])

    def test_dry_run_has_no_side_effects(self):
        before = self.tree()
        self.assertEqual(0, self.cli("setup", "--dry-run"))
        self.assertEqual(before, self.tree())
        self.assertFalse((self.project / ".jstack").exists())

    def cli(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main([*args, "--project", str(self.project)])

    def test_unowned_collision_changes_nothing(self):
        self.write(".claude/skills/jstack-mode/SKILL.md", "my own skill")
        before = self.tree()
        with self.assertRaises(JstackError):
            install.setup(self.project)
        self.assertEqual(before, self.tree())

    def test_modified_runtime_and_block_are_preserved(self):
        install.setup(self.project)
        self.write(".jstack/jstack.py", "user-edited runtime")
        before = self.tree()
        for operation in (install.setup, install.uninstall):
            with self.assertRaises(JstackError):
                operation(self.project)
            self.assertEqual(before, self.tree())

    def test_modified_instruction_block_rejected(self):
        install.setup(self.project)
        path = self.project / "AGENTS.md"
        path.write_text(path.read_text().replace("## jstack", "## custom jstack"))
        before = self.tree()
        with self.assertRaises(JstackError):
            install.setup(self.project)
        self.assertEqual(before, self.tree())

    def test_uninstall_reinstall_preserves_user_data(self):
        self.ready()
        session = workflow.mode(self.project, "on")
        self.write(".agents/skills/jstack-mode/my-notes.md", "mine")
        install.uninstall(self.project)
        self.assertTrue(record_path(self.project, "sessions", session["id"]).exists())
        self.assertEqual("mine", (self.project / ".agents/skills/jstack-mode/my-notes.md").read_text())
        self.assertNotIn("jstack:start", (self.project / "AGENTS.md").read_text())
        install.setup(self.project)
        self.assertTrue(install.doctor(self.project)["ok"])

    def test_setup_preserves_custom_config(self):
        cfg = self.ready(budget="cheap")
        install.setup(self.project)
        self.assertEqual(cfg, config.load(self.project))

    @unittest.skipIf(os.name == "nt", "Symlink privilege varies on Windows")
    def test_symlink_ancestor_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.project / ".agents").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(JstackError):
                install.setup(self.project, "codex")
            self.assertEqual([], list(Path(outside).iterdir()))

    def test_doctor_does_not_claim_empty_checks_work(self):
        install.setup(self.project)
        self.assertFalse(install.doctor(self.project)["ok"])

    def test_installed_cli_runs_without_checkout(self):
        self.ready()
        result = subprocess.run([sys.executable, str(self.project / ".jstack/jstack.py"), "doctor"], cwd=self.project, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_write_failure_rolls_back(self):
        self.write("a.txt", "original")
        real_write = install.atomic_write
        def failing(path, data):
            if path.name == "b.txt":
                raise OSError("simulated disk failure")
            real_write(path, data)
        with patch.object(install, "atomic_write", failing), self.assertRaises(OSError):
            install.apply_changes(self.project, {"a.txt": b"new", "b.txt": b"other"})
        self.assertEqual("original", (self.project / "a.txt").read_text())


class ConfigTests(unittest.TestCase):
    def test_defaults_and_strict_boundary(self):
        self.assertEqual(config.DEFAULT, config.validate({"version": 1}))
        invalid = [[], {"version": True}, {"version": 2}, {"version": 1, "buget": "cheap"},
                   {"version": 1, "budget": []}, {"version": 1, "agents": {"enabled": "yes"}},
                   {"version": 1, "agents": {"max_children": True}},
                   {"version": 1, "verification": {"timeout_seconds": 0}},
                   {"version": 1, "verification": {"checks": [{"name": "x", "argv": "echo x"}]}},
                   {"version": 1, "verification": {"checks": [{"name": "x", "argv": ["echo"], "required": "false"}]}}]
        for raw in invalid:
            with self.subTest(raw=raw), self.assertRaises(JstackError):
                config.validate(raw)

    def test_duplicate_check_names_rejected(self):
        check = {"name": "same", "argv": ["echo", "ok"]}
        with self.assertRaises(JstackError):
            config.validate({"version": 1, "verification": {"checks": [check, check]}})


class WorkflowTests(ProjectTest):
    def test_routes_cover_all_playbooks(self):
        cases = {"feature": "Add a cart", "bug-fix": "Fix reconnect bug", "refactor": "Refactor cart module",
                 "perf": "Reduce slow queries", "prototype": "Prototype an editor", "verification": "Verify the release",
                 "shipping": "Publish the release", "lightweight": "Correct a typo"}
        for expected, task in cases.items():
            self.assertEqual(expected, workflow.route(task)["playbook"])
        self.assertEqual("bug-fix", workflow.route("Fix a slow crashing loop", "bug-fix")["playbook"])
        self.assertEqual("low", workflow.route("Fix a slow crashing loop")["confidence"])

    def test_korean_and_ambiguous_input(self):
        self.assertEqual("bug-fix", workflow.route("로그인 버그 수정")["playbook"])
        self.assertEqual("low", workflow.route("Work on this")["confidence"])
        with self.assertRaises(JstackError):
            workflow.route("   ")

    def test_independent_sticky_sessions_and_opt_out(self):
        self.ready()
        a = workflow.mode(self.project, "on", budget="cheap", host="codex")
        b = workflow.mode(self.project, "on", budget="deep", host="claude")
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual("cheap", self.task(session_id=a["id"])["budget"])
        workflow.mode(self.project, "off", a["id"])
        with self.assertRaises(JstackError):
            self.task(session_id=a["id"])
        self.assertTrue(workflow.mode(self.project, "status", b["id"])["active"])
        with self.assertRaises(JstackError):
            workflow.mode(self.project, "status")

    def test_budget_change_and_host_isolation(self):
        self.ready()
        a = workflow.mode(self.project, "on", host="codex")
        self.assertEqual("cheap", workflow.mode(self.project, "on", a["id"], "cheap")["budget"])
        with self.assertRaises(JstackError):
            workflow.mode(self.project, "on", a["id"], host="claude")

    def test_acceptance_is_required(self):
        self.ready()
        with self.assertRaises(JstackError):
            workflow.plan(self.project, "Something")

    def test_fanout_gates_and_no_silent_escalation(self):
        self.ready()
        with self.assertRaises(JstackError):
            self.task(budget="deep", children=1, reason="independent parser", independent=True, agents_available=True)
        self.ready(agents=True)
        with self.assertRaises(JstackError):
            self.task(budget="cheap", children=1)
        for args in ({}, {"reason": "independent"}, {"reason": "independent", "independent": True}):
            with self.assertRaises(JstackError):
                self.task(children=1, **args)
        task = self.task(children=1, reason="isolated parser", independent=True, agents_available=True)
        self.assertEqual(1, task["fanout"]["requested"])
        with self.assertRaises(JstackError):
            self.task(playbook="lightweight", children=1, reason="isolated", independent=True, agents_available=True)

    def test_record_ids_cannot_escape_project(self):
        for value in ("../bad", "/tmp/evil", "x/y", "", "a" * 81):
            with self.assertRaises(JstackError):
                record_path(self.project, "tasks", value)

    def test_writer_lock_rejects_overlapping_mutation(self):
        with project_lock(self.project):
            with self.assertRaises(JstackError):
                with project_lock(self.project):
                    pass
        self.assertFalse((self.project / ".jstack/write.lock").exists())


class VerificationTests(ProjectTest):
    def test_pass_then_content_change_is_stale(self):
        self.ready()
        task = self.task()["id"]
        value = verification.verify(self.project, task)
        self.assertTrue(value["local_checks_passed"])
        self.assertEqual("local_checks_passed", verification.report(self.project, task)["status"])
        self.write("check.py", "print('different content')\n")
        self.assertEqual("stale_or_unknown", verification.report(self.project, task)["status"])

    def test_failing_reproduction_then_fix(self):
        self.write("check.py", "assert 1 == 2, 'reproduction'\n")
        self.ready()
        task = self.task(playbook="bug-fix")["id"]
        baseline = verification.verify(self.project, task, "baseline")
        self.assertEqual("failed", baseline["checks"][0]["status"])
        self.assertEqual("unverified", verification.report(self.project, task)["status"])
        self.write("check.py", "assert 1 == 1\n")
        self.assertTrue(verification.verify(self.project, task)["local_checks_passed"])

    def test_latest_failure_overrides_earlier_pass(self):
        self.ready()
        task = self.task()["id"]
        verification.verify(self.project, task)
        self.write("check.py", "raise SystemExit(3)\n")
        verification.verify(self.project, task)
        report = verification.report(self.project, task)
        self.assertEqual("local_checks_failed_or_incomplete", report["status"])

    def test_no_checks_or_only_optional_cannot_pass(self):
        for checks in ([], [{"name": "optional", "argv": ["{python}", "check.py"], "required": False}]):
            self.ready(checks=checks)
            self.assertFalse(verification.verify(self.project, self.task()["id"])["local_checks_passed"])

    def test_missing_executable_and_timeout(self):
        checks = [{"name": "missing", "argv": ["jstack-nonexistent-executable-98327"]},
                  {"name": "timeout", "argv": ["{python}", "-c", "import time; time.sleep(10)"], "timeout_seconds": 1}]
        self.ready(checks)
        result = verification.verify(self.project, self.task()["id"])
        self.assertEqual(["error", "timeout"], [c["status"] for c in result["checks"]])
        self.assertFalse(result["local_checks_passed"])

    def test_no_shell_interpolation(self):
        self.ready([{"name": "literal", "argv": ["{python}", "-c", "import sys; print(sys.argv[1])", "$(touch injected); hello"]}])
        result = verification.verify(self.project, self.task()["id"])
        self.assertFalse((self.project / "injected").exists())
        self.assertIn("$(touch injected)", result["checks"][0]["output_tail"])

    def test_output_is_bounded(self):
        self.ready([{"name": "loud", "argv": ["{python}", "-c", "print('x'*20000)"]}])
        check = verification.verify(self.project, self.task()["id"])["checks"][0]
        self.assertTrue(check["output_truncated"])
        self.assertLessEqual(len(check["output_tail"]), 16000)

    def test_source_changes_during_check_do_not_pass(self):
        self.ready([{"name": "mutation", "argv": ["{python}", "-c", "from pathlib import Path; Path('changed.txt').write_text('new')"]}])
        value = verification.verify(self.project, self.task()["id"])
        self.assertFalse(value["source_stable"])
        self.assertFalse(value["local_checks_passed"])

    def test_config_change_requires_new_contract_and_stales_report(self):
        cfg = self.ready()
        task = self.task()["id"]
        verification.verify(self.project, task)
        cfg["verification"]["checks"] = []
        self.write(".jstack/config.json", json.dumps(cfg))
        with self.assertRaises(JstackError):
            verification.verify(self.project, task)
        self.assertEqual("stale_or_unknown", verification.report(self.project, task)["status"])

    def test_retry_budget_is_enforced(self):
        self.ready(budget="cheap")
        task = self.task()["id"]
        verification.verify(self.project, task)
        verification.verify(self.project, task)
        with self.assertRaises(JstackError):
            verification.verify(self.project, task)

    def test_supplied_evidence_is_not_execution_proof(self):
        self.ready()
        task = self.task()["id"]
        workflow.add_evidence(self.project, task, "deployment", "Everything works", "https://example.test", "low")
        report = verification.report(self.project, task)
        self.assertEqual("unverified", report["status"])
        self.assertIn("not independently", report["evidence"][0]["provenance"])

    def test_non_git_project_does_not_claim_freshness(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory).resolve()
            install.setup(project)
            cfg = deepcopy(config.DEFAULT)
            cfg["verification"]["checks"] = [{"name": "ok", "argv": ["{python}", "-c", "print('ok')"]}]
            atomic_write(project / ".jstack/config.json", json_bytes(cfg))
            task = workflow.plan(project, "Check one behavior", acceptance=["prints ok"])
            self.assertFalse(verification.verify(project, task["id"])["local_checks_passed"])


if __name__ == "__main__":
    unittest.main()
