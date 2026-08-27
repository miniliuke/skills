---
name: architecture
description: "Unified explicit architecture skill. Use when the user explicitly wants to design, change, review, document, or improve software architecture, including new projects, new modules, structural refactors, architecture reviews, and ARCHITECTURE.md maintenance."
disable-model-invocation: true
---

# Architecture

This is the single explicit entry point for architecture work.

For ordinary development, do not use this skill; `architecture-guard` is enough.

Do not make the user choose between separate architecture workflows. Infer the mode from the request and do only the work needed for that mode.

## Modes

Choose one primary mode automatically:

- **Design** — new project, major subsystem, module, plugin, or extension seam.
- **Change** — an existing architecture must change: ownership, dependencies, public seam, runtime/data flow, persistence/integration boundary, or lifecycle ownership.
- **Review** — review a plan, diff, branch, or PR for architecture conformance/regressions.
- **Document** — bootstrap, update, or reconcile architecture documentation.
- **Health** — inspect an evolving codebase for structural friction and prioritize architecture improvements.

Do not run every mode in sequence.

## Common rules

### Read narrowly

Inspect only architecture evidence relevant to the requested scope:

- `ARCHITECTURE.md` or the repository's authoritative architecture document;
- relevant module README/design docs;
- relevant ADRs;
- `CONTEXT.md` / `CONTEXT-MAP.md` when domain vocabulary matters;
- affected public interfaces, representative callers, tests, and dependency/build configuration.

Do not scan the entire repository by default.

Distinguish when necessary:

```text
Documented architecture
Actual architecture
Proposed architecture
```

Surface meaningful conflicts instead of silently choosing whichever source supports the proposed design.

### Core architecture questions

Across all modes, focus on these:

1. **Ownership** — which module owns the behavior, state, and lifecycle?
2. **Dependency direction** — what may depend on what, and what must not?
3. **Seams/contracts** — what must callers know and what complexity is hidden?
4. **Runtime/data ownership** — where are source of truth, consistency, async, and failure boundaries?
5. **Migration/compatibility** — how does existing code move without leaving permanent parallel abstractions?

Prefer deep modules and small stable interfaces over layers of pass-through wrappers.

Before adding an abstraction, identify any existing overlapping abstraction and prefer extending it when that preserves coherent ownership.

Do not force DDD, Clean Architecture, hexagonal architecture, microservices, plugin systems, or generic layers without concrete pressure.

### Supporting skills

Do not automatically cascade into other skills.

Use `domain-modeling` only when the problem vocabulary, lifecycle ownership, or domain meaning itself is unresolved.

Use `codebase-design` only when a load-bearing module/interface design needs deeper exploration than this skill can reasonably do inline.

For most architecture tasks, apply those principles directly and keep the workflow inside this skill.

## Design mode

Use for a new project, major subsystem, module, plugin, crate/package, or public extension point.

Establish only enough architecture to make implementation coherent:

1. Clarify goals, constraints, external systems, important quality attributes, and non-goals.
2. Define the few core concepts and ownership boundaries.
3. Propose modules only where they hide meaningful complexity or own a coherent lifecycle.
4. Define allowed/forbidden dependency directions.
5. Define public seams and extension points only where variation is real.
6. Describe only load-bearing runtime/data flows.
7. For an existing codebase, explain why the new module cannot be an extension of an existing one.
8. Hand the result to the agent's normal implementation plan; do not create a second planning workflow.

For a new project, create a compact architecture contract only when useful:

```markdown
# Architecture

## System shape
## Modules and ownership
## Dependency rules
## Public seams
## Runtime / data flow
## Architectural invariants
## Known constraints
```

Create ADRs only for consequential, non-obvious, expensive-to-reverse decisions.

## Change mode

Use when existing structural contracts must change.

First state the concrete pressure. Good reasons include repeated cross-module changes, leaked implementation details, dependency erosion, duplicated ownership, parallel abstractions, or a seam that blocks required behavior.

Then determine:

```text
Affected ownership:
Seams/contracts changed:
Dependency edges changed:
Runtime/data-flow impact:
Domain/lifecycle impact:
Compatibility impact:
Migration path:
Architecture docs/ADR impact after landing:
```

Prefer incremental migration:

```text
establish or extend seam
-> migrate one vertical path
-> validate
-> migrate remaining callers
-> remove old path
```

Do not update current-state architecture documentation merely because the target design was approved. Document the new current state after it actually lands and is verified.

## Review mode

Review only the change and the architecture it touches.

Check:

- ownership moved to the wrong layer/module;
- forbidden/reversed/cyclic dependencies;
- callers bypassing an established seam;
- widened public interfaces leaking internals;
- parallel abstractions for the same responsibility;
- shallow pass-through layers;
- accidental compatibility/behavior contract changes;
- domain semantics or lifecycle ownership drifting;
- documentation claiming a target architecture that has not landed.

Use findings only when supported by concrete code/diff or an explicit architecture rule.

Severity:

- `BLOCK` — violates an explicit invariant/ADR or creates a dangerous structural/compatibility break.
- `WARN` — meaningful structural risk/debt, but not necessarily incorrect.
- `NOTE` — optional improvement; use sparingly.

Return `PASS`, `PASS WITH WARNINGS`, or `BLOCKED` plus only meaningful findings and the smallest credible fixes.

Do not manufacture architecture criticism when the change is fine.

## Document mode

Architecture documentation describes **verified current architecture**, not aspiration.

Infer one submode:

- **Bootstrap** — no useful authoritative architecture document exists.
- **Update** — a verified structural change landed; update only stale sections.
- **Reconcile** — docs and executable reality may have drifted.

For reconciliation classify mismatches as:

```text
DOC_STALE          code is accepted current truth; docs need updating
CODE_DEVIATION     code violates an intended invariant/ADR
AMBIGUOUS          evidence is insufficient or intent conflicts
PLANNED_NOT_LANDED target design is not yet current reality
```

Preserve useful human-written rationale and make surgical edits. Do not rewrite unaffected documentation for style.

Keep `ARCHITECTURE.md`, ADRs, and `CONTEXT.md` distinct:

- architecture docs: current structural truth and active structural constraints;
- ADRs: consequential decisions and rationale;
- CONTEXT: canonical domain vocabulary.

## Health mode

Use for explicit architecture optimization/maintainability work, not routine feature development.

Prefer hot areas with evidence of friction:

- files/modules repeatedly changed together;
- recurring bugs around one seam;
- widespread navigation needed to understand one behavior;
- shallow wrappers;
- scattered invariants;
- parallel abstractions;
- dependency cycles/erosion;
- implementation-specific type switches leaking upward;
- unstable tests coupled to internals;
- inconsistent domain ownership.

Return at most three primary candidates unless exhaustive coverage is requested.

For each candidate state:

```text
Pressure/evidence:
Current structural problem:
Proposed direction:
Expected leverage:
Migration size/risk:
Recommendation strength:
```

Prioritize improvements that reduce the amount of context a future human or agent must load to make a correct change.

Do not recommend large rewrites for stylistic consistency or speculative future extensibility.

## Completion discipline

Architecture work should end with the smallest durable result appropriate to the mode:

- Design/Change: structural decisions that normal Plan Mode can implement.
- Review: concrete evidence-backed findings or a pass.
- Document: accurate, minimally changed current-state documentation.
- Health: a short prioritized candidate list, not an automatic refactor campaign.

Do not automatically chain Design -> Change -> Review -> Document -> Health.
