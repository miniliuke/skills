# Agent Engineering Skills Bundle

A lightweight set of skills for modern coding agents. The goal is not to add process to every change: ordinary development should use the agent's native planning flow with small guardrails, while deep design remains explicitly opt-in.

## Install

List available skills:

```bash
npx skills add miniliuke/skills --list
```

Install the complete bundle:

```bash
npx skills add miniliuke/skills --skill '*'
```

Antigravity:

```bash
npx skills add miniliuke/skills --skill '*' --agent antigravity
```

Claude Code:

```bash
npx skills add miniliuke/skills --skill '*' --agent claude-code
```

## Default development flow

Ordinary features and bug fixes should not start separate architecture or TDD workflows:

```text
Requirement
  -> Native Plan Mode
  -> Execute
       + architecture-guard
       + tdd-guard
  -> Tests
  -> Review
```

The guards are implementation disciplines, not additional planning stages.

## Architecture: two entry points only

### `architecture-guard`

Implicit lightweight guardrail for ordinary development.

It checks only whether a change accidentally breaks:

- module ownership;
- dependency direction;
- public contracts / seams;
- abstraction boundaries.

If no conflict exists, it should stay silent and should not invoke deeper architecture skills.

### `architecture`

The single explicit architecture skill a human needs to remember.

Use it when the task itself is architecture work, such as:

```text
design a new project architecture
design a new module/plugin
change existing module boundaries
review architecture in a plan/diff/PR
create or update ARCHITECTURE.md
assess structural health and improvement opportunities
```

It infers one mode automatically:

```text
Design    new project / module / subsystem
Change    ownership / dependency / seam / runtime-flow changes
Review    architecture conformance of a plan/diff/branch/PR
Document  Bootstrap / Update / Reconcile architecture documentation
Health    structural health assessment and prioritized improvements
```

There is no longer a user-facing choice between `architecture-change`, `new-module-architecture`, `architecture-review`, and similar workflow skills.

`architecture` also avoids automatic skill cascades. Use `domain-modeling` only when domain meaning/lifecycle ownership is actually unresolved, and `codebase-design` only when a load-bearing module/interface needs deeper focused design.

## TDD

### `tdd-guard`

Implicit lightweight TDD discipline:

```text
testable behavior
  -> smallest useful failing test
  -> confirm expected failure
  -> smallest reasonable implementation
  -> pass the focused test
  -> run relevant nearby regression tests
```

It does not create a separate TDD plan, seam-design session, or testing-strategy document. It also does not invoke `codebase-design` merely to place an ordinary test.

Test-first is not forced when there is no practical test setup, the change is documentation/trivial configuration, or creating a harness would cost substantially more than the requested change.

## Vendored Matt Pocock skills

CI synchronizes only upstream skills that still provide independent value:

```text
codebase-design
domain-modeling
diagnosing-bugs
grill-with-docs
grill-me
grilling
writing-for-agents
```

The upstream `tdd` and `improve-codebase-architecture` skills are intentionally not mirrored because their relevant responsibilities are covered by the lightweight guard and unified architecture skill.

Use `codebase-design` directly when module/interface/seam design is itself the task. Use `domain-modeling` directly when canonical concepts, terminology, state, or lifecycle ownership are unresolved. Neither is a mandatory step for ordinary feature development.

## Persistent architecture memory

Keep three concerns separate:

```text
CONTEXT.md
  Domain language: what do the concepts mean?

docs/adr/
  Consequential decisions: why was this choice made?

ARCHITECTURE.md
  Verified current structural truth and active constraints.
```

Important rule:

```text
ARCHITECTURE.md describes architecture that has actually landed.
A planned target architecture is not current-state documentation.
```

The `architecture` skill's Document mode handles Bootstrap, Update, and Reconcile work.

## Automatic upstream synchronization

`.github/workflows/sync-mattpocock-skills.yml`:

- runs daily and supports manual dispatch;
- synchronizes only explicitly selected Matt Pocock skills;
- never executes upstream scripts;
- protects custom skill names listed in `.github/custom-skills.txt` from silent upstream replacement;
- validates vendored `SKILL.md` names;
- records the upstream commit SHA and preserves the MIT license;
- creates no empty commit when synchronized content has not changed.

## Mental model

A human only needs to remember:

```text
ordinary development: do not choose an architecture skill
actual architecture work: use architecture
```

The skill itself handles the remaining mode selection instead of exposing a workflow taxonomy to the user.
