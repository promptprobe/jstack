# Contributing

Use Python 3.10+ and Git. There are no third-party runtime or test dependencies.

```sh
python3 scripts/validate.py
```

Keep changes focused on an observable workflow improvement. For a bug, include the
reproduction, expected result, root cause and regression check. For a skill change,
provide a realistic task and explain the decision it improves. Do not grow the
entry skill with generic coding advice or every host's manual.

## Working boundaries

Keep source instructions in `skills/jstack-mode/` and host-specific behavior in
`adapters/`. Put new deterministic logic behind the CLI and test its externally
visible effect. Preserve project files and local edits during setup. Treat claims
about lower cost, live-host behavior, CI and deployment as separate claims requiring
their own evidence. Avoid vendor model aliases or implicit model upgrades.

Do not include local session records, command logs, credentials or private prompt
text in a contribution. Original contributions only; credit public inspiration and
identify any third-party code and license before adding it.

## Manual host evaluation scenarios

Extract the built ZIP into a disposable project and exercise each target host.
Test skill-only mode with no runtime or config; evaluate recorded mode separately:

1. Invoke jstack cheap, complete a small bug fix, then request a follow-up without
   mentioning jstack. Check active mode/budget continuity and evidence.
2. Turn the mode off. Confirm unrelated later work stops applying the workflow.
3. Compact context and check recovery of the active flag and budget. In recorded
   mode, preserve the explicit ID without selecting another conversation's record.
4. Ask for three agents under cheap budget. Confirm no silent escalation.
5. Ask only for a review. Confirm no application edit or external publication.
6. Provide a failing check or unavailable environment. Confirm it is not reported
   as a successful delivery.

Record host/model versions, exact starting revision, observations, failures and
usage when available. The deterministic suite does not substitute for these tasks.
