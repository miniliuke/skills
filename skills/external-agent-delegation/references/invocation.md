# External CLI invocation

Use the execution tool's working directory as the default repository context. Add a CLI-specific cwd flag only if the locally installed CLI supports it and the task actually needs it.

Before constructing a real command, follow [`cli-runtime.md`](cli-runtime.md): validate uncertain flags with local `--help`, treat structured output as a transport envelope, and record runtime/cost metadata exposed by the CLI.

Prompts must state scope, permissions, completion criteria, and output shape.

## Claude

A typical headless shape may be:

```powershell
claude -p "<bounded task; include commands, constraints, and required output>" --output-format json
```

Treat this as an example, not a guaranteed contract. Verify supported flags locally before relying on them.

For test/log chores, default to no file edits.

Prefer this split:

```text
Claude: run / extract / measure -> evidence
Codex: reason -> decide -> fix
```

Do not ask Claude to "investigate and fix" an open-ended problem.

Suggested semantic result contract:

```text
status
commands_run
failures_or_findings
measurements
relevant_paths_or_log_locations
unresolved_items
```

If `--output-format json` returns an outer object whose `result` is a string, parse the outer envelope first. If `result` contains a fenced JSON block, strip the fence and parse that inner value separately. Preserve outer metadata such as model usage, cost, service tier, duration, session id, and errors.

## AGY

Do not hard-code `--cwd` or sandbox/permission flags. The execution tool's `workdir` is sufficient unless local `agy --help` confirms another mechanism is required.

For read-only investigation or review, construct the command from flags verified by the installed binary. Prefer the least-privileged mode that actually works.

For explicitly delegated documentation edits, allow edits only after the user requested documentation work and Codex has already bounded the documentation paths.

Suggested semantic result contract:

```text
summary
files_examined
findings (with file/symbol references)
risks
missing_tests_or_docs
recommended_followups
```

If normal AGY permissions or supported sandbox modes are blocked by the local environment, do not automatically add a permission-bypass flag. A flag such as `--dangerously-skip-permissions` is a separate high-risk degradation path and requires explicit user authorization before use.

Prefer paths, symbols, command names, failing tests, measurements, and concrete evidence over long prose.

Do not rely on prose in the prompt as a security boundary. Use verified CLI permissions plus the surrounding execution sandbox/tool permissions when available.
