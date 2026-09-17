# Codex adapter

Setup places this skill at `.agents/skills/jstack-mode/` and adds a small opt-in
anchor to `AGENTS.md`. Invoke `$jstack-mode` in Codex CLI or the IDE extension;
use the host's skill picker if its UI uses a different mention syntax.

Use `python3 .jstack/jstack.py mode on --host codex` from the project root.
Use the tools actually available in this Codex environment for shell execution,
editing and inspection. Do not assume a Cursor Task API, model alias, browser
driver, or a particular thread environment variable. Keep the existing model and
permissions. If native agent tools are unavailable or forbidden, work sequentially.

Retain the jstack session ID in the conversation and any compaction handoff.
CLI records do not make the host remember an ID it has lost. Project instructions
provide a reminder, not a background service. No hooks or global settings are
installed. Existing AGENTS.md content remains authoritative within its scope.
