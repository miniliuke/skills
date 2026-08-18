# Architecture Workflow Guide

## 1. Existing project: establish architecture documentation

```text
Existing codebase
  -> architecture-documentation (Bootstrap)
  -> inspect executable module/dependency/runtime structure
  -> read CONTEXT / ADR / existing design docs
  -> establish the authoritative architecture document
```

Document what exists now. Do not redesign the codebase during documentation work.

If an architecture document already exists but may be stale:

```text
Architecture docs + code
  -> architecture-documentation (Reconcile)
  -> classify DOC_STALE / CODE_DEVIATION / AMBIGUOUS / PLANNED_NOT_LANDED
```

## 2. New project

```text
Initial requirements
  -> clarify goals / constraints
  -> domain-modeling
  -> codebase-design
  -> native Plan Mode
  -> establish ARCHITECTURE.md
  -> execute
  -> architecture-review
```

Use `to-spec` only when the architecture needs durable handoff or multi-session execution.

## 3. Ordinary feature

```text
Requirement
  -> native Plan Mode
  -> execute
  -> tests
  -> review
```

Escalate to `architecture-change` only when the feature changes ownership, module topology, public seams, dependency direction, or domain concepts.

## 4. New module

```text
Requirement
  -> inspect current architecture / ADRs
  -> justify the module
  -> domain-modeling if vocabulary changes
  -> codebase-design
  -> native Plan Mode
  -> execute
  -> architecture-review
  -> architecture-documentation (Update) if structural truth changed
```

Do not update current-state documentation merely because the module design was approved. Update it after the landed architecture is verified.

## 5. Architecture change

```text
Current architecture
  -> architecture-change
      -> architecture impact analysis
      -> domain-modeling if semantics change
      -> codebase-design for new seams
      -> migration / compatibility plan
      -> native Plan Mode
  -> execute
  -> architecture-review
  -> architecture-documentation (Update)
```

This separates target design from current-state documentation:

```text
Plan/spec/ADR
  -> what we intend to change

Architecture documentation
  -> what has actually landed and been verified
```

If a migration is partially complete, document the real mixed state rather than the final target.

## 6. Periodic health check

```text
Recent changes / hotspots
  -> architecture-health
  -> choose 1-3 high-value candidates
  -> architecture-change
  -> execute in small steps
  -> architecture-review
  -> architecture-documentation if structure changed
```

## Architecture documentation responsibilities

Use `architecture-documentation` for three modes:

```text
Bootstrap
  Build architecture documentation for an existing project.

Update
  Surgically update documentation after verified structural changes.

Reconcile
  Compare documentation with executable reality and classify drift.
```

Architecture docs should distinguish:

- observed architecture;
- architectural invariants;
- known deviations;
- architectural debt.

Prefer surgical edits over regenerating an entire human-maintained document.

## Escalation triggers

Run architecture-specific design when any of these appears:

- new core domain term;
- ambiguous ownership of state/lifecycle;
- new module/package/crate/service/plugin;
- new public API or SPI;
- cross-module feature;
- dependency direction changes;
- duplicated concept or parallel abstraction;
- type-switching in upper layers for implementation-specific behavior;
- two or more modules repeatedly changing together;
- tests must reach through multiple internals to verify behavior;
- the proposed implementation bypasses an existing seam.

Run `architecture-documentation` when:

- an existing project lacks an authoritative architecture document;
- architecture documentation may be stale;
- a verified structural change has landed and current-state documentation needs updating.

Otherwise, stay with native Plan Mode.
