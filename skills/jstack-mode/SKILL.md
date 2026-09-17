---
name: jstack-mode
description: Use jstack for cost-aware coding with cheap, normal, or deep effort and verification before completion. Apply when the user asks for jstack or continues an active jstack conversation; works without a separate runtime.
---

# jstack-mode

Start with one agent, one observable outcome, and the smallest useful check.
This folder is a complete skill. Default to **skill-only** operation: no jstack
CLI, Python installation, Git setup, generated config, or session files required.
Use the host's existing editing, execution and inspection tools. The project may
still need its own language runtime and dependencies to run its tests.

## Activate once per conversation

Read [host guidance](references/host.md) on first use. Remember in this conversation:
`jstack active; skill-only; budget cheap|normal|deep; fanout off`.
Use the requested budget, otherwise an existing `.jstack/config.json` budget if
present, otherwise `normal`. Config is optional; do not create it or install
anything just to activate. Existing config can also supply checks and agent
preferences; current user and project instructions still control scope.

Briefly acknowledge the budget and proceed with the user's task. Later coding
turns reuse this state without another invocation. `jstack budget cheap` changes
the remembered budget; `jstack off` stops the mode without a command or disk write.
Ordinary conversation does not need a task contract. Keep state, current outcome
and unresolved evidence in any compaction handoff. If context is lost, say so and
restart on invocation; never infer activation from another conversation's files.
Sticky behavior depends on host adherence, not guaranteed cross-chat memory.

**Recorded operation is opt-in.** Only when the user requests jstack's local
receipts, or explicitly continues a recorded session, read
[the optional runner](references/runner.md). Having `.jstack/` on disk alone does
not require using it. If requested recording is unavailable, disclose that gap;
continue authorized work in skill-only mode without claiming a receipt exists.

## Route and choose evidence before editing

Choose from intent and read only the relevant playbook:
[feature](references/playbooks/feature.md),
[bug-fix](references/playbooks/bug-fix.md),
[refactor](references/playbooks/refactor.md),
[perf](references/playbooks/perf.md),
[prototype](references/playbooks/prototype.md),
[verification](references/playbooks/verification.md),
[shipping](references/playbooks/shipping.md), or
[lightweight](references/playbooks/lightweight.md).

State a short acceptance contract **in the conversation**: intended result,
scope and how it will be checked. A small edit needs only a sentence. Discover
real checks from project instructions, manifests, test files or existing config;
inspect commands and referenced scripts before running them. Do not invent a test
command, create ceremonial plan files, or add tests that just mirror a text edit.
Configured `{python}` placeholders need an available interpreter, not a guessed
path; if none exists, report that check as unavailable.

For a meaningful baseline, reproduce the bug or measure current behavior before
the fix. Then make the scoped change and run relevant checks using native host
tools. If checks are missing or unavailable, inspect what can be observed and
state the verification gap. Absence of a test suite is not a passing test.

## Spend deliberately

| Budget | Investigation passes | Repair attempts after first check | Child-agent ceiling | Initial file-read hint |
| --- | ---: | ---: | ---: | ---: |
| cheap | 1 | 1 | 0 | 4 |
| normal | 2 | 2 | 1 | 10 |
| deep | 4 | 3 | 3 | 20 |

These are ceilings, not quotas. In skill-only mode they are instructions, not
mechanically enforced counters or token/dollar caps. At the limit, preserve failed
evidence and propose a smaller scope or a specific next experiment; do not silently
raise the budget or relabel the task to evade it. Keep the host's selected model
and reasoning settings. Required checks remain required at every budget.
Read narrow source slices; do not load all playbooks or reread unchanged files.

Fanout is off by default. Consider it only if the user or existing project config
explicitly enables it, the host and current instructions permit it, and independent
work justifies its coordination cost. Then read [fanout](references/fanout.md).
A deep budget alone does not enable agents. Work sequentially otherwise.

## Report what the evidence establishes

Read actual output. A zero exit code proves only what the command tests. Exercise
relevant behavior when available: a UI flow, saved artifact, API response or
before/after measurement. After a material source or input change, rerun affected
checks within budget; do not present older results as current.

Report the outcome, exact check or observation, failures and omissions, and
remaining limits. Label major claims high, moderate, low or unknown. Keep source
inspection, local tests, CI, remote commits and live deployment separate.
Read [evidence](references/evidence.md) when the distinction is unclear. Skill-only
mode reports evidence in the conversation; never invent session IDs, receipts,
fingerprints, saved reports or automatic freshness detection.

Shipping needs the user's task authorization; reuse authorization already given.
An instruction to implement does not itself authorize publishing, merging or
deploying. Report missing access as a boundary, not a successful action.
