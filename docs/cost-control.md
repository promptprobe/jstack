# Cost-control policy

The cheapest useful workflow is the one that resolves the task with sufficient
evidence. Fewer tokens can be a false economy if an untested patch creates a later
incident. jstack constrains optional exploration and coordination while preserving
the checks required by the task and project.

The host's existing model, reasoning effort and other installed plugins still
contribute to usage under every budget. For example, `cheap` does not lower a
host configured for maximum reasoning. Its label describes workflow allowances,
not a demonstrated low-price execution mode.

## Hard checks versus agent guidance

| Policy | Implemented by |
| --- | --- |
| Allowed budget names and strict config fields | CLI validation |
| Maximum planned children, enablement, reason and independence flags | CLI plan gate |
| Initial final verification plus 1 / 2 / 3 retries | CLI per-task run receipts |
| One baseline verification per task | CLI per-task run receipts |
| Required checks, timeout and nonempty required set | Verification runner |
| Investigation passes, initial file reads, concise context | Skill instructions |
| No recursive fanout, actual child count, current model | Host/agent adherence |
| Token/dollar caps | Not implemented; requires host metering/enforcement |

Flags about independence and capability are declarations, not proofs. The parent
must assess them honestly. CLI task limits can be bypassed by creating another
task; the skill explicitly forbids doing that just to evade a budget. This is a
collaboration tool, not a sandbox or billing enforcement service.

When an allowance is exhausted, report what failed and the remaining uncertainty.
Recommend a concrete next experiment, smaller scope or revised budget. Preserve
existing authorization, but do not interpret it as permission to increase spending
or launch new models. Do not manufacture a “success” by dropping required checks.

## A useful cost experiment

Select representative tasks with fixed starting revisions and acceptance tests.
Compare the same host/model with and without jstack; alternate task order to reduce
learning effects. Record tokens, wall time, tool calls, human interventions and
acceptance failures. Include retries and child-agent usage. Repeat enough tasks to
show variability and publish raw conditions. Until such measurements exist, treat
lower cost as a design objective, not an established result.
