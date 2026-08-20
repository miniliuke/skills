# External CLI invocation

Use the repository root as the working directory unless the task is intentionally narrower. Prompts must state scope, permissions, completion criteria, and output shape.

## Claude

Typical headless call:

```powershell
claude -p "<bounded task; include commands, constraints, and required output>" --output-format json
```

For test/log chores, default to no file edits.

Prefer this split:

```text
Claude: run / extract / measure -> evidence
Codex: reason -> decide -> fix
```

Do not ask Claude to "investigate and fix" an open-ended problem.

Suggested result contract:

```text
status
commands_run
failures_or_findings
measurements
relevant_paths_or_log_locations
unresolved_items
```

## AGY

For read-only investigation or review, prefer plan mode:

```powershell
agy -p "<repository investigation/review task; do not edit files>" --cwd "$PWD" --mode=plan --output-format json
```

For explicitly delegated documentation edits:

```powershell
agy -p "Update <specific docs> from verified repository facts. Do not edit source code." --cwd "$PWD" --mode=accept-edits --output-format json
```

Suggested result contract:

```text
summary
files_examined
findings (with file/symbol references)
risks
missing_tests_or_docs
recommended_followups
```

Prefer paths, symbols, command names, failing tests, measurements, and concrete evidence over long prose.

Do not rely on prose in the prompt as a security boundary. Use the CLI's configured permissions/sandbox when available.
