# Architecture and boundaries

The canonical portable skill lives in `skills/jstack-mode/`. Its short entry
selects one reference playbook. Setup copies the skill to each host's discovery
location and substitutes a host-specific reference. Adapters translate discovery,
invocation and tool expectations; they do not duplicate the workflow engine.

The Python runtime has no external dependencies:

- `config.py` validates project data and defines effort presets.
- `workflow.py` routes tasks, creates acceptance contracts, and manages explicit
  conversation IDs. Mode is not shared implicitly between conversations.
- `verification.py` runs argv checks and ties their receipts to source content.
- `install.py` manages owned files and bounded instruction blocks.
- `storage.py` contains path validation, atomic record writes and the writer lock.
- `cli.py` provides explicit commands and exit codes.

## Contract lifecycle

1. Setup creates config with no assumed project check command.
2. Mode activation creates an isolated session and selects an effort preset.
3. Planning stores the task, acceptance, playbook, budget, optional fanout reason
   and a snapshot of verification configuration. Plans do not execute code.
4. An optional baseline records current behavior. The host performs the edit.
5. Final verification executes the plan's checks if configuration still matches.
6. Reporting compares current source with the latest final receipt and lists
   supplied observations separately.

Records live under `.jstack/local/{sessions,tasks,runs,evidence}/`. Records are
written via temporary files plus replace. Mutating CLI operations hold one
project lock; live checks can block another CLI writer until they finish. This
does not lock the application source against other editors.

## What a fingerprint means

The verifier asks Git for tracked and nonignored untracked paths at the project
root, then hashes file content and permission modes. Deleted paths and symlinks
are represented explicitly. Symlink targets are not followed; ancestor symlinks
or submodule directories make freshness unavailable. Git HEAD is captured as
context but content determines freshness, so merely committing identical content
does not invalidate a receipt.

`.jstack/local/` and the lock are excluded so recording evidence does not make
itself stale. Ignored files, external dependencies, environment variables,
databases and remote services are outside this fingerprint. A concurrent edit
that is reverted during a check can evade a before/after fingerprint; isolate
verification when that matters. These receipts are not reproducible-build or
security attestations.

The runner captures stdout and stderr together in temporary disk storage and keeps
the final 16,000 bytes in a JSON receipt. A noisy command can still use disk space
until its timeout. POSIX timeout handling kills the process group. On Windows it
kills the direct process; descendant cleanup is a known limitation. Commands inherit
the caller's environment and permissions. jstack is not an execution sandbox.

## Trust boundaries

Configuration is user-managed executable project configuration. argv execution
avoids implicit shell expansion but a command can explicitly launch a shell or
perform network/mutation operations. jstack itself makes no network or model calls;
configured checks may do so. Reports label supplied CI/deployment observations as
supplied. The host must verify their actual sources before asserting success.
