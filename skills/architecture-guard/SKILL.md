---
name: architecture-guard
description: "Lightweight architecture guardrail for ordinary development. Use implicitly during coding to prevent accidental boundary, dependency, ownership, and public-contract violations without running an architecture workflow."
---

# Architecture Guard

Keep architecture coherent without turning normal development into an architecture exercise.

This is a guardrail, not a workflow. Do not create extra planning stages, design sessions, reports, specs, or architecture documents because this skill is present.

## Default behavior

For ordinary bugs, features, tests, refactors, configuration changes, and UI work:

1. Use the agent's normal planning/execution flow.
2. Check only architecture rules relevant to the code being changed.
3. Continue immediately when no conflict is found.

Do not automatically invoke `architecture`, `domain-modeling`, `codebase-design`, or another design workflow.

## Read narrowly

Only read architecture documentation when the change may touch a structural boundary.

Prefer:

- a short `ARCHITECTURE.md` or architecture index;
- the affected module's README/design doc;
- relevant ADRs;
- broader architecture documents only when necessary.

Do not scan the whole repository merely to prove architectural compliance.

## Check four things

### 1. Ownership

Does the changed behavior still belong to the module being modified?

Avoid moving responsibility or lifecycle ownership accidentally.

### 2. Dependency direction

Does the change introduce a new dependency, reverse an intended dependency, or create a cycle?

Prefer existing dependency directions and seams.

### 3. Public contract

Does the change unintentionally alter a public API/SPI, persistence contract, wire format, event schema, compatibility promise, or caller-visible behavior?

Treat intentional contract changes as explicit design work.

### 4. New abstraction

Before adding a module, interface, service, adapter, manager, or abstraction layer, check whether an existing abstraction can coherently own the behavior.

Do not introduce a layer merely because a pattern permits it.

## When architecture work is actually needed

A task is architecture work when it explicitly asks for architecture design/review/documentation/optimization or materially changes one of these:

- major subsystem or real module ownership boundary;
- dependency direction;
- domain ownership/lifecycle;
- runtime or data-flow architecture;
- load-bearing public seam;
- consequential compatibility contract.

The single explicit entry point for that work is `architecture`.

Do not start it automatically from this guard. When uncertain, prefer normal development plus this guard.

## Output discipline

Do not produce an Architecture Impact section for ordinary work.

If a conflict exists, state it briefly in the normal plan or implementation notes:

`Architecture guard: <specific conflict and smallest safe adjustment>`

If there is no conflict, do not emit architecture commentary.

## After implementation

Perform only a lightweight final check against the four rules above.

Do not automatically update architecture documentation. Use explicit `architecture` Document mode when architecture documentation work is actually requested.
