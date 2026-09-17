# Codex adapter

Invoke `$jstack-mode` or select it in the host's skill picker. The project path is
`.agents/skills/jstack-mode/`; a personal copy can live at
`~/.agents/skills/jstack-mode/`. The portable ZIP works without setup.

Default to skill-only operation even if this adapter was installed by the optional
runner. Retain the active flag and budget in conversation context. Do not create
session files or require Python just to activate. Only read `references/runner.md`
when the user explicitly requests recorded operation; then use `--host codex`.

Use available Codex tools and preserve existing model, permissions and AGENTS.md
instructions. No Cursor API, browser driver, agent tool or thread variable is
assumed. Work sequentially when delegation is unavailable or disallowed.
