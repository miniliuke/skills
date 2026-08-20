# AGY role

Use Antigravity as a repository investigator, independent reviewer, and scoped technical-document writer. It is useful when the task benefits from reading a lot of repository context without moving ownership away from Codex.

## Good work for AGY

Prefer AGY for:

- repository search and codebase exploration;
- tracing callers, implementations, dependencies, data flow, and configuration paths;
- locating the implementation surface for a requested change;
- implementation/code review;
- reviewing diffs for correctness, regressions, missing tests, and convention violations;
- checking consistency between implementation and existing docs;
- drafting or updating technical documentation from repository facts;
- inventories/maps of modules, APIs, configs, extension points, or ownership.

AGY is read-only by default and should return findings to Codex.

Documentation edits may be delegated only when all are true:

- the user requested documentation work;
- Codex already defined the intended scope;
- edits are limited to documentation paths;
- AGY is not making architecture decisions on Codex's behalf.

## Do not use AGY for

- architecture ownership;
- product/solution trade-offs;
- ordinary feature implementation;
- broad autonomous refactors;
- final acceptance of its own review findings.

Codex validates important file/symbol references and applies business-code fixes itself.
