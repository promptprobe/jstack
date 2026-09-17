# CLI reference

Run `python3 jstack.py COMMAND --help` from the checkout, or
`python3 .jstack/jstack.py COMMAND --help` after installation. Every command accepts
`--project PATH` after the command; the default is the current directory.

| Command | Purpose |
| --- | --- |
| `setup --host codex\|claude\|both [--dry-run]` | Install/update from a complete checkout |
| `uninstall [--dry-run]` | Remove owned files; preserve user config and local data |
| `doctor` | Inspect config, install hashes and optional host binary presence |
| `mode on [--session ID] [--host codex\|claude] [--budget LEVEL]` | Create or update conversation state |
| `mode status\|off --session ID` | Inspect or deactivate that explicit session |
| `route 'TASK' [--playbook NAME]` | Preview routing without config or state writes |
| `plan 'TASK' --accept 'OUTCOME' [--session ID] [--budget LEVEL]` | Save an acceptance contract |
| `verify --task ID [--phase baseline\|final]` | Execute configured checks and save a receipt |
| `report --task ID [--format markdown\|json]` | Read evidence and current source freshness |
| `evidence --task ID --kind KIND --claim TEXT --source REF --confidence LEVEL` | Record an explicitly supplied observation |

`plan` also accepts `--playbook`, repeatable `--accept`, and fanout declarations:
`--agents N --reason TEXT --independent --agents-available`. The latter are not
permission to spawn if the host, user or project instructions disallow it.

Evidence kinds: `source`, `runtime`, `ci`, `deployment`, `inference`. Confidence:
`high`, `moderate`, `low`, `unknown`. A source is a reference string for the human
reviewer; the CLI does not fetch or validate it.

```sh
python3 .jstack/jstack.py evidence --task TASK_ID --kind runtime \
  --claim 'Saved Unicode rows reopen with the same values' \
  --source 'artifacts/export-roundtrip.txt' --confidence high
```

This example records a claim. Create and inspect the real artifact before using it.

## Exit codes and statuses

- `0`: command completed; for `verify`, a nonempty required set passed with stable,
  available source fingerprints. For `doctor`, no reported problem remains.
- `1`: `verify` failed/incomplete/unknown, or `doctor` found a problem.
- `2`: invalid usage/config, installation conflict, exhausted allowance or I/O error.

`report` returns 0 when it successfully renders **any** status, including stale or
unverified. Automation consuming reports must inspect the JSON `status` field.
Possible statuses are `unverified`, `stale_or_unknown`, `local_checks_passed`, and
`local_checks_failed_or_incomplete`. None means natural-language acceptance or
successful deployment. A baseline never satisfies final verification.

The first final verification plus the selected number of repair retries is allowed
per task. Baseline is limited to one run. Do not churn task IDs to evade a limit;
retain the findings and make an explicit scope/budget decision instead.
