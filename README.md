# Architecture Skills

A small set of agent skills for **designing and maintaining software architecture with modern coding agents**.

The core idea is deliberately lightweight:

> Use the agent's native Plan Mode for ordinary planning. Use skills only when specialized architectural reasoning or long-lived architectural memory is needed.

These skills are designed to work well with the open `npx skills` ecosystem and with Matt Pocock's engineering skills.

## Skills

| Skill | When to use | Main outcome |
|---|---|---|
| `architecture-workflow` | Unsure which architecture workflow a task needs | Routes to the lightest appropriate workflow |
| `new-project-architecture` | Starting a new codebase or major subsystem from scratch | Initial domain model, module map, dependency rules, architecture contract |
| `new-module-architecture` | Adding a new module / plugin / subsystem to an existing codebase | Justified module seam, interface, dependencies, integration plan |
| `architecture-change` | A feature changes existing module boundaries, ownership, public interfaces, or dependency direction | Architecture impact analysis and migration-safe plan |
| `architecture-review` | Reviewing a completed plan/diff/PR for architectural regressions | Architecture findings independent from code-style/spec findings |
| `architecture-health` | Periodic architecture maintenance or "this codebase is getting hard to change" | Prioritized structural improvement candidates |

## Philosophy

This repository intentionally does **not** recreate a long planning pipeline.

For most work:

```text
Requirement
  -> Native Plan Mode
  -> Execute
  -> Tests
  -> Review
```

Specialized architecture skills are inserted only when the task changes something structurally important.

```text
Requirement
  -> architecture-workflow
       -> domain-modeling?       (problem vocabulary changed)
       -> codebase-design?       (module/seam/interface changed)
       -> native Plan Mode
  -> Execute
  -> architecture-review
```

For long-running or multi-agent work, a durable spec/ticket workflow can still be useful. It is conditional, not mandatory.

## Recommended Matt Pocock dependencies

These skills complement rather than replace the following skills from `mattpocock/skills`:

```bash
npx skills add mattpocock/skills \
  --skill domain-modeling \
  --skill codebase-design \
  --skill code-review \
  --skill improve-codebase-architecture
```

Optional:

```bash
npx skills add mattpocock/skills --skill tdd
```

The custom skills will use those skills when available. If they are not available, the custom skills contain enough fallback rules to continue without blocking.

## Install

List skills:

```bash
npx skills add miniliuke/skills --list
```

Install all:

```bash
npx skills add miniliuke/skills --skill '*'
```

Or install only the router and review skills:

```bash
npx skills add miniliuke/skills \
  --skill architecture-workflow \
  --skill architecture-review
```

For Antigravity:

```bash
npx skills add miniliuke/skills --skill '*' --agent antigravity
```

For Claude Code:

```bash
npx skills add miniliuke/skills --skill '*' --agent claude-code
```

For Codex, choose the Codex target exposed by your installed `skills` CLI version.

## Project architecture memory

The workflows use three kinds of project memory, each with a different purpose:

```text
CONTEXT.md
  Domain language only.
  "What do these concepts mean?"

docs/adr/
  Consequential decisions only.
  "Why did we deliberately choose this?"

ARCHITECTURE.md
  Current structural contract.
  "How is the system currently divided and what rules must changes preserve?"
```

Do not use these files as generic design diaries.

### `ARCHITECTURE.md` should stay compact

Recommended sections:

```markdown
# Architecture

## System shape
## Modules and ownership
## Dependency rules
## Public seams
## Extension points
## Runtime / data flow
## Architectural invariants
## Known constraints
```

Prefer explicit statements such as:

```text
Allowed: application -> dataset-api
Forbidden: dataset-api -> connector-mysql
Rule: application must not branch on connector type
```

over generic statements such as "keep coupling low".

## When `to-spec` / `to-tickets` are still useful

Use a durable spec when at least one of these is true:

- the work spans multiple sessions;
- multiple agents or developers will implement it;
- the design changes a core SPI/public contract;
- the reasoning must be recoverable weeks later;
- implementation has multiple independent workstreams.

Use tickets when the work needs parallel ownership, resumable context boundaries, or explicit dependency ordering.

For an ordinary feature handled by one agent in one context, native Plan Mode is usually enough.

## Credits

The workflow is inspired by the engineering practices in [`mattpocock/skills`](https://github.com/mattpocock/skills), especially the separation between domain modeling, codebase design, code review, and periodic architecture deepening.
