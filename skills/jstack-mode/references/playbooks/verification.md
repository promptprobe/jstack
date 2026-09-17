# Verification

Identify the exact revision or artifact and the claim being tested. Build a short
map from acceptance conditions to evidence. Start with the highest-risk condition
whose failure would change the decision.

Run relevant checks and exercise the actual entry point where available. For saved
state, reopen and read it back. For an export, inspect the produced file. Keep
inspection-only tasks read-only apart from local evidence; ask before expanding
into repair when repair was not requested. Report failures, missing coverage and
environment blocks separately. Reverify after a material change, not after every
commentary update.
