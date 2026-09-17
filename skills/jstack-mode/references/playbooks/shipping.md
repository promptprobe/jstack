# Shipping

Resolve the intended remote, branch, artifact and existing authorization. Inspect
the diff for unrelated work, generated logs and secrets. Run required checks
against the content to be published. Keep failures visible.

Perform only the authorized publication action. Verify the remote SHA matches the
intended commit. If CI is part of delivery, inspect checks on that SHA; queued,
cancelled and billing-blocked runs are not passing. If deployment is requested,
confirm the deployed revision and exercise its live route separately. Record those
facts with sources. A push is complete when the remote content is confirmed; it is
not evidence of a healthy deployment.
