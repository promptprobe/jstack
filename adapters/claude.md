# Claude Code adapter

Setup places this skill at `.claude/skills/jstack-mode/` and adds a small opt-in
anchor to `CLAUDE.md`. Invoke `/jstack-mode`, optionally followed by the budget and
task in ordinary language. The skill does not depend on plugin namespacing or
automatic argument substitution.

Use `python3 .jstack/jstack.py mode on --host claude` from the project root.
Use Claude Code's available tools and existing permissions. A configured child
allowance is not a request to create a new model configuration or enable an
unavailable Agent tool. Keep the current model. No hooks, global settings,
MCP servers or background processes are installed.

Retain the session ID in conversation summaries so later turns can reuse it.
If compaction loses it, start fresh on invocation or recover the ID from the user;
never select another task's on-disk session. Existing CLAUDE.md content remains
intact outside the managed jstack block. Organization settings may restrict skill
discovery; inspect the host's skill list instead of claiming successful activation.
