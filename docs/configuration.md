# Project configuration

This reference describes the optional Python runner. The standalone skill does
not require this setup; see [skill-only installation](installation.md#skill-only-download-copy-invoke).

`.jstack/config.json` is strict JSON, with `version: 1`. Unknown keys and malformed
values are rejected to expose misspellings. The [JSON Schema](../schemas/config.schema.json)
supports editor validation. `jstack_core/config.py` is the runtime validator.

| Field | Default | Meaning |
| --- | --- | --- |
| `version` | required | Currently `1` |
| `budget` | `normal` | `cheap`, `normal`, or `deep` |
| `agents.enabled` | `false` | Permit a justified plan to include child agents |
| `agents.max_children` | `1` | Project ceiling, integer 0–3 |
| `verification.timeout_seconds` | `120` | Default per-check timeout, integer 1–3600 |
| `verification.checks` | `[]` | Explicit ordered check definitions |

Each check has a unique nonempty `name` (up to 80 characters) and a nonempty `argv`
array of strings. Optional `required` defaults to true. Optional `timeout_seconds`
overrides the project timeout. No command is inferred from package files, and there
is no implicit shell. Every check runs, including optional ones. A failed optional
check remains in the report but does not prevent the required set from passing.
At least one required check must pass for `local_checks_passed`.

Choose checks whose scope fits your project and task. Required checks are never
dropped because the budget is cheap. A plan stores their exact config; editing
verification config requires a new plan before running checks. Project budget
changes affect new sessions/tasks; explicit session and task choices take precedence:

```text
Explicit per-task budget → active session budget → project budget → normal
```

Budget presets are fixed in this release. They do not accept dollar or token values.
Fanout's effective ceiling is zero when disabled, otherwise the minimum of the
budget ceiling and `agents.max_children`. Planning children also needs a reason,
independence declaration and host-capability declaration; lightweight always stays
sequential. The CLI never starts child agents.
