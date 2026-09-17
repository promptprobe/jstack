# Optional fanout

Use extra agents only for a bounded independent investigation, implementation
slice, or review whose results the parent can validate. Duplicate full-repository
reads and several agents editing the same file usually erase the benefit.

All gates must hold: project `agents.enabled`, budget ceiling, available host
capability, current user/project permission, a concrete reason, and independent
ownership. Example after those facts have been established:

```sh
python3 .jstack/jstack.py plan 'Add CSV and JSON exports' --session ID \
  --accept 'Both exports round-trip the documented fixture' --agents 1 \
  --reason 'The JSON serializer has an isolated file and test fixture' \
  --independent --agents-available
```

The CLI records the allowance; it does not create agents or enforce the host's
agent lifecycle. Give each child its exact deliverable, owned paths, required
evidence, and stopping condition. Keep shared contracts and final integration with
one owner. Charge children to the same task budget; do not let them recursively
fan out. Use separate checkouts when edits could collide. Verify integrated
behavior yourself and cite the child's report as a report, not as observed proof.

If the tool is absent, do the same work sequentially. Do not install another host,
invent an API, or pay for another model just to satisfy a playbook.
