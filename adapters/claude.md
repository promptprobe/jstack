# Claude Code adapter

Invoke `/jstack-mode`, optionally followed by a budget and task. The project path
is `.claude/skills/jstack-mode/`; a personal copy can live at
`~/.claude/skills/jstack-mode/`. The portable ZIP works without setup, namespacing
or automatic argument substitution.

Default to skill-only operation even if this adapter was installed by the optional
runner. Retain the active flag and budget in conversation context. Do not create
session files or require Python just to activate. Only read `references/runner.md`
when the user explicitly requests recorded operation; then use `--host claude`.

Use available Claude Code tools and preserve the existing model, permissions and
CLAUDE.md instructions. Do not enable new tools, MCP servers, hooks or agents just
to follow a playbook. Organization settings may restrict skill discovery.
