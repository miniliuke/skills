# Claude role

Treat Claude as a cheap, high-throughput bounded executor. The CLI brand is not the runtime model identity; use the wrapper's `runtime.actual_model`, service tier, usage, and cost when available.

## Good work for Claude

Prefer Claude for simple, token-heavy, repetitive, objectively verifiable work:

- run tests, builds, linters, formatters, benchmarks, or known repro commands;
- execute a command matrix and summarize failures;
- inspect large logs and extract errors, timings, counts, repeated patterns, or suspicious windows;
- cluster/deduplicate repetitive diagnostics;
- compare large textual outputs with an explicit rule;
- mechanical checklist checks;
- summarize verbose execution output.

A delegated task should have bounded scope, concrete operations, an objective completion signal, explicit edit permissions, and a compact result contract.

When Codex depends on particular result fields, pass wrapper `--require-field`; when success requires a specific value, pass `--require-value`. Do not treat CLI exit code 0 alone as a successful delegation.

Example task contract:

```text
Run `mvn -pl connector-mysql test`.
Do not edit files.
Return JSON with status, failures_or_findings, and unresolved_items.
Set status=ok only if the requested command completed.
```

## Runtime identity and cost

Do not spend a model call merely to check whether Claude CLI exists; use wrapper `--health`. For tiny tasks, keep work in Codex when delegation overhead or observed cost is disproportionate.

After calls, retain the wrapper's runtime cost/model metadata so future routing can be calibrated from real usage. If Claude reports no model or cost metadata, do not infer it: the wrapper exposes `runtime.metadata_status`, `runtime.missing`, and explicit missing-metadata warnings.

## Do not use Claude for

- architecture or solution design;
- open-ended implementation decisions;
- domain modeling;
- subtle code review;
- choosing a root cause from weak evidence;
- modifying production/business code;
- tasks whose correctness cannot be cheaply verified.

Treat interpretations as untrusted input until Codex verifies the evidence.
