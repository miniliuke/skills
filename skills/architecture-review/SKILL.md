---
name: architecture-review
description: "Review a plan, diff, branch, or pull request specifically for architectural regressions and conformance. Use after implementation or before a major change is accepted. Complements normal code review with an independent architecture axis."
disable-model-invocation: true
---

# Architecture Review

Review architecture as its own axis. Do not blend structural findings into generic code-style review.

When available, run or consult `code-review` for standards/spec correctness. This skill answers a separate question:

> Does this change preserve or deliberately update the project's structural contract?

## Scope

Review only the change and the architecture it touches. Do not turn every review into a whole-codebase redesign.

Read:

- the plan/spec if one exists;
- `ARCHITECTURE.md` or the repository's authoritative architecture docs;
- relevant `CONTEXT.md`;
- relevant ADRs;
- the diff against a known-good point;
- affected public interfaces and callers;
- affected tests.

## Review axes

### 1. Ownership

Check whether behavior/state moved to a module that actually owns the concept.

Find:

- logic placed in a convenience layer rather than the owning module;
- upper layers taking ownership of connector/storage/runtime details;
- duplicated ownership of lifecycle/state.

### 2. Dependency direction

Find:

- new forbidden dependency edges;
- reverse dependencies;
- cycles;
- concrete implementation imports where an established seam should be used;
- generic/core modules importing feature-specific modules.

### 3. Seam integrity

Find:

- callers bypassing an established interface;
- widened interfaces that expose internal details;
- tests reaching through the public seam to verify internals;
- implementation-specific type switches outside the owning module.

### 4. Parallel abstractions

Find concepts implemented twice under different names.

For every new abstraction ask:

- what existing abstraction overlaps?
- why could it not be extended?
- if it replaces something, where is the retirement path?

### 5. Module depth and locality

Find:

- pass-through wrappers;
- modules whose interface is nearly as complex as what they hide;
- one behavior scattered across many shallow files/modules;
- unrelated behavior accumulating in a generic bucket.

Do not demand large modules. The goal is information hiding and locality, not file size.

### 6. Public contract

Find accidental changes to:

- behavior;
- invariants;
- ordering;
- error semantics;
- lifecycle;
- compatibility;
- performance characteristics that callers rely on.

Public interface means every fact callers must know, not only signatures.

### 7. Domain consistency

Use the project's domain language.

Find:

- new synonyms for existing canonical concepts;
- code that changes domain semantics without updating the model;
- state ownership contradicting `CONTEXT.md` or a relevant ADR.

### 8. Architecture memory impact

Determine what persistent architecture memory must change as a consequence of the verified implementation.

Do not require current-state architecture documentation to be updated *before* this review merely because the plan proposed a new architecture. Instead:

- verify the landed code actually establishes the intended new structural state;
- identify which architecture-document sections/diagrams are now stale;
- identify ADR updates only when a consequential decision changed;
- identify domain glossary updates only when domain meaning changed.

After a passing review, route current-state architecture documentation updates through `architecture-documentation` in Update mode.

If architecture docs were already updated in the same change, verify that they describe the landed reality rather than the planned target.

## Severity

Use exactly:

- `BLOCK` — violates an explicit architecture invariant/ADR, creates an unsafe dependency/ownership change, or introduces a parallel contract likely to cause long-term divergence.
- `WARN` — structural risk or design debt worth addressing, but the change can still be correct.
- `NOTE` — optional improvement; do not inflate these.

## Output

```markdown
# Architecture Review

## Verdict
PASS | PASS WITH WARNINGS | BLOCKED

## Findings

### [BLOCK|WARN|NOTE] Short finding title
Evidence:
Architecture rule / principle:
Why it matters:
Smallest credible fix:

## Positive confirmations
Only list important architecture properties the change preserved.

## Architecture memory
Required `architecture-documentation` update, CONTEXT.md change, or ADR update, if any.
```

If there are no findings, say so. Do not manufacture architecture criticism.

## Guardrail

A review finding must cite concrete evidence from the diff/current code or a documented architecture rule. "I prefer another pattern" is not a finding.
