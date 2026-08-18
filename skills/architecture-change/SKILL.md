---
name: architecture-change
description: "Plan a feature or refactor that changes existing architecture: module ownership, public interfaces, dependency direction, runtime/data flow, persistence/integration seams, or domain lifecycle. Use before implementing cross-module structural changes."
disable-model-invocation: true
---

# Architecture Change

Change an existing architecture deliberately. Preserve what is useful, challenge what creates concrete friction, and make migration part of the design.

## 1. Establish the current truth

Read:

- `ARCHITECTURE.md`;
- relevant domain glossary;
- relevant ADRs;
- current public interfaces;
- dependency graph/imports;
- representative callers;
- representative tests;
- recent changes in the affected area when useful.

Distinguish:

```text
Documented architecture
Actual architecture
Proposed architecture
```

Surface mismatches instead of silently treating one as authoritative.

## 2. State the pressure causing the change

Architecture changes need concrete pressure, for example:

- one feature touches too many modules;
- callers must know implementation details;
- the same concept has parallel abstractions;
- dependency direction blocks extension;
- repeated type switches leak implementation-specific behavior;
- two modules co-change repeatedly;
- tests are coupled to internal structure;
- a module is shallow and adds navigation without hiding complexity.

Do not redesign because another pattern looks cleaner in isolation.

## 3. Domain impact first

Use `domain-modeling` before module redesign when:

- ownership of state/lifecycle changes;
- a core concept is split or merged;
- terminology is overloaded;
- the new architecture only works if a domain concept is redefined.

Do not let software structure silently redefine domain meaning.

## 4. Design the new software shape

Use `codebase-design` if available.

Check:

- module depth;
- locality;
- interface complexity;
- information hiding;
- seam placement;
- test surface;
- real versus hypothetical variation.

Before introducing a new abstraction:

1. search for existing abstractions with overlapping responsibility;
2. explain why they cannot be extended;
3. define the retirement path for any replaced abstraction.

## 5. Produce Architecture Impact before implementation

```markdown
## Architecture Impact

### Current pressure
What concrete problem makes structural change worthwhile?

### Affected modules
Which modules change responsibility or dependency?

### Domain changes
Terms, lifecycle, state ownership, invariants.

### Seam changes
Existing seam reused, widened, replaced, or newly introduced.

### Dependency changes
New edges, removed edges, newly forbidden edges.

### Public contract changes
Compatibility and caller impact.

### Runtime / data-flow changes
Only if execution shape changes.

### Migration
Order of changes, compatibility bridge, cleanup point.

### Architecture memory
ARCHITECTURE.md updates and ADRs.

### Risks
Failure modes and rollback/verification strategy.
```

If the impact cannot be stated clearly, do not start coding yet.

## 6. Migration over flag day rewrites

Prefer an incremental path:

```text
establish/extend seam
  -> migrate one vertical path
  -> validate
  -> migrate remaining callers
  -> remove old path
```

Avoid maintaining two permanent implementations of the same architectural concept.

Compatibility adapters are temporary unless they hide a genuinely independent integration.

## 7. Specs and tickets are conditional

Use native Plan Mode by default.

Create a durable spec when:

- the change spans multiple contexts/sessions;
- multiple agents will work on it;
- it changes a core public SPI;
- the migration has multiple independent phases;
- future maintainers need the decision chain preserved.

Create tickets when they provide real parallel or resumable execution boundaries.

## 8. Completion criteria

The architecture change is complete only when:

- obsolete paths are removed or have an explicit retirement issue;
- `ARCHITECTURE.md` describes the new current state;
- consequential decisions are recorded in ADRs;
- tests target stable behavior through the intended seam;
- no upper layer bypasses the new seam;
- the dependency graph matches the intended direction.
