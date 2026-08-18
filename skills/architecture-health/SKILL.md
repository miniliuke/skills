---
name: architecture-health
description: "Periodically inspect an evolving codebase for architecture friction, shallow modules, concept drift, dependency problems, and repeated change hotspots. Use for architecture optimization, maintainability reviews, or when the codebase is getting harder for agents or humans to navigate."
disable-model-invocation: true
---

# Architecture Health

Run this as periodic maintenance, not as a mandatory step for every feature.

If `improve-codebase-architecture` is installed, use it as the primary deep-module survey and supplement it with the architecture contract checks below.

## 1. Scope by change pressure

Prefer areas that are actively changing.

Use evidence such as:

- recent commit hotspots;
- files/modules repeatedly changed together;
- recurring bugs around the same seam;
- review comments that repeat;
- tests that frequently need updates during internal refactors;
- repeated navigation across many files to understand one behavior.

If the user names a subsystem, scope there first.

## 2. Read architecture memory

Read:

- `ARCHITECTURE.md`;
- relevant `CONTEXT.md`;
- relevant ADRs.

Do not re-propose a decision an ADR intentionally settled unless there is new, concrete pressure strong enough to reopen it.

## 3. Look for high-signal architecture friction

### Shallow modules

Signs:

- forwarding/wrapping dominates;
- callers still need to understand the implementation;
- deleting the module mostly deletes indirection.

### Scattered behavior

Signs:

- one domain behavior requires editing many unrelated modules;
- invariants are enforced in multiple places;
- callers recreate the same orchestration.

### Parallel abstractions

Signs:

- multiple types/interfaces represent the same domain responsibility;
- old and new approaches both continue indefinitely;
- adapters exist only to translate between duplicate internal models.

### Dependency erosion

Signs:

- cycles;
- core importing leaf/implementation modules;
- upper layers importing concrete integrations;
- broad "common" modules becoming dependency sinks.

### Leaky implementation variation

Signs:

```text
if database == mysql
if connector_type == ...
if provider == ...
```

outside the module that should own that variation.

### Domain drift

Signs:

- canonical terms used inconsistently;
- one concept has multiple lifecycle owners;
- code semantics no longer match the glossary.

### Test-surface friction

Signs:

- tests mock many internal collaborators;
- simple internal refactors require many test changes;
- there is no stable public seam for important behavior.

## 4. Prioritize, do not dump

Return at most 3 primary candidates unless the user asks for exhaustive coverage.

For each:

```markdown
## Candidate: <name>

Pressure:
Evidence:
Current seam:
Why it is shallow/leaky/scattered:
Proposed direction:
Expected leverage:
Migration size:
Risk:
Recommendation strength: Strong | Worth exploring | Speculative
```

Prefer candidates that improve future change cost in hot parts of the codebase.

## 5. Respect YAGNI

Do not propose:

- new interfaces for hypothetical future adapters;
- large rewrites for stylistic uniformity;
- microservice extraction without operational/domain pressure;
- generic platform layers that merely centralize code;
- refactors whose only benefit is "cleaner".

A good architecture improvement should reduce the amount of context a future maintainer/agent must load to make a correct change.

## 6. From diagnosis to change

After a candidate is selected, switch to the `architecture-change` workflow:

1. state the concrete pressure;
2. model domain changes if any;
3. redesign the seam;
4. plan migration;
5. implement incrementally;
6. architecture-review the result.

## Output ending

Always end with one top recommendation and why it has the best ratio of future leverage to migration risk.
