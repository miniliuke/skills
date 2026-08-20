# AGY role

Use Antigravity as a repository investigator, independent reviewer, and scoped technical-document writer. It is useful when the task benefits from reading a lot of repository context without moving ownership away from Codex.

Before invoking AGY, follow [`cli-runtime.md`](cli-runtime.md) and inspect the locally installed `agy --help` before relying on flags. Do not assume examples from another host or version are supported.

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

## Local CLI compatibility

Prefer the surrounding execution tool's `workdir` for repository context. Do not add `--cwd` unless the installed AGY version actually exposes it.

Do not assume a `--sandbox` flag or permission mode exists or is usable. Validate supported permission/sandbox options from local help before constructing the command.

If normal execution and supported least-privileged modes are blocked, stop and surface the constraint. Do **not** automatically fall back to `--dangerously-skip-permissions` or an equivalent bypass.

A dangerous permission-bypass flag is allowed only when:

1. the local CLI documents/supports it;
2. the ordinary invocation cannot run for an environment/permission reason;
3. the user explicitly authorizes that degraded permission mode for the task;
4. scope is kept as narrow as possible;
5. Codex reports that the invocation ran with bypassed permissions.

Never encode dangerous permission bypass as a default command example.

## Output and path handling

Treat AGY structured output as a transport envelope according to [`cli-runtime.md`](cli-runtime.md). Preserve outer status/usage metadata when present and parse the semantic result separately.

On Windows, verify suspicious or mojibake non-ASCII paths against the filesystem before using them for edits or conclusions.

## Do not use AGY for

- architecture ownership;
- product/solution trade-offs;
- ordinary feature implementation;
- broad autonomous refactors;
- final acceptance of its own review findings.

Codex validates important file/symbol references and applies business-code fixes itself.
