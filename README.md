# Agent Specialist Skills Bundle

A collection of **specialist engineering skills** for coding agents.

The responsibility split is intentionally small:

```text
Ponytail
  -> always-on YAGNI, reuse-first, minimum implementation, anti-overengineering

Minimal engineering guardrails
  -> always-on architecture safety + lightweight TDD discipline

skills/
  -> specialist methods only
```

Ordinary features, bug fixes, UI changes, and configuration edits should not invoke a skill merely to follow a process.

## 1. Install Ponytail first

This repository no longer duplicates Ponytail's complexity-control rules as skills. Use the upstream plugin directly:

[Ponytail](https://github.com/DietrichGebert/ponytail)

### Codex

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex
```

Then open `/plugins`, install Ponytail from its marketplace, open `/hooks`, review and trust its two lifecycle hooks, and start a new thread. Node.js must be on the non-interactive shell PATH for the always-on hooks.

### Claude Code

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

## 2. Install specialist skills

List available skills:

```bash
npx skills add miniliuke/skills --list
```

Install the complete specialist bundle:

```bash
npx skills add miniliuke/skills --skill '*'
```

Because `skills/` now contains specialist capabilities only, installing the bundle no longer adds default architecture/TDD workflow skills to ordinary development.

Antigravity:

```bash
npx skills add miniliuke/skills --skill '*' --agent antigravity
```

Claude Code:

```bash
npx skills add miniliuke/skills --skill '*' --agent claude-code
```

## 3. Minimal always-on engineering rules

`guardrails/engineering.md` is a short **non-skill** snippet intended for global or project `AGENTS.md` / agent instructions.

It supplements Ponytail with only two concerns Ponytail does not own:

- architecture safety: ownership, dependency direction, and public contracts/seams;
- lightweight TDD: when existing test infrastructure makes it practical, prefer a small failing test, the minimum implementation, then focused regression tests.

It does not repeat Ponytail's YAGNI/reuse/minimal-code rules and does not start a workflow.

## 4. Specialist skills

### `architecture`

The **explicit architecture entry point** for new system/module design, structural changes, architecture review, `ARCHITECTURE.md` maintenance, and explicit architecture-health work.

It selects only one relevant mode: Design, Change, Review, Document, or Health.

### `codebase-design`

Use when load-bearing module/interface/seam or deep-module design is itself the problem. It is not a default feature-development phase.

### `domain-modeling`

Use when canonical concepts, terminology, state, or lifecycle ownership are genuinely unresolved. Ordinary DTO/field/API parameter changes do not require domain modeling.

### `diagnosing-bugs`

Use for difficult diagnosis, hard-to-reproduce failures, complex incidents, or performance regressions. Obvious local bugs should normally be reproduced, fixed, and tested directly.

### `grilling`

Use when the user explicitly wants a plan, design, or decision stress-tested through a rigorous interview.

### `writing-for-agents`

Use for agent-facing instructions, context, and documentation.

## 5. Removed entries

- `architecture-guard` — moved into the non-skill engineering guardrail.
- `tdd-guard` — reduced to a few baseline engineering rules instead of a triggerable workflow.
- `grill-me` — removed because it was only a thin wrapper around `grilling`.
- `grill-with-docs` — removed because it only cascaded `grilling + domain-modeling`.
- upstream `tdd` and `improve-codebase-architecture` remain intentionally unmirrored.

## 6. Default routing

```text
ordinary development
  -> Ponytail
  -> native Plan / Execute
  -> minimal engineering guardrails
  -> focused tests
  -> done

actual specialist task
  -> Ponytail
  -> one best-matching skill
  -> native Plan / Execute
  -> done
```

Rules:

```text
Do not invoke a skill because it is installed.
Do not turn several skills into a fixed pipeline.
Prefer at most one primary skill per task.
Use a supporting skill only when it solves a separate real problem.
```

Ponytail decides **how little should be built**. A specialist skill only decides **how to handle that specialist problem**.

## 7. Persistent architecture memory

Keep these concerns separate:

```text
CONTEXT.md
  domain language and canonical concepts

docs/adr/
  consequential decisions and rationale

ARCHITECTURE.md
  verified current structural truth and constraints
```

`ARCHITECTURE.md` describes architecture that has actually landed, not a planned target state.

## 8. Upstream synchronization

`.github/workflows/sync-mattpocock-skills.yml` synchronizes only Matt Pocock skills that retain independent specialist value:

```text
codebase-design
domain-modeling
diagnosing-bugs
grilling
writing-for-agents
```

The custom `architecture` skill is protected through `.github/custom-skills.txt`.

## Mental model

```text
Complexity: Ponytail.
Baseline engineering discipline: guardrails, not skills.
Specialist problem: invoke a skill.
```
