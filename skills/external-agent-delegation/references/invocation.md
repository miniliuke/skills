# Wrapper invocation

Ordinary external-agent calls go through `scripts/external_agent.py`; raw CLI syntax is an implementation detail.

## Common calls

```text
python scripts/external_agent.py claude --task "Run the specified tests and summarize failures" --workdir .
python scripts/external_agent.py agy --task "Map callers and dependencies for X" --workdir .
```

For long/multiline prompts:

```text
python scripts/external_agent.py claude --task-file task.txt --workdir .
```

Useful local-only checks:

```text
python scripts/external_agent.py claude --health --pretty
python scripts/external_agent.py agy --task "..." --dry-run --pretty
python scripts/external_agent.py --self-test --pretty
```

`--health` performs only executable/version/help discovery. `--dry-run` validates capabilities and constructs the command without invoking a model. Capability help is cached by executable+version and refreshed automatically when the version changes; use `--refresh-capabilities` to force it.

## Stable output contract

The wrapper emits one JSON object:

```text
schema_version
ok
agent
cli { executable, version, capabilities_cache_hit }
execution { workdir, exit_code, duration_ms, mode, permission_mode }
runtime { actual_model, service_tier, cost_usd, usage/model_usage }
transport { selected session/duration/error metadata }
result
warnings[]
encoding_suspects[]
error
```

`result` is already normalized: if the CLI emitted an outer JSON envelope with a `result` string containing a fenced JSON block, the wrapper removes the fence and parses the inner JSON. Callers should consume `result` directly and retain `runtime` for model/cost accounting.

Use `--max-cost-usd N` to flag `COST_BUDGET_EXCEEDED` after a call when the CLI reports cost. This is accounting/feedback, not a pre-call hard limit unless the underlying CLI exposes one.

## Modes

Default mode is `read-only`. Use `--mode docs-edit` only for explicitly scoped documentation edits.

For AGY, dangerous permission bypass is never automatic. A retry is allowed only after explicit user authorization:

```text
python scripts/external_agent.py agy --task "..." \
  --permission-mode dangerous --ack-dangerous-permissions
```

If the installed AGY does not advertise the dangerous flag, the wrapper refuses the request.

## Raw CLI fallback

Bypass the wrapper only while debugging/adapting it. In that case inspect the installed CLI's local `--help`; do not copy flags from old docs or another machine.
