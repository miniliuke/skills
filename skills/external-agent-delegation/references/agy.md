# AGY role

Use Antigravity as a repository investigator, independent reviewer, and scoped technical-document writer. Invoke it through the wrapper so local CLI differences and permission failures are normalized.

## Good work for AGY

Prefer AGY for:

- repository search and codebase exploration;
- tracing callers, implementations, dependencies, data flow, and configuration paths;
- locating the implementation surface for a change;
- implementation/code review and diff review;
- checking implementation/doc consistency;
- drafting/updating technical documentation from repository facts;
- inventories/maps of modules, APIs, configs, extension points, or ownership.

AGY is read-only by default and returns findings to Codex. Documentation edits may be delegated only when the user requested documentation work, Codex already defined scope, edits stay within documentation paths, and AGY is not deciding architecture.

## Local compatibility and permissions

The wrapper uses the surrounding execution `workdir`; it does not assume AGY supports `--cwd`. CLI flags are discovered from local `--help` and cached by version.

Do not automatically retry permission failures with `--dangerously-skip-permissions`. If the wrapper reports `permission_blocked` and `requires_explicit_authorization`, obtain explicit user authorization first. Only then use wrapper dangerous mode with `--ack-dangerous-permissions`; keep scope narrow and report that permissions were bypassed.

## Do not use AGY for

- architecture ownership;
- product/solution trade-offs;
- ordinary feature implementation;
- broad autonomous refactors;
- final acceptance of its own review findings.

Codex validates important file/symbol references and applies business-code fixes itself.
