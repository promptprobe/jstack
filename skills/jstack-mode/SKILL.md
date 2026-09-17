---
name: jstack-mode
description: Run an opt-in jstack coding workflow with cheap, normal, or deep effort, an acceptance contract, and recorded verification. Use when the user asks for jstack or continues an active jstack session.
---

# jstack-mode

Keep engineering effort proportional to the decision. Start with one agent, one
observable outcome, and the smallest useful check. Budget is an effort policy,
not a dollar estimate or a substitute for correctness.

## Activate once per conversation

On first use, read [the host adapter](references/host.md) if installed, then
`.jstack/config.json`. From the project root run:

```sh
python3 .jstack/jstack.py mode on --host codex --budget normal
```

Use `--host claude` for Claude Code. Use the user's budget when specified;
otherwise omit `--budget` to read the project default. Retain the returned session
ID in this conversation. On later coding turns, reuse that ID and the selected
budget without making the user invoke the skill again. Ordinary conversation does
not need a task contract. User instructions continue to control scope.

`jstack off` means run `mode off --session ID` and stop applying this workflow.
For a budget change, run `mode on --session ID --budget cheap|normal|deep`.
Never search disk for an arbitrary active session. After compaction, carry the ID,
budget, current task ID and unresolved evidence in the handoff. If those are lost,
explain the gap and start a new session on invocation; do not promise automatic
cross-chat memory. Sticky behavior depends on the host following these instructions.

## Route and define evidence before editing

Read only the selected playbook: [feature](references/playbooks/feature.md),
[bug-fix](references/playbooks/bug-fix.md), [refactor](references/playbooks/refactor.md),
[perf](references/playbooks/perf.md), [prototype](references/playbooks/prototype.md),
[verification](references/playbooks/verification.md), [shipping](references/playbooks/shipping.md),
or [lightweight](references/playbooks/lightweight.md).

Choose from task intent. The CLI's keyword router is a hint and can be wrong,
particularly with negation or several goals. Use `--playbook` to correct it.
Split genuinely distinct goals into separate task contracts.

```sh
python3 .jstack/jstack.py plan 'Fix duplicate cart additions' --session ID \
  --playbook bug-fix --accept 'One click adds exactly one item after reconnect'
```

Before creating the contract, inspect configured checks and make them relevant to
the outcome. Checks are executable project code; read their argv and referenced
scripts before running them. Configure them only within existing authorization.
The default checks list is empty on purpose. If configuration changes after a
plan, create a new contract instead of silently weakening the old one.

## Spend deliberately

| Budget | Investigation passes | Repair attempts after first check | Child-agent ceiling | Initial file-read hint |
| --- | ---: | ---: | ---: | ---: |
| cheap | 1 | 1 | 0 | 4 |
| normal | 2 | 2 | 1 | 10 |
| deep | 4 | 3 | 3 | 20 |

These are ceilings, not quotas. File counts and investigation passes are guidance;
the local runner enforces final verification attempts per task. Do not recreate
task IDs just to bypass an exhausted allowance. Preserve the failed evidence,
explain what was learned, and let the user choose a new scope or budget. Do not
upgrade effort or switch paid models silently. Keep the host's current model.
Required checks remain required at every budget. Read narrow source slices; do
not load every playbook or reread unchanged files after each turn.

Fanout is off unless project config enables it, the host and current instructions
permit it, and independent work will save more time than coordination costs.
Read [fanout](references/fanout.md) only at that decision. Sequential work is the
fallback. A deep budget never creates an obligation to spawn agents.

## Verify, then report what the evidence establishes

For a meaningful baseline, run `verify --task TASK_ID --phase baseline` before
implementation. A failing baseline is useful evidence. After implementation run:

```sh
python3 .jstack/jstack.py verify --task TASK_ID
python3 .jstack/jstack.py report --task TASK_ID
```

Read the actual check output. A zero exit code establishes only what that command
tests. Inspect relevant behavior: a UI flow, a saved artifact, a API response, or a
before/after measurement. Record extra observations with `evidence --task TASK_ID
--kind runtime|source|ci|deployment|inference --claim TEXT --source PATH_OR_URL
--confidence high|moderate|low|unknown`. This records a supplied claim, not an
automatic independent verification. Never label an inference as observed.

Read [evidence](references/evidence.md) when a result is ambiguous. Report the
outcome, source of proof, check failures or omissions, and remaining limits. Keep
local checks, CI, remote commits, and live deployment separate. Use high, moderate,
low, or unknown for major claims. If source changed after verification, recheck the
affected behavior within budget. Never say “done” just because a command ran.

Shipping actions require the user's task authorization. Reuse authorization
already given; prepare the concrete result before asking about a missing decision.
Do not turn a request to implement into permission to publish, merge or deploy.
