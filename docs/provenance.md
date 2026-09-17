# Design provenance

jstack's original brief was a lighter, cost-aware engineering workflow for Codex
and Claude Code. The public pstack README was reviewed for product concepts:
persistent mode, task routing, focused playbooks, explicit verification, and
configurable effort. No upstream source tree was cloned into this project and no
upstream code or prompt text is bundled.

Source reviewed: [cursor/plugins pstack README](https://github.com/cursor/plugins/blob/e31650eea443aaea1e84cc15d88c13f40080b275/pstack/README.md),
snapshot `e31650eea443aaea1e84cc15d88c13f40080b275`, accessed 2026-09-16.
Credit for pstack belongs to Lauren Tan ([poteto](https://github.com/poteto)).

The current pstack README includes reasoning-budget configuration. Budget choice
is therefore not presented as a novel jstack invention. jstack's implementation
choices are a dependency-free local helper, a single progressively loaded skill,
project-local adapters for two hosts, explicit session isolation, gated fanout,
and source-bound command evidence. Lower token usage remains an unmeasured goal.

Compatibility references checked while authoring:

- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) — repository
  discovery, metadata, progressive loading and explicit invocation.
- [Anthropic: Extend Claude with skills](https://code.claude.com/docs/en/skills) —
  project skill folders, slash invocation and supporting references.

The project ships under its own MIT license. Attribution here recognizes
conceptual inspiration; it does not imply affiliation or endorsement.
