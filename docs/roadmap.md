# Roadmap

## 0.1 — Available now

Project-local Codex and Claude Code adapters; one sticky entry skill; eight focused
playbooks; cheap/normal/deep effort; explicit session IDs; strict config; justified
fanout declarations; acceptance contracts; baseline/final check execution; bounded
output receipts; source freshness; and evidence reports. All tooling works offline
except whatever network access a project's configured checks explicitly use.

## Next: demonstrate host behavior

Build a small public evaluation suite of genuine tasks for each host. Include a
multi-turn bug fix, lightweight edit, performance hypothesis, shipping with and
without authorization, lost session context, and exhausted cheap budget. Publish
the host/model versions, prompts, artifacts, cost and observed deviations. Passing
means correct task behavior with evidence, not matching a sentence in the skill.

## Next: account for actual cost

Import usage only when a host exposes it and the user opts in. Attribute parent and
child tokens to a task. Display unknown when unavailable. Compare accepted tasks
per unit cost and include failure/retry costs. A hard spend cap must be enforced
at the host/API boundary, not simulated by a prompt.

## Next: improve verification scope

Allow named external-input fingerprints and attach structured browser/CI artifacts.
Ensure stale or missing inputs never silently pass. Add explicit submodule support,
Windows descendant process cleanup, and bounded on-disk command logging. Keep
direct observations distinct from imported or operator-supplied claims.

## Later: distribution and routing

Offer versioned plugin packages for both hosts, signed checksums and an update
compatibility policy. Keep project-local setup available. Expand routing using
published ambiguous/multilingual fixtures; preserve deterministic offline routing
and explicit playbook overrides. Add playbooks only when repeated real tasks show
that an existing one is insufficient.

## Non-goals

An autonomous deployment service, model marketplace, billing proxy, security
sandbox, or persistent cross-chat memory system. No automatic external messages,
publication, recursive agent swarms or hidden telemetry.
