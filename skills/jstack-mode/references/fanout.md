# Optional fanout

Use extra agents only for a bounded independent investigation, implementation
slice or review whose results the parent can validate. Duplicate repository reads
and several agents editing the same file usually erase the benefit.

All gates must hold: explicit enablement by the user or existing project config,
budget ceiling, available host capability, current user/project permission, a
concrete reason, and independent ownership. Use the lower of the budget and any
configured child ceiling. Lightweight tasks never use children. Cheap permits zero.
State the reason and ownership in the conversation before delegating.

Give each child its deliverable, owned paths, required evidence and stopping
condition. Keep shared contracts and integration with one owner. Charge children
to the same task budget; do not let them recursively fan out. Use isolated
checkouts if edits could collide. Verify integrated behavior yourself; a child's
report is a report, not direct observation by the parent.

In optional recorded operation, the CLI additionally requires project
`agents.enabled` and records the allowance, but does not create or supervise agents:

```sh
python3 .jstack/jstack.py plan 'Add CSV and JSON exports' --session ID \
  --accept 'Both exports round-trip the documented fixture' --agents 1 \
  --reason 'The JSON serializer has an isolated file and test fixture' \
  --independent --agents-available
```

If capability is absent, do the work sequentially. Do not install another host,
invent an API or select a paid model just to satisfy a playbook.
