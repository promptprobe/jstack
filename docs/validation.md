# Release validation

Observed during preparation of 0.1.0 on 2026-09-16:

| Check | Result | Scope / confidence |
| --- | --- | --- |
| 34 deterministic tests, Python 3.12.14 on macOS | Passed | High: tested behavior in this environment |
| Installed CLI smoke flow | Passed | High: both adapter layouts, separate sessions, failing baseline, passing fix, stale detection, opt-out, uninstall/reinstall |
| Skill Creator structure validator | Passed | High: skill frontmatter/structure only |
| Local links, Python syntax, example configs | Passed | High: static repository checks |
| Codex CLI 0.149.1 `skills/list` | Discovered one enabled repo-scoped `jstack-mode`, correct UI metadata, no skill errors | High: live discovery only; no model call |
| Live multi-turn Codex workflow | Not evaluated | Unknown: adherence, compaction and actual cost |
| Live Claude Code discovery/workflow | Not evaluated; executable unavailable locally | Unknown: layout tests are not live-host evidence |
| Lower token cost than another workflow | Not measured | Unknown |

The [CI workflow](https://github.com/promptprobe/jstack/actions/workflows/validate.yml)
runs the repository validation on Linux (Python 3.10 and 3.14), macOS (3.12), and
Windows (3.12). Consult the exact commit's run for remote status; this document is
a preparation record, not an assertion that all future CI runs pass.

Reproduce tooling validation with `python3 scripts/validate.py`. The installed CLI
smoke flow also runs independently with `python3 scripts/smoke.py`. Live Codex
discovery was checked via its local app-server's `initialize` and `skills/list`
methods against a disposable Git project after setup; it used no model calls.
See [contributing](../CONTRIBUTING.md) for the behavioral host evaluations still
needed before claiming workflow reliability or cost improvements.
