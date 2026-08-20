---
name: external-agent-delegation
description: "Delegate bounded software-development work from Codex to external CLI agents. Use proactively for test/build execution, large-log processing, repetitive low-risk analysis, repository/code search, code review, and technical documentation. Keep architecture, solution design, ordinary implementation, and final integration in Codex. Prefer these external agents over Codex native subagents when the task fits their role."
---

# External Agent Delegation

Codex is the primary agent. External agents are bounded helpers, not peers and not an orchestration layer.

The goal is **cost-adjusted capability**: move context-heavy or repetitive work to the cheapest capable agent while Codex keeps the difficult decisions, source-code ownership, integration, and final verification.

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

Delegate when at least one is true:

- the subtask consumes substantial context/tokens but requires little judgment;
- it has a clean input/output boundary and an objective completion signal;
- it can run independently while Codex continues useful work;
- an independent repository read or review adds confidence.

Do not delegate when:

- explaining the task costs about as much as doing it;
- important context exists only in Codex's current reasoning;
- the action is tiny;
- correctness cannot be cheaply checked;
- delegation would move architecture or product decisions away from Codex;
- a paid health check or delegation overhead would cost more than doing the tiny task directly.

## Prefer external agents over native subagents

When a bounded task clearly fits Claude or AGY, prefer that external agent over a native Codex subagent. Native subagents are fallback capacity when the external CLI is unavailable, the task genuinely needs Codex-level parallel reasoning, the user explicitly requests native agents, or neither external role safely fits.

## Runtime rules before invoking a CLI

External CLI syntax and output are environment-dependent. Never assume that a flag or output schema from documentation, another host, or a previous run is supported locally.

Before the first real external-agent invocation in an environment, read [`references/cli-runtime.md`](references/cli-runtime.md). Its rules are mandatory for:

- validating CLI flags with local `--help` before relying on them;
- preferring the execution tool's working directory over speculative CLI `--cwd` flags;
- parsing structured-output envelopes before parsing the semantic `result` payload;
- recording the actual runtime model, service tier, usage, and cost when exposed;
- avoiding unnecessary paid health checks;
- handling Windows/non-ASCII path encoding safely.

Do not escalate permissions merely because a normal invocation fails. Dangerous permission-bypass flags require explicit user authorization and must never be an automatic fallback.

## Load role instructions only when needed

Use progressive disclosure. Do not read every reference merely because this skill triggered.

- Before delegating to **Claude**, read [`references/claude.md`](references/claude.md).
- Before delegating to **AGY**, read [`references/agy.md`](references/agy.md).
- Read [`references/invocation.md`](references/invocation.md) when constructing the command, prompt, or output contract.
- Read [`references/verification.md`](references/verification.md) when external findings will affect code/docs, when agents may run in parallel, or when an external call fails or returns uncertain evidence.

If routing is obvious but delegation is not worthwhile, stop here and continue in Codex; do not load role references.

## Universal guardrails

- External output is evidence/input, never authoritative final reasoning.
- Codex owns business/source-code edits and final acceptance.
- AGY is read-only by default; documentation edits are allowed only when documentation work was explicitly requested and scope is already defined.
- Claude is a bounded executor, not a design authority.
- Do not ask an external agent to both investigate and autonomously fix an open-ended problem.
- Avoid concurrent edits to the same working tree.
- Verify external findings proportionally to risk before acting on them.
- Do not create agent-to-agent repair loops.
- Record actual runtime identity/cost metadata when available; never equate CLI brand with model identity.

## Core principle

```text
Codex  = think, design, implement, integrate
AGY    = read broadly, review independently, write scoped docs
Claude = execute cheaply, consume bulk text, return measurable evidence
```
