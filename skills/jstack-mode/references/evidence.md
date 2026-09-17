# Evidence without inflated claims

An acceptance condition describes what a user can observe. A test name describes
one way to check it. Keep both: a passing unit test may not cover the whole flow.

| Evidence | Supports | Does not establish |
| --- | --- | --- |
| Source inspection | A code path exists; a likely mechanism | Runtime execution |
| Local command receipt | Command, exit, duration, source fingerprint | Complete user acceptance |
| Browser or runtime observation | The exercised scenario at the observed time | Unvisited scenarios |
| Remote commit / CI link | Published SHA / checks on that SHA | Live deployment health |
| Live artifact or endpoint | The particular response, download or behavior | Future availability |

Use high confidence for direct, relevant, repeatable evidence; moderate for partial
coverage or a well-supported inference; low for tentative explanations; unknown
when not observed. Source references should be inspectable paths, commands,
receipts, or URLs. Never invent a source. Scrub captured output before sharing.

The helper's receipts are local mutable JSON files, not signed attestations. It
does not evaluate natural-language acceptance or verify supplied URLs. Its source
fingerprint covers Git-visible files, not ignored inputs, symlink targets,
submodules, databases, dependencies, environment changes or external services.
Re-run checks when those inputs change even if the fingerprint is unchanged.

For a concise final response, state: outcome; evidence and confidence; what failed
or remains unknown; next action only if useful. Do not dump the full receipt unless
requested. An unavailable test environment is a limitation, not a passing test.
