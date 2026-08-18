---
name: new-module-architecture
description: "Design and justify a new module, plugin, crate, package, subsystem, or public extension point inside an existing codebase. Use before adding a structural unit that changes ownership, dependencies, interfaces, or extension seams."
disable-model-invocation: true
---

# New Module Architecture

A new module is a long-lived structural decision. Make it earn its existence before adding files.

## 1. Read the current architecture first

Before proposing the module, inspect:

- `ARCHITECTURE.md`;
- relevant `CONTEXT.md` / `CONTEXT-MAP.md`;
- ADRs in the affected area;
- existing neighboring modules and their public interfaces;
- current dependency graph/import patterns;
- tests that already exercise the relevant behavior.

Do not design a clean-room architecture that ignores what the project already treats as stable.

## 2. Decide whether a new module is actually needed

A module is justified when it creates useful information hiding and ownership.

Answer:

```text
Problem this module owns:
Behavior it hides:
State/lifecycle it owns:
Callers:
Public interface:
Existing abstraction that overlaps:
Why that abstraction cannot be extended:
What changes independently behind this seam:
```

Apply the deletion test:

- If deleting the proposed module would mostly delete pass-through wrappers, do not add it.
- If deleting it would force multiple callers to understand duplicated complexity, the module is earning its keep.

## 3. Check domain impact

Use `domain-modeling` when the module introduces or changes a canonical domain concept.

Do not name a module after an implementation detail if the domain already has a stable concept that owns the behavior.

If no domain concept is involved, do not force domain modeling.

## 4. Design the seam

Use `codebase-design` when available.

Prefer:

- a small interface;
- high behavioral leverage;
- invariants hidden behind the module;
- caller-facing types that do not leak internal implementation;
- tests through the same interface callers use.

For a load-bearing interface, compare at least two materially different designs before choosing one.

Do not create an extension interface solely because there is one implementation today unless variation is an explicit near-term requirement.

## 5. Dependency placement

Record:

```text
May depend on:
May be depended on by:
Must not depend on:
Must not be imported by:
```

If the module makes the dependency graph cyclic, redesign the ownership/seam instead of tolerating the cycle.

If upper layers need `if type == X` to use the module, check whether the behavior belongs behind an existing interface.

## 6. Integration and migration

Plan:

- how existing callers move to the module;
- compatibility if a public contract changes;
- whether old abstractions are removed, deprecated, or temporarily bridged;
- how to avoid two permanent ways to perform the same operation.

Parallel abstractions require an explicit retirement path.

## 7. Native Plan Mode output

Require:

```markdown
## Module Architecture

Purpose:
Ownership:
Public seam:
Hidden complexity:
Dependencies:
Forbidden dependencies:
Existing abstractions reused:
New abstractions justified:
Domain changes:
Compatibility/migration:
Testing seam:
ARCHITECTURE.md update:
ADR needed:
```

## 8. Documentation

Update `ARCHITECTURE.md` only if the new module changes the structural contract that future work must understand.

Create an ADR only for consequential trade-offs, not because a module was added.

## Review bar

The module is ready to implement when a future agent can answer:

- where new behavior of this kind belongs;
- what interface it should call;
- what it must not depend on;
- what internal details callers must never learn.
