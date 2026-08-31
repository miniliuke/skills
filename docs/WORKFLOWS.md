# Task Routing Guide

This repository is not a default development workflow. Ponytail handles complexity pressure; the baseline engineering guardrail handles architecture safety and lightweight TDD; skills are reserved for specialist work.

## Default path: ordinary development

```text
Requirement / bug / refactor / UI / config
  -> Ponytail
  -> native Plan / Execute
  -> guardrails/engineering.md
  -> focused tests / lightest useful verification
  -> done
```

Do not call `architecture`, `codebase-design`, `domain-modeling`, or `diagnosing-bugs` merely because code is being changed.

## Architecture work

Use `architecture` when the task itself asks for architecture design, structural change, architecture review, architecture documentation, or architecture health analysis.

```text
Architecture request
  -> architecture
       Design | Change | Review | Document | Health
  -> native Plan / Execute when implementation is requested
```

The skill chooses one primary mode. Do not run all modes in sequence.

Examples that justify architecture work:

- designing a new project, subsystem, module, plugin, or extension seam;
- deliberately moving ownership or changing dependency direction;
- changing a load-bearing public seam or runtime/data-flow boundary;
- reviewing a plan/diff/PR for architecture conformance;
- bootstrapping, updating, or reconciling `ARCHITECTURE.md`;
- explicit structural-health or architecture-improvement analysis.

A small feature that happens to touch several files is not automatically architecture work.

## Deep module / interface design

Use `codebase-design` when the actual problem is where a seam belongs, what an interface should expose, or how to make a load-bearing module deeper and more coherent.

Do not require it before every new class/package/module. Ponytail's minimum-design pressure still applies.

## Domain modeling

Use `domain-modeling` when the difficult part is the meaning of concepts, terminology, states, invariants, or lifecycle ownership.

Do not invoke it merely because a request introduces a field, DTO, table column, endpoint parameter, or another ordinary data shape.

## Difficult diagnosis

Use `diagnosing-bugs` for failures that need a real diagnosis loop: hard reproduction, uncertain causal chain, multi-system incidents, or performance regressions.

For an obvious local bug:

```text
reproduce -> regression test when practical -> smallest fix -> focused tests
```

No diagnosis workflow is needed.

## Stress-testing a plan

Use `grilling` only when the user explicitly wants a plan/design/decision challenged through an interview.

There are no `grill-me` or `grill-with-docs` wrappers. If domain modeling is independently needed after grilling, invoke it because the domain is genuinely unresolved, not because a wrapper chained it.

## Agent-facing writing

Use `writing-for-agents` when producing durable instructions or context specifically meant for coding agents.

## Architecture memory

Keep these separate:

```text
CONTEXT.md
  canonical domain language

docs/adr/
  consequential decisions and rationale

ARCHITECTURE.md
  verified current structural truth and active constraints
```

Planned target architecture belongs in a plan/spec/ADR until it actually lands. Do not write future architecture as current-state truth.

## Routing rules

```text
1. Ponytail is always-on complexity pressure.
2. Ordinary development uses native agent behavior + minimal guardrails.
3. Skills are specialist tools, not mandatory phases.
4. Prefer one primary skill per task.
5. Never create a fixed skill cascade.
6. Read narrowly; do not scan the whole repository to prove compliance.
```
