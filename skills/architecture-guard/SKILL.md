---
name: architecture-guard
description: "Lightweight architecture guardrail for ordinary development. Use implicitly during coding to prevent accidental boundary, dependency, ownership, and public-contract violations without running an architecture workflow."
---

# Architecture Guard

Keep architecture coherent without turning normal development into an architecture exercise.

This is a guardrail, not a workflow. Do not create extra planning stages, design sessions, reports, specs, or architecture documents just because this skill is present.

## Default behavior

For ordinary bugs, features, tests, refactors, configuration changes, and UI work:

1. Use the agent's normal planning/execution flow.
2. Check only the architecture rules relevant to the code being changed.
3. Continue immediately when no conflict is found.

Do not invoke `architecture-change`, `new-module-architecture`, `new-project-architecture`, `domain-modeling`, `codebase-design`, or other architecture skills automatically.

## Read narrowly

Only read architecture documentation when the change may touch a structural boundary.

Prefer, in order:

- a short `ARCHITECTURE.md` or architecture index;
- the README/design doc for the affected module;
- relevant ADRs;
- broader architecture documents only when necessary.

Do not scan the whole repository merely to prove architectural compliance.

## Check these four things

### 1. Ownership

Does the changed behavior still belong to the module being modified?

Avoid moving responsibilities across modules accidentally.

### 2. Dependency direction

Does the change introduce a new dependency or reverse an existing intended dependency?

Prefer existing dependency directions and seams.

### 3. Public contract

Does the change unintentionally alter a public API, SPI, persistence contract, wire format, event schema, or compatibility promise?

Treat intentional contract changes as explicit design work.

### 4. New abstraction

Before adding a module, interface, service, adapter, manager, or abstraction layer, check whether an existing abstraction can own the behavior.

Do not introduce a layer merely because a pattern permits it.

## Escalation

Escalate to a dedicated architecture skill only when the user asks for architecture work or the task clearly requires one of these:

- a new project or major subsystem;
- a new module with a real ownership boundary;
- changed dependency direction;
- changed domain ownership/lifecycle;
- changed runtime or data-flow architecture;
- a consequential public compatibility contract change;
- an explicit architecture refactor or architecture review.

When uncertain, prefer normal development plus this guard over escalation.

## Output discipline

Do not produce an Architecture Impact section for ordinary work.

If a conflict exists, state it briefly in the normal plan or implementation notes:

`Architecture guard: <specific conflict and smallest safe adjustment>`

If there is no conflict, do not emit architecture commentary.

## After implementation

Perform only a lightweight final check against the four rules above.

Do not automatically update architecture documentation. Update it only when verified structural reality changed and the user/task actually requires documentation maintenance.
