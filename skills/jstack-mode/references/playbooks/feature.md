# Feature

Define the smallest complete user path and its failure case. Inspect the existing
entry point, data shape and conventions before introducing a new abstraction.
Choose a verification command and a runtime observation that would distinguish
success from a plausible-looking implementation; write these into the contract.

Implement one coherent slice. Exercise valid input, a relevant error and state
persistence when the feature saves data. Run focused checks, then required project
checks. Share the observable result and the boundaries not exercised. New
infrastructure or broad cleanup belongs here only when the feature requires it.
