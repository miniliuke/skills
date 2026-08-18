# Architecture Workflow Guide

## 1. New project

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

## 2. Ordinary feature

```text
Requirement
  -> native Plan Mode
  -> execute
  -> tests
  -> review
```

Escalate to `architecture-change` only when the feature changes ownership, module topology, public seams, dependency direction, or domain concepts.

## 3. New module

```text
Requirement
  -> inspect current architecture / ADRs
  -> justify the module
  -> domain-modeling if vocabulary changes
  -> codebase-design
  -> native Plan Mode
  -> update ARCHITECTURE.md if topology changes
  -> execute
  -> architecture-review
```

## 4. Architecture change

```text
Current architecture
  -> architecture impact analysis
  -> domain-modeling if semantics change
  -> codebase-design for new seams
  -> migration / compatibility plan
  -> native Plan Mode
  -> execute
  -> architecture-review
  -> update ADR / ARCHITECTURE.md
```

## 5. Periodic health check

```text
Recent changes / hotspots
  -> architecture-health
  -> choose 1-3 high-value candidates
  -> architecture-change
  -> execute in small steps
  -> architecture-review
```

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

Otherwise, stay with native Plan Mode.
