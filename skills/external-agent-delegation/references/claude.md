# Claude role

Treat Claude as a cheap, high-throughput bounded executor. In this environment it may be backed by a weaker model, so optimize tasks for objective verification rather than judgment.

## Good work for Claude

Prefer Claude for work that is simple, token-heavy, repetitive, and measurable:

- run tests, builds, linters, formatters, benchmarks, or existing repro commands;
- execute a known command matrix and summarize failures;
- inspect large logs and extract errors, timings, counts, repeated patterns, or suspicious windows;
- cluster or deduplicate repetitive diagnostics;
- compare large textual outputs when the comparison rule is explicit;
- perform mechanical checks against an explicit checklist;
- summarize verbose execution output into a compact result.

A delegated task should specify:

1. bounded input/scope;
2. exact operation or commands;
3. objective completion signal;
4. whether edits are forbidden;
5. required output fields.

Example:

```text
Run `mvn -pl connector-mysql test`.
Do not edit files.
Return failing test names, the first causal error for each failure,
and relevant log locations. Do not propose architecture changes.
```

Example:

```text
Inspect logs/run.jsonl.
Extract operations slower than 2s, group by operation name,
and report count / p50 / p95 / max plus the five slowest examples.
Do not infer causes unless directly supported by the log.
```

## Do not use Claude for

- architecture or solution design;
- open-ended implementation decisions;
- domain modeling;
- subtle code review;
- choosing a root cause from weak evidence;
- modifying production/business code;
- tasks whose correctness cannot be cheaply checked by Codex.

If Claude returns interpretation rather than evidence, treat it as untrusted input and verify it.
