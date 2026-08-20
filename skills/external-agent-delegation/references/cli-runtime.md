# Wrapper runtime contract

This file documents `scripts/external_agent.py` internals. **Do not load it for ordinary delegation.** The wrapper implements these rules deterministically so the model does not need to reason through them on every call.

## Capability discovery

- Resolve the installed executable from `PATH`.
- Read `--version` on each invocation (local/no model call).
- Cache `--help` capability detection by executable+version.
- Prefer subprocess `cwd`/tool workdir; never require a CLI-specific `--cwd`.
- Only pass optional flags that the installed CLI advertises.

## Transport parsing

Structured CLI stdout may be layered:

```text
outer CLI JSON
  -> runtime/session/cost metadata
  -> result string
      -> optional fenced JSON
          -> semantic JSON/text
```

The wrapper parses this into stable top-level `runtime`, `transport`, and normalized `result` fields. It preserves reported actual model/service-tier/cost metadata instead of inferring model identity from the CLI name.

## Cost and health

`--health` and `--dry-run` must never invoke a model. Model-backed probes are intentionally not part of the wrapper health path. `--max-cost-usd` is a post-call warning threshold when reported cost is available.

## Encoding

Subprocess bytes are decoded UTF-8 first with locale fallback. Semantic output is scanned for obvious mojibake/replacement markers such as `锟斤拷` or `�`; suspicious values are surfaced in `encoding_suspects` rather than silently trusted.

## Permission handling

AGY permission failures are normalized to `permission_blocked`. If the installed CLI advertises a dangerous bypass, the wrapper may return a retry hint but must never auto-retry. Dangerous mode requires both an explicit mode argument and an acknowledgement flag; the surrounding agent is responsible for obtaining user authorization first.
