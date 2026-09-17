# Release and runtime validation

[한국어 검증 기록](validation.ko.md)

## Follow-up live Codex evaluation

On 2026-09-16 (America/Los_Angeles), three real model turns were executed in an
isolated cart fixture using Codex CLI 0.154.0, the configured `gpt-6-astra` model,
and the host's existing `max` reasoning setting. jstack used `cheap` throughout.
No model or global setting was changed. The runtime under test was commit
`5a33920c17afe0dc4f809540f24c1101bffc321a`.

| Scenario | Observed result |
| --- | --- |
| Explicit `$jstack-mode cheap` bug fix | Skill read, acceptance contract created, failing baseline recorded before implementation, 5 fixture tests passed after the fix |
| Follow-up without mentioning the skill | Same session ID and cheap budget retained; a second contract and failing/passing receipts were created; 6 fixture tests passed |
| `jstack off`, then a plain README edit | Session became inactive, README changed, no new task or run records were created |
| Independent post-run check | All 6 fixture tests and 75 combinations of cart state, product name and quantity passed; original tests remained present |

Confidence is high for those observed scenarios. This is one small fixture and one
host/model configuration, not a reliability benchmark. Compaction recovery,
cross-chat behavior, live Claude Code execution and comparative token savings
remain unverified. The [structured summary](evaluations/codex-2026-09-16.json)
contains the evaluated scope and limits; the [Korean record](validation.ko.md)
includes prompts and reproduction instructions.

The existing Codex CLI 0.149.1 rejected the configured model before jstack ran.
An isolated copy of the official 0.154.0 CLI and its matching code-mode host was
used instead, with release download hashes checked. This resolved the test
environment without replacing the existing CLI. Claude Code was unavailable.

`cheap` did not lower the host's `max` reasoning setting. It controls workflow
allowances, not model billing or unrelated plugin context. No savings claim follows
from this test.

## Initial release preparation

Observed during preparation of 0.1.0 on 2026-09-16:

| Check | Result | Scope / confidence |
| --- | --- | --- |
| 34 deterministic tests, Python 3.12.14 on macOS | Passed | High: tested behavior in this environment |
| Installed CLI smoke flow | Passed | High: both adapter layouts, separate sessions, failing baseline, passing fix, stale detection, opt-out, uninstall/reinstall |
| Skill Creator structure validator | Passed | High: skill frontmatter/structure only |
| Local links, Python syntax, example configs | Passed | High: static repository checks |
| Codex CLI 0.149.1 `skills/list` | Discovered one enabled repo-scoped `jstack-mode`, correct UI metadata, no skill errors | High: live discovery only; no model call |
| Live multi-turn Codex workflow at initial release | Not yet evaluated at that point; see follow-up above | The later test covers three turns, not compaction or actual savings |
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
