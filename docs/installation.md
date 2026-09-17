# Installation, updates and removal

Run setup from a full jstack checkout with Python 3.10+ and Git. Target an existing
project directory; source freshness requires it to be a Git repository root.
Use `--project /absolute/path` if you are not already in that directory.

```sh
python3 /path/to/jstack/jstack.py setup --project /path/to/project --host codex
python3 /path/to/jstack/jstack.py setup --project /path/to/project --host claude
```

Adding a host preserves the other installed adapter. Both get the same entry
skill and playbooks, with a different `references/host.md`. The installed runtime
does not require the original checkout after setup. Copying only the skill folder
omits the helper; use setup for the supported complete experience.

## Files and ownership

| Path | Ownership |
| --- | --- |
| `.jstack/config.json` | User/team; setup creates only if absent |
| `.jstack/jstack.py`, `.jstack/jstack_core/` | Managed runtime |
| `.agents/skills/jstack-mode/` | Managed Codex skill files; extra user files preserved |
| `.claude/skills/jstack-mode/` | Managed Claude Code skill files; extra user files preserved |
| `AGENTS.md`, `CLAUDE.md` | Only the marked jstack block is managed |
| `.gitignore` | A marked privacy block is added; other content preserved |
| `.jstack/install.json` | Managed file hashes, host list and instruction-block hashes |
| `.jstack/local/` | Private local sessions, tasks, runs and observations |

Setup preflights all known conflicts before writing. It rejects symlinked managed
paths, unowned collisions, changed/missing owned files, and malformed instruction
markers. There is no force-overwrite option. Preserve local edits elsewhere and
resolve the specific conflict before retrying. Ordinary write failures trigger
rollback; abrupt process termination or power loss is not transactional. Restore
from Git or inspect the partial state after such an interruption.

`--dry-run` does not create files or acquire a write lock. Regular mutations share
an exclusive project lock. A second writer exits with a clear message rather than
overwriting records. After a crash, confirm no jstack process is running before
removing `.jstack/write.lock`. Different conversation IDs isolate state, but agents
still need separate worktrees if their application edits can collide.

## Updating

Review the new version and update the source checkout, then rerun setup from it:

```sh
git -C /path/to/jstack pull --ff-only
python3 /path/to/jstack/jstack.py setup --project /path/to/project --host both
```

Unchanged installations are idempotent. Local config and records survive updates.
Existing file hashes allow owned files to be replaced, while locally edited
runtime/skill files stop the update. Review the resulting project diff and commit
the update with your usual workflow. There are no automatic downloads.

## Removing

```sh
python3 .jstack/jstack.py uninstall --dry-run
python3 .jstack/jstack.py uninstall
```

Removal deletes owned runtime and skill files and removes the instruction blocks.
It preserves config, records, additional user files, and the `.gitignore` privacy
block. A small manifest retains ownership of that block so reinstallation works.
Empty directories or whitespace in instruction files may remain. Delete preserved
data yourself only when you no longer need it; inspect it before committing.

## Host compatibility

Codex repository skills use `.agents/skills`; Claude Code uses `.claude/skills`.
These paths and invocation forms follow [OpenAI's skills documentation](https://learn.chatgpt.com/docs/build-skills)
and [Claude Code's skills documentation](https://code.claude.com/docs/en/skills).
Both adapters preserve the host's model and permission configuration. Organization
policies can prevent discovery. Check the skill selector and restart/refresh the
host when needed. Host discovery and behavior should be validated in your own
environment; setup success alone does not establish them.
