# Roadmap

## 0.2 — Available now

A standalone skill ZIP for personal or project use in Codex and Claude Code,
with no jstack runtime or config prerequisite; one sticky entry skill; eight
focused playbooks; cheap/normal/deep effort; and justified optional fanout.
The optional runner adds project-local adapters, explicit session IDs, strict
config, acceptance contracts, check execution, bounded receipts and source freshness. All tooling works offline
except whatever network access a project's configured checks explicitly use.

## Next: broaden host evaluation

A [three-turn live Codex evaluation](validation.md) now covers activation, a sticky
follow-up and opt-out in one small fixture. It establishes an initial observed
case, not a cross-host reliability result.

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
