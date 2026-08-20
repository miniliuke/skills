# Wrapper invocation

Ordinary external-agent calls go through the wrapper under this skill directory; raw CLI syntax is an implementation detail.

## Resolve the wrapper path

Resolve `SKILL_DIR` from the actual path of this skill's `SKILL.md`, then build:

```text
WRAPPER = <absolute SKILL_DIR>/scripts/external_agent.py
```

Do not assume the task repository contains `scripts/external_agent.py`.

Examples below use `$SKILL_DIR` as a resolvable placeholder for that absolute directory:

```text
python "$SKILL_DIR/scripts/external_agent.py" claude --task "Run the specified tests and summarize failures" --workdir . --require-field status
python "$SKILL_DIR/scripts/external_agent.py" agy --task "Map callers and dependencies for X" --workdir . --require-field summary --require-field findings
```

For long/multiline prompts:

```text
python "$SKILL_DIR/scripts/external_agent.py" claude --task-file task.txt --workdir . --require-field status
```

Useful local-only checks:

```text
python "$SKILL_DIR/scripts/external_agent.py" claude --health --pretty
python "$SKILL_DIR/scripts/external_agent.py" agy --task "..." --dry-run --pretty
python "$SKILL_DIR/scripts/external_agent.py" --self-test --pretty
```

`--health` performs only executable/version/help discovery. `--dry-run` validates capabilities and constructs the command without invoking a model. Capability help is cached by executable+version and refreshed automatically when the version changes; use `--refresh-capabilities` to force it.

## Result contract

Wrapper schema version 2 distinguishes process success from semantic result success.

Default `--result-format json` expects a JSON object. Override when needed:

```text
--expect-result object
--expect-result array
--expect-result json
--result-format text
```

Declare fields Codex relies on with repeatable dotted paths:

```text
--require-field status
--require-field findings
--require-field measurements.p95
```

Declare success values when applicable:

```text
--require-value status=ok
--require-value success=true
```

`VALUE` is parsed as JSON when possible; otherwise it is treated as a string.

`ok: true` requires all of the following:

1. CLI exit code is 0;
2. transport metadata does not report an error;
3. result matches the expected type;
4. every required field exists;
5. every required value matches.

If JSON was expected but the semantic result is a non-JSON string, the wrapper adds `RESULT_SCHEMA_UNEXPECTED` and returns `ok: false`.

Other contract warnings include:

```text
RESULT_REQUIRED_FIELDS_MISSING
RESULT_REQUIRED_VALUE_MISMATCH
```

## Stable output contract

The wrapper emits one JSON object:

```text
schema_version
ok
agent
cli { executable, version, capabilities_cache_hit }
execution { workdir, exit_code, duration_ms, mode, permission_mode }
runtime {
  metadata_status,
  actual_model,
  service_tier,
  cost_usd,
  usage/model_usage,
  missing[],
  reported_fields[]
}
transport { selected session/duration/error metadata }
result_contract {
  valid,
  expected_type,
  required_fields[],
  required_values{},
  missing_fields[],
  value_mismatches[],
  actual_type
}
result
warnings[]
encoding_suspects[]
error
```

`result` is normalized: if the CLI emitted an outer JSON envelope with a `result` string containing a fenced JSON block, the wrapper removes the fence and parses the inner JSON.

For Claude, absent model or cost metadata is never represented as an ambiguous empty runtime object. The wrapper reports null values plus `metadata_status`/`missing`, and emits:

```text
RUNTIME_MODEL_METADATA_MISSING
RUNTIME_COST_METADATA_MISSING
```

Use `--max-cost-usd N` to flag `COST_BUDGET_EXCEEDED` after a call when the CLI reports cost. This is accounting/feedback, not a pre-call hard limit unless the underlying CLI exposes one.

## Modes

Default mode is `read-only`. Use `--mode docs-edit` only for explicitly scoped documentation edits.

AGY permission escalation is never automatic. Follow [`agy.md`](agy.md) for the explicit-authorization boundary and supported retry procedure.

## Raw CLI fallback

Bypass the wrapper only while debugging/adapting it. In that case inspect the installed CLI's local `--help`; do not copy flags from old docs or another machine.
