---
name: architecture-workflow
description: "Route software development work to the lightest architecture workflow. Use when planning a new project, new module, cross-module feature, architecture refactor, or when deciding whether domain modeling, codebase design, specs, tickets, or architecture review are actually necessary."
---

# Architecture Workflow

Use native agent Plan Mode as the default planning engine. Do not create process for its own sake.

Your job is to detect when a task carries **architectural risk** and add only the specialized reasoning needed to keep the codebase coherent over time.

## First: classify the task

Choose exactly one primary mode.

### A. Ordinary change

Use when the change:

- stays inside an existing module and seam;
- does not introduce a new domain concept;
- does not change a public interface or dependency direction;
- does not create a new module.

Workflow:

```text
Native Plan Mode -> Execute -> Tests -> Review
```

Do not invoke architecture workflows just to make the task look rigorous.

### B. New project / major subsystem from scratch

Use `new-project-architecture` if available.

Otherwise:

1. Clarify product goals, constraints, external systems, important quality attributes, and explicit non-goals.
2. Use `domain-modeling` if installed to establish canonical domain language.
3. Use `codebase-design` if installed to design deep modules and stable seams.
4. Use native Plan Mode to turn those decisions into an implementation plan.
5. Create a compact `ARCHITECTURE.md` only after the structural decisions are coherent.
6. Create ADRs only for hard-to-reverse, non-obvious trade-offs.

### C. New module / plugin / subsystem in an existing project

Use `new-module-architecture` if available.

The module must earn its existence. Check:

- Does it own a coherent responsibility or domain concept?
- Does it hide meaningful complexity behind a smaller interface?
- Is there a real seam, or are we creating an abstraction for a single implementation?
- Can callers use it without understanding its internals?
- Can tests target its public interface?
- Does it preserve dependency direction?

### D. Architecture-changing feature or refactor

Use `architecture-change` if available.

Escalate here when any of these changes:

- module ownership;
- public interface / SPI;
- dependency direction;
- runtime/data flow;
- domain lifecycle or state ownership;
- persistence or integration seam;
- compatibility contract.

Require an Architecture Impact block in the plan.

### E. Review

Use `architecture-review` when a plan, diff, branch, or PR exists and architectural conformance needs checking.

### F. Periodic architecture maintenance

Use `architecture-health` when the user asks to improve structure globally, or when repeated development friction suggests the architecture itself is becoming the bottleneck.

## When to use Matt Pocock skills

### `domain-modeling`

Use when the **problem vocabulary changes**:

- a new core term is introduced;
- one word is overloaded;
- state/lifecycle ownership is unclear;
- two concepts are being collapsed incorrectly;
- code and the stated domain model disagree.

Do not use it merely to read `CONTEXT.md`.

### `codebase-design`

Use when the **software shape changes**:

- placing a seam;
- designing an interface;
- introducing/deepening a module;
- improving information hiding;
- making the code testable through stable public behavior.

Prefer deep modules: meaningful behavior behind a small interface.

Fallback principles when the skill is unavailable:

- The interface is every fact a caller must know, not just method signatures.
- Prefer high leverage: a small surface should unlock substantial behavior.
- Keep related behavior local.
- Do not introduce a seam just because an abstraction is imaginable.
- A single implementation is weak evidence for a new polymorphic seam.
- Apply the deletion test: if deleting a module merely removes pass-through code, the module was probably shallow.

### `code-review`

Use it for implementation correctness and spec/standards review. Architecture review is a separate axis; do not assume ordinary code review covers it.

### `improve-codebase-architecture`

Use it for periodic structural surveys, not before every feature.

## Native Plan Mode contract

For architecture-relevant work, the plan must include:

```markdown
## Architecture Impact

Affected modules:
Existing seams reused:
New or changed seams:
Domain concepts changed:
Dependency changes:
Public contract changes:
Runtime/data-flow changes:
Migration/compatibility concerns:
ADRs affected:
ARCHITECTURE.md changes:
Risks:
```

Omit rows that are genuinely irrelevant; do not invent impact.

## Persistent architecture memory

Read these when present before structural work:

- `CONTEXT.md` / `CONTEXT-MAP.md`
- relevant `docs/adr/`
- `ARCHITECTURE.md`
- local module READMEs or design docs that the repo already treats as authoritative

Use them differently:

- `CONTEXT.md`: vocabulary, no implementation diary.
- ADRs: consequential decisions and rationale.
- `ARCHITECTURE.md`: current structural contract.

If documentation conflicts with executable reality, surface the conflict. Do not silently choose whichever source supports the proposed plan.

## Do not create a spec or tickets by default

Native Plan Mode is enough for ordinary single-agent work.

Use a durable spec only when the work must survive context loss, coordinate multiple people/agents, or preserve a core contract decision.

Use tickets only when they create useful execution boundaries: parallel ownership, resumability, or explicit blocking order.

## Guardrails

- Prefer extending an existing abstraction over creating a parallel one.
- Before introducing a new abstraction, identify overlapping abstractions and explain why they cannot be extended.
- Do not add an architecture layer to satisfy a pattern name.
- Do not force DDD, Clean Architecture, hexagonal architecture, or microservices onto a codebase that does not need them.
- Preserve useful existing conventions unless there is concrete evidence that changing them pays for the migration cost.
- Distinguish structural debt from style preferences.
