---
name: architecture-documentation
description: "Create, update, or reconcile architecture documentation for an existing codebase. Use when documenting current architecture, maintaining ARCHITECTURE.md after verified structural changes, or checking whether architecture docs still match executable reality."
---

# Architecture Documentation

Maintain architecture documentation as an accurate description of the **architecture that exists now**.

This skill documents and reconciles architecture. It is not an architecture-improvement session and must not silently redesign the codebase while documenting it.

Core rule:

> `ARCHITECTURE.md` describes verified current architecture. Planned or target architecture belongs in a plan/spec/ADR until implementation is complete and reviewed.

## Select the mode automatically

Choose one primary mode from the user's request and repository state.

### Bootstrap

Use when an existing project has no authoritative architecture document, or the existing material is too fragmented to serve as one.

Goal: reverse-engineer the current architecture and establish an architecture document without pretending the code is cleaner than it is.

### Update

Use when architecture documentation already exists and a verified structural change has landed.

Goal: surgically update only the sections made stale by the change.

### Reconcile

Use when documentation may have drifted from the code, or the user explicitly asks whether the architecture document is still accurate.

Goal: compare documented architecture with executable reality, classify mismatches, and correct the documentation where the code represents the accepted current state.

## 1. Discover the authoritative architecture documentation

Before creating a new file, inspect the repository for existing architecture sources, including:

- `ARCHITECTURE.md`;
- architecture or design docs under `docs/`;
- root/module READMEs that the repository treats as authoritative;
- `CONTEXT.md` / `CONTEXT-MAP.md`;
- relevant `docs/adr/`;
- build/workspace manifests and module definitions.

If the project already has an authoritative architecture document, update it rather than introducing a competing document merely to satisfy this skill.

Use a root `ARCHITECTURE.md` as the default only when no stronger project convention exists.

## 2. Establish current executable reality

Use code and configuration to understand what actually exists:

- module/package/crate/project structure;
- build-time dependency edges;
- representative imports and callers;
- public interfaces and extension points;
- composition/bootstrap/wiring code;
- persistence and external integration seams;
- runtime process/service relationships;
- important data/control flows;
- tests that demonstrate intended public behavior.

Do not infer the architecture only from directory names.

When documentation and code disagree, preserve both facts long enough to classify the mismatch instead of silently picking one.

## 3. Use supporting skills only for their proper purpose

### `domain-modeling`

Use it only when documentation work exposes an unresolved or contradictory domain term, ownership rule, or lifecycle concept.

Do not invoke it merely to copy existing glossary terms into architecture documentation.

### `codebase-design`

Use its vocabulary — module, interface, implementation, seam, adapter, depth, leverage, locality — when describing software shape.

Do not use documentation work as an excuse to redesign shallow modules. Record structural debt separately and leave improvement to `architecture-health` / `improve-codebase-architecture` / `architecture-change`.

## 4. Separate observed architecture from intended constraints

Architecture documentation must distinguish at least these concepts:

### Observed architecture

What the code/configuration currently does.

Examples:

- current modules and responsibilities;
- actual dependency edges;
- current runtime/data flow;
- actual public seams and extension points.

### Architectural invariants

Rules the project intends future changes to preserve, supported by explicit docs, ADRs, established conventions, or strong current structure.

Examples:

```text
Allowed: application -> dataset-api
Forbidden: dataset-api -> connector-mysql
Rule: application must not branch on connector implementation type
```

Do not invent invariants simply because they would make the architecture nicer.

### Known deviations

Executable reality that violates an accepted invariant or ADR.

Record it honestly instead of rewriting the observed architecture to look compliant.

### Architectural debt

Structural friction worth improving that does not necessarily violate an invariant.

Keep this concise. Architecture documentation is not a refactoring backlog.

## 5. Bootstrap format

Prefer a compact document shaped roughly like this, adapting to the codebase rather than forcing empty sections:

```markdown
# Architecture

## System Purpose
## System Context
## Module Map
## Module Responsibilities
## Dependency Model
## Public Interfaces and Seams
## Runtime Flow
## Data Flow
## Extension Points
## External Systems
## Architectural Invariants
## Known Deviations
## Architectural Debt
## Relevant Decisions
```

Use diagrams only when they communicate relationships more clearly than prose. Keep diagrams source-controlled as text when practical (for example Mermaid).

## 6. Update mode: make surgical changes

Prefer targeted edits over full-document regeneration.

Before editing:

1. identify which architecture facts changed;
2. map them to affected document sections/diagrams;
3. preserve valid human-written context and rationale;
4. update only stale material;
5. remove statements that are no longer true.

Do not rewrite unaffected wording for style consistency.

Do not replace a hand-maintained diagram unless the topology it describes actually changed or the diagram is demonstrably stale.

## 7. Reconcile mode: classify drift

Compare documentation with current code and classify each mismatch as one of:

```text
DOC_STALE
  Code reflects the accepted current architecture; documentation needs updating.

CODE_DEVIATION
  Code violates an intended invariant/ADR; document under Known Deviations and do not normalize it as the intended design.

AMBIGUOUS
  Evidence is insufficient or sources disagree about intent; surface it for resolution.

PLANNED_NOT_LANDED
  A plan/spec describes a future architecture that is not fully implemented; do not promote it to current architecture.
```

Do not fix code unless the user separately asks for an architecture change.

## 8. Relationship to architecture changes

Before implementation:

```text
architecture-change
  -> describes current pressure and target architecture
```

After implementation and architecture review pass:

```text
architecture-documentation
  -> records the verified new current architecture
```

Never update the current-state architecture document merely because a plan was approved.

If a migration is only partially complete, document the actual mixed state and any accepted temporary compatibility seam. Do not describe the final target as already complete.

## 9. ADR and CONTEXT responsibilities

Do not duplicate their jobs inside `ARCHITECTURE.md`:

- `CONTEXT.md`: canonical domain vocabulary, no implementation diary.
- ADR: hard-to-reverse, non-obvious trade-off and rationale.
- architecture document: current structural truth and active structural constraints.

Link relevant ADRs instead of copying their full rationale.

## Output

After the documentation work, report concisely:

```markdown
## Architecture Documentation

Mode: Bootstrap | Update | Reconcile
Authoritative document: <path>
Sections changed: <list>

Observed conflicts:
- DOC_STALE: ...
- CODE_DEVIATION: ...
- AMBIGUOUS: ...
- PLANNED_NOT_LANDED: ...

Unresolved evidence gaps:
- ...
```

Omit empty categories.

## Guardrails

- Document what exists, not what would be ideal.
- Do not silently redesign architecture while documenting it.
- Do not silently change an invariant to make current code compliant.
- Do not describe planned architecture as current architecture.
- Prefer evidence from executable configuration/code for observed structure.
- Prefer explicit ADRs/architecture rules for intended constraints.
- Preserve useful human-written documentation and make surgical updates.
- If a mismatch needs code changes, route it to `architecture-change`; if it needs structural exploration, route it to `architecture-health`.
