---
name: external-agent-delegation
description: "Delegate bounded software-development work from Codex to external CLI agents. Use proactively for test/build execution, large-log processing, repetitive low-risk analysis, repository/code search, code review, and technical documentation. Keep architecture, solution design, ordinary implementation, and final integration in Codex. Prefer these external agents over Codex native subagents when the task fits their role."
---

# External Agent Delegation

Codex is the primary agent. External agents are bounded helpers, not peers and not an orchestration layer.

## Routing

| Work | Default owner |
| --- | --- |
| Architecture / solution / trade-offs | Codex |
| Domain modeling / plan decisions | Codex |
| Ordinary implementation / bug fixes | Codex |
| Complex root-cause reasoning | Codex |
| Tests / builds / lint / benchmarks | Claude |
| Large logs / repetitive deterministic analysis | Claude |
| Repository search / code navigation | AGY |
| Call-chain / dependency investigation | AGY |
| Code / diff review | AGY |
| Technical documentation drafting | AGY |
| Final synthesis / edits / verification | Codex |

Split only the bounded subtask that fits an external role. Keep the parent task in Codex.

## Delegation threshold

Delegate when the subtask is context-heavy/repetitive but low-judgment, has a clean input/output boundary, can run independently, or benefits from an independent repository read/review.

Do not delegate tiny work, work whose explanation costs as much as execution, work that depends on private in-flight reasoning, or work whose correctness cannot be cheaply checked. Cost matters: if external-agent overhead is comparable to doing the task directly, keep it in Codex.

## Use the wrapper, not raw CLI calls

For ordinary delegation invoke [`scripts/external_agent.py`](scripts/external_agent.py). It owns CLI capability discovery/caching, tool-level `workdir`, structured-output normalization, outer/inner JSON parsing, actual model/service-tier/cost extraction, Windows encoding warnings, and permission-block detection.

```text
python scripts/external_agent.py claude --task "<bounded task>" --workdir .
python scripts/external_agent.py agy --task "<repository task>" --workdir .
```

For long prompts prefer `--task-file`. `--health` and `--dry-run` are local-only and must not call a model.

Do not bypass the wrapper unless debugging or adapting the wrapper itself.

The wrapper does **not** decide whether to delegate, how to split the task, whether findings are trustworthy, or whether code should change. Those remain Codex responsibilities.

## Load only role-specific guidance

Use progressive disclosure:

- Before delegating to **Claude**, read [`references/claude.md`](references/claude.md).
- Before delegating to **AGY**, read [`references/agy.md`](references/agy.md).
- Read [`references/verification.md`](references/verification.md) only when findings affect code/docs, agents run in parallel, or results are uncertain/failing.
- Read [`references/invocation.md`](references/invocation.md) only for wrapper options, output schema, or wrapper debugging.
- `references/cli-runtime.md` documents wrapper internals; do not load it for ordinary delegation.

## Permission boundary

Never automatically escalate AGY permissions. If the wrapper returns `permission_blocked` with `requires_explicit_authorization: true`, stop and obtain explicit user authorization before retrying with dangerous permission mode. Dangerous mode must be explicit in the wrapper call and acknowledged with `--ack-dangerous-permissions`.

## Universal guardrails

- External output is evidence/input, never authoritative final reasoning.
- Codex owns business/source-code edits and final acceptance.
- AGY is read-only by default; scoped documentation edits are allowed only when explicitly requested.
- Claude is a bounded executor, not a design authority.
- Prefer external agents over native Codex subagents when a bounded task clearly fits; native subagents are fallback capacity.
- Avoid concurrent edits to the same working tree.
- Verify external findings proportionally to risk.
- Do not create agent-to-agent repair loops.

```text
Codex  = think, design, implement, integrate
AGY    = read broadly, review independently, write scoped docs
Claude = execute cheaply, consume bulk text, return measurable evidence
```
