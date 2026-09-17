# Optional recorded operation

Read this only when jstack receipts are explicitly requested or a recorded session
is being continued. The complete project runtime must already exist at
`.jstack/jstack.py`, with Python 3.10+, Git and `.jstack/config.json` at the project
repository root. Do not install or claim to run missing tooling. If unavailable,
state that recording is unavailable and continue authorized work in skill-only mode.

Inspect configured checks before execution. If they are empty, configure relevant
checks within the user's scope before creating a task; empty checks cannot pass.
Do not execute an invalid config or silently remove failing required checks.

```sh
python3 .jstack/jstack.py mode on --host codex --budget normal
```

Use `--host claude` in Claude Code and the selected budget. Retain the returned
session ID in this conversation; never select an arbitrary active session on disk.
For budget changes run `mode on --session ID --budget cheap|normal|deep`;
for `jstack off` run `mode off --session ID`, then stop applying the mode.
Carry the ID into handoffs. If lost, explain the gap and recover it from the user
or start fresh on explicit invocation.

```sh
python3 .jstack/jstack.py plan 'Fix duplicate cart additions' --session ID \
  --playbook bug-fix --accept 'One click adds exactly one item after reconnect'
python3 .jstack/jstack.py verify --task TASK_ID --phase baseline
# Implement the scoped change, then:
python3 .jstack/jstack.py verify --task TASK_ID
python3 .jstack/jstack.py report --task TASK_ID
```

The router is only a keyword hint; choose the intended playbook explicitly when
needed. Configure checks before planning; a later config change needs a new
contract. The runner enforces final-check attempts per task. Never create new IDs
just to bypass a failed or exhausted task. Preserve its evidence and report the gap.

Extra observations can be recorded with `evidence --task TASK_ID --kind
runtime|source|ci|deployment|inference --claim TEXT --source PATH_OR_URL
--confidence high|moderate|low|unknown`. This saves an operator-supplied claim; it
does not verify that claim or URL. Read actual output and keep receipt coverage
distinct from user acceptance. Source fingerprints cover Git-visible content,
not all environmental or external inputs. Local JSON is mutable, not an attestation.
