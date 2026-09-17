# Portable host guidance

The same folder works in both hosts; no setup command or other repository files
are required for skill-only operation.

| Host | Project skill path | Personal skill path | Invoke |
| --- | --- | --- | --- |
| Codex | `.agents/skills/jstack-mode/` | `~/.agents/skills/jstack-mode/` | `$jstack-mode cheap` |
| Claude Code | `.claude/skills/jstack-mode/` | `~/.claude/skills/jstack-mode/` | `/jstack-mode cheap` |

Use the host's skill picker when its UI offers one. If discovery fails, inspect
the folder layout and refresh/restart the host. A file copy does not prove that
the model loaded it. Organization settings can restrict discovery.

Use only tools available in the current host. Keep the selected model, permissions
and project instructions. Do not assume a Cursor API, browser driver or child
agent tool. The skill does not modify AGENTS.md, CLAUDE.md or global configuration.
In skill-only mode, carry the active flag and budget in conversation context;
there is no on-disk session to recover. The optional runner has separate session
IDs described in [runner guidance](runner.md); read it only for recorded operation.
