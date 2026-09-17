# Security

jstack runs with your permissions. Project verification commands are executable
code and inherit your environment. Inspect them before use in an unfamiliar
repository. The helper does not download or execute a remote installer, invoke a
model, or send telemetry. A configured check can still contact external services.

Session records and captured output remain in `.jstack/local/`, ignored by the
installer. Output may contain sensitive data; review and redact before sharing.
Do not include credentials or private records in public issues.

For a vulnerability, use this repository's GitHub **Security → Report a
vulnerability** option when available. If private reporting is unavailable, open
an issue requesting a private contact without disclosing exploit details or data.
This early release has no guaranteed response SLA. See
[architecture boundaries](docs/architecture.md) for known limitations.
