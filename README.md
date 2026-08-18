# Architecture Skills Bundle

A self-contained set of agent skills for **designing, implementing, reviewing, documenting, and maintaining software architecture with modern coding agents**.

The repository combines:

1. custom architecture workflow skills maintained here; and
2. automatically synchronized stable skills from [`mattpocock/skills`](https://github.com/mattpocock/skills).

The core idea is deliberately lightweight:

> Use the agent's native Plan Mode for ordinary planning. Add specialized skills only when domain, module, interface, documentation, review, or long-lived architecture reasoning is needed.

## Install

List everything available from this bundle:

```bash
npx skills add miniliuke/skills --list
```

Install the complete bundle:

```bash
npx skills add miniliuke/skills --skill '*'
```

For Antigravity:

```bash
npx skills add miniliuke/skills --skill '*' --agent antigravity
```

For Claude Code:

```bash
npx skills add miniliuke/skills --skill '*' --agent claude-code
```

No separate `mattpocock/skills` installation is required when using the full bundle.

## Custom architecture skills

| Skill | When to use | Main outcome |
|---|---|---|
| `architecture-workflow` | Unsure which architecture workflow a task needs | Routes to the lightest appropriate workflow |
| `architecture-documentation` | Documenting an existing project, updating architecture docs, or reconciling docs with code | Accurate current-state architecture documentation without silently redesigning the codebase |
| `new-project-architecture` | Starting a new codebase or major subsystem | Domain model, module map, dependency rules, architecture contract |
| `new-module-architecture` | Adding a module / plugin / subsystem | Justified module seam, interface, dependencies, integration plan |
| `architecture-change` | Changing boundaries, ownership, public interfaces, dependencies, or runtime flow | Architecture impact analysis and migration-safe plan |
| `architecture-review` | Reviewing a plan/diff/PR for structural regressions | Architecture findings independent from ordinary code review |
| `architecture-health` | Periodic architectural maintenance | Prioritized structural improvement candidates |

These names are protected by `.github/custom-skills.txt`; the upstream sync workflow will fail instead of overwriting them if an upstream name ever collides.

## Vendored Matt Pocock skills

The synchronization workflow mirrors all stable skills directly under these upstream groups:

```text
mattpocock/skills/skills/engineering/*
mattpocock/skills/skills/productivity/*
```

Only directories containing `SKILL.md` are mirrored into this repository's top-level `skills/<name>/` layout.

This includes the architecture/development toolchain such as:

```text
domain-modeling
codebase-design
grilling
grill-with-docs
grill-me
to-spec
to-tickets
implement
tdd
code-review
improve-codebase-architecture
diagnosing-bugs
research
prototype
...
```

The entire skill directory is copied, including companion `agents/`, scripts, and reference Markdown files where present.

`deprecated`, `in-progress`, and `misc` upstream groups are intentionally not mirrored into the stable bundle.

## Workflow philosophy

### Ordinary change

```text
Requirement
  -> Native Plan Mode
  -> Execute
  -> Tests
  -> Review
```

Do not invoke extra process just to make a simple change look rigorous.

### Existing project: establish or maintain architecture documentation

```text
Existing codebase
  -> architecture-documentation
      -> Bootstrap   (no authoritative architecture doc)
      -> Update      (verified structural change landed)
      -> Reconcile   (docs may have drifted from code)
```

`architecture-documentation` records the architecture that **exists now**. It separates observed architecture, intended invariants, known deviations, and structural debt. Planned/target architecture must stay in a plan/spec/ADR until implementation and architecture review establish it as current reality.

### New project

```text
Requirement discussion
  -> new-project-architecture
      -> domain-modeling
      -> codebase-design
      -> Native Plan Mode
      -> ARCHITECTURE.md / ADR where useful
  -> Execute
  -> architecture-review
```

### New module

```text
Requirement
  -> new-module-architecture
      -> read CONTEXT / ADR / ARCHITECTURE
      -> justify module boundary
      -> domain-modeling when vocabulary changes
      -> codebase-design
      -> Native Plan Mode
  -> Execute
  -> architecture-review
```

### Architecture-changing feature

```text
Requirement
  -> architecture-change
      -> Architecture Impact
      -> domain-modeling when semantics change
      -> codebase-design when seams/interfaces change
      -> migration / compatibility plan
      -> Native Plan Mode
  -> Execute
  -> architecture-review
  -> architecture-documentation (Update)
```

The documentation update happens after the landed structure is verified, not when the target design is merely planned.

### Periodic health check

```text
Several features / one milestone
  -> architecture-health
      -> improve-codebase-architecture
      -> select only high-value candidates
  -> architecture-change
  -> Execute
  -> architecture-review
  -> architecture-documentation (if structural truth changed)
```

## `to-spec` and `to-tickets`

They remain available in the bundle, but are not mandatory for ordinary single-agent work.

Use a durable spec when:

- work spans multiple sessions;
- several people/agents must share the same design contract;
- a core SPI or public contract changes;
- the reasoning must be recoverable later.

Use tickets when they create useful execution boundaries: parallel ownership, resumability, or explicit blocking order.

## Project architecture memory

Use three kinds of persistent architecture memory for different jobs:

```text
CONTEXT.md
  Domain language.
  "What do these concepts mean?"

docs/adr/
  Consequential decisions.
  "Why did we deliberately choose this?"

ARCHITECTURE.md (or the repo's authoritative architecture doc)
  Verified current structural truth + active constraints.
  "How is the system actually divided now, and what rules should future changes preserve?"
```

`architecture-documentation` maintains the third category and should prefer surgical updates over full rewrites.

Keep architecture documentation compact and explicit. Prefer rules such as:

```text
Allowed: application -> dataset-api
Forbidden: dataset-api -> connector-mysql
Rule: application must not branch on connector type
```

over generic advice such as "keep coupling low".

## Automatic upstream synchronization

`.github/workflows/sync-mattpocock-skills.yml`:

- runs daily and supports manual dispatch;
- clones the current upstream `main` branch without executing upstream scripts;
- mirrors stable `engineering` and `productivity` skill directories;
- removes vendored skills that were removed upstream;
- refuses symlink-containing upstream skill directories;
- refuses collisions with locally maintained custom skill names;
- validates each vendored `SKILL.md` frontmatter name against its directory;
- records the exact upstream SHA in `vendor/mattpocock/UPSTREAM_COMMIT`;
- preserves Matt Pocock's MIT license in `vendor/mattpocock/LICENSE`;
- commits only when the mirrored content actually changes.

## Third-party license

Vendored Matt Pocock content is MIT licensed. See `THIRD_PARTY_NOTICES.md` and `vendor/mattpocock/LICENSE`.

The custom architecture skills in this repository are maintained independently from the vendored upstream content.
