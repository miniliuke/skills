---
name: external-agent-delegation
description: "Delegate bounded software-development work from Codex to external CLI agents. Use proactively for test/build execution, large-log processing, repetitive low-risk analysis, repository/code search, code review, and technical documentation. Keep architecture, solution design, ordinary implementation, and final integration in Codex. Prefer these external agents over Codex native subagents when the task fits their role."
---

# External Agent Delegation

Codex is the **primary agent**. External agents are helpers, not peers and not an orchestration layer.

The goal is to move work to the cheapest capable agent **without moving ownership away from Codex**.

```text
User
  -> Codex: understand / plan / decide
       -> Claude: cheap bounded execution / bulk text work
       -> AGY: repository reading / review / documentation
  -> Codex: synthesize / implement / verify / finish
```

## Roles

### Codex — owner, architect, developer

Keep these in Codex:

- solution design and architecture;
- domain modeling and important trade-offs;
- implementation plans;
- ordinary feature development and bug fixes;
- cross-module decisions;
- API / data-model / persistence design;
- non-trivial debugging that requires hypothesis generation;
- choosing which external findings to trust;
- final code changes, integration, verification, and user-facing answer.

Do **not** delegate important reasoning merely to increase agent usage.

### Claude — cheap, bounded executor

In this environment Claude may be backed by a cheaper/weaker model. Treat it as a high-throughput worker, not a design authority.

Prefer Claude for tasks that are **simple, token-heavy, repetitive, and objectively verifiable**:

- run tests, builds, linters, formatters, benchmarks, or existing repro commands;
- execute a known command matrix and summarize failures;
- read large logs and extract errors, timings, counts, repeated patterns, or suspicious windows;
- cluster or deduplicate repetitive diagnostics;
- compare two large textual outputs when the comparison rule is clear;
- perform mechanical checks against an explicit checklist;
- summarize verbose tool/test output into a compact result.

A Claude task MUST have:

1. bounded input or scope;
2. a concrete operation to perform;
3. an objective completion signal;
4. explicit output requirements.

Good delegation:

```text
Run `mvn -pl connector-mysql test`.
Do not edit files.
Return failing test names, the first causal error for each failure,
and the relevant log excerpt locations. Do not propose architecture changes.
```

```text
Inspect logs/run-2026-08-20.jsonl.
Extract operations slower than 2s, group by operation name,
and report count / p50 / p95 / max plus the five slowest examples.
Do not infer causes unless directly supported by the log.
```

Do NOT use Claude for:

- architecture or solution design;
- open-ended implementation decisions;
- domain modeling;
- subtle code review;
- deciding a root cause from weak evidence;
- modifying production/business code;
- tasks whose correctness cannot be cheaply checked by Codex.

If Claude returns an interpretation rather than evidence, treat it as untrusted input and verify it.

### AGY — repository investigator, reviewer, document writer

Use Antigravity for work that benefits from reading a lot of repository context but does not need Codex to surrender the main task:

- codebase search and repository exploration;
- tracing callers, implementations, dependencies, data flow, and configuration paths;
- locating the implementation surface for a requested change;
- implementation/code review;
- reviewing diffs for correctness, regressions, missing tests, and convention violations;
- checking consistency between implementation and existing docs;
- drafting or updating technical documentation from repository facts;
- producing inventories/maps of modules, APIs, configs, or extension points.

AGY is normally **read-only**. It should return findings to Codex.

For documentation tasks, AGY may edit documentation files when all of the following are true:

- the user requested documentation work;
- Codex has already defined the intended scope;
- edits are limited to documentation paths;
- AGY is not making architecture decisions on Codex's behalf.

Do NOT use AGY for:

- architecture ownership;
- product/solution trade-offs;
- ordinary feature implementation;
- broad autonomous refactors;
- final acceptance of its own review findings.

Codex decides whether AGY findings are valid and applies business-code fixes itself.

## Routing table

| Work | Default owner |
| --- | --- |
| Architecture / solution / trade-offs | Codex |
| Domain modeling | Codex |
| Plan / spec decisions | Codex |
| Ordinary implementation | Codex |
| Complex root-cause reasoning | Codex |
| Run tests / builds / lint / benchmarks | Claude |
| Large log parsing / extraction | Claude |
| Repetitive deterministic analysis | Claude |
| Large output summarization | Claude |
| Repository search / code navigation | AGY |
| Call-chain / dependency investigation | AGY |
| Code / diff review | AGY |
| Technical documentation drafting | AGY |
| Final synthesis / edits / verification | Codex |

When a task contains several kinds of work, split only the **bounded subtask** that fits an external role. Keep the parent task in Codex.

## Prefer external agents over native Codex subagents

When a bounded task clearly fits Claude or AGY, use that external agent instead of spawning a native Codex subagent.

Native Codex subagents are fallback capacity, not the default delegation mechanism. Use them only when:

- the external CLI needed for the role is unavailable or fails;
- the subtask genuinely needs Codex-level reasoning in parallel;
- the user explicitly requests native Codex agents;
- neither external role safely fits the task.

Do not spawn a native Codex agent for test execution, bulk log reading, repository search, routine review, or documentation merely because `spawn_agent` is convenient.

## Delegation threshold

Delegate when at least one of these is true:

- the subtask will consume substantial context/tokens but requires little judgment;
- the subtask can run independently while Codex continues useful work;
- another model reading the repository independently adds review value;
- the task has a clean input/output boundary and cheap verification.

Do not delegate when:

- explaining the task costs about as much as doing it;
- the relevant context exists only in Codex's current reasoning and would need to be reconstructed;
- the action is tiny (one grep, one short test, one small file);
- delegation would put an external agent on the critical path without saving context or improving confidence.

## Invocation patterns

Use the repository root as the working directory unless the task is intentionally narrower.

### Claude / cheap executor

Typical headless call:

```powershell
claude -p "<bounded task; include commands, constraints, and required output>" --output-format json
```

Prompts should explicitly state whether edits are forbidden. For test/log chores, default to **no file edits**.

Do not ask Claude to "investigate and fix". Split it:

```text
Claude: run/extract/measure -> evidence
Codex: reason -> decide -> fix
```

### AGY / repository reader-reviewer

For read-only investigation or review, prefer plan mode:

```powershell
agy -p "<repository investigation/review task; do not edit files>" --cwd "$PWD" --mode=plan --output-format json
```

For an explicitly delegated documentation edit, keep scope narrow and allow edits only for that job:

```powershell
agy -p "Update <specific docs> from verified repository facts. Do not edit source code." --cwd "$PWD" --mode=accept-edits --output-format json
```

Do not rely on prose in the prompt as a security boundary. Use the CLI's configured permissions/sandbox as the actual enforcement mechanism when available.

## Output contracts

External-agent output is evidence/input to Codex, not an authoritative final answer.

Ask Claude to return compact execution evidence:

```text
status
commands_run
failures_or_findings
measurements
relevant_paths_or_log_locations
unresolved_items
```

Ask AGY to return repository-grounded findings:

```text
summary
files_examined
findings (with file/symbol references)
risks
missing_tests_or_docs
recommended_followups
```

Prefer paths, symbols, command names, failing tests, and concrete evidence over long prose.

## Verification rules

Codex must verify external results proportionally to risk.

- Test/build result: verify exit status or rerun the decisive narrow command when needed.
- Log extraction: spot-check representative source lines or records.
- Repository search: open the important files/symbols before making a design decision.
- Review finding: reproduce or inspect the cited code before changing it.
- Documentation: ensure statements describe verified repository reality; planned architecture must not be presented as current architecture.

Never let an external agent's confidence score substitute for verification.

## Parallelism

External agents are most useful when they remove context-heavy chores from Codex.

Safe examples:

```text
Codex designs/implements
  || Claude runs a previously defined test matrix
```

```text
Codex reasons about a change
  || AGY maps callers/dependencies
```

Avoid having Codex, Claude, and AGY edit the same working tree concurrently.

Default write ownership:

```text
business/source code -> Codex
technical docs       -> Codex or explicitly delegated AGY
execution artifacts  -> tools/tests as required
```

## Failure handling

If an external call fails:

1. Retry once only when the failure is transient or the prompt/command is trivially correctable.
2. Otherwise continue in Codex or use the other appropriate mechanism.
3. Do not create an orchestration loop that repeatedly asks agents to fix each other.
4. Report external-agent unavailability only if it materially affected the result.

## Core principle

Optimize for **cost-adjusted capability**:

```text
Codex  = think, design, implement, integrate
AGY    = read broadly, review independently, write docs
Claude = execute cheaply, consume bulk text, return measurable evidence
```

Delegation is successful when Codex keeps the difficult decisions while spending less context and compute on work that does not require them.
