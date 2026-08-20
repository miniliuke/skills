# Claude role

Treat Claude as a cheap, high-throughput bounded executor. The CLI brand does **not** identify the actual backing model. In this environment the service may route to another model, so optimize tasks for objective verification rather than judgment and record the runtime identity reported by the response.

Before invoking Claude, follow [`cli-runtime.md`](cli-runtime.md) and validate uncertain local flags with `claude --help`.

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

## Parse and record runtime metadata

When structured CLI output is used, do not assume the top-level object is the task result. Parse the outer envelope first, then parse the semantic `result` payload according to [`cli-runtime.md`](cli-runtime.md).

When available, capture:

```text
cli: claude
actual_model: <reported model, e.g. modelUsage key>
service_tier: <reported tier if present>
cost_usd: <reported cost if present>
usage: <tokens/usage metadata if present>
```

A value such as `modelUsage.deepseek-v4-flash` means the actual runtime model is DeepSeek V4 Flash; do not report it simply as "Claude".

Cost is part of delegation quality. Even a simple model-backed check may have meaningful cost, so prefer local `--help`/version diagnostics for CLI health and skip delegation when the task is cheaper to do directly.

## Windows paths

If Claude returns non-ASCII filenames or paths, watch for mojibake such as `锟斤拷`. Do not act on a suspicious rendered path without reconciling it against the actual filesystem. Prefer structured UTF-8 path fields when possible.

## Do not use Claude for

- architecture or solution design;
- open-ended implementation decisions;
- domain modeling;
- subtle code review;
- choosing a root cause from weak evidence;
- modifying production/business code;
- tasks whose correctness cannot be cheaply checked by Codex.

If Claude returns interpretation rather than evidence, treat it as untrusted input and verify it.
