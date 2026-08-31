# Minimal Engineering Guardrails

Use this together with Ponytail. Ponytail owns YAGNI, reuse-first decisions, and minimum implementation. Do not duplicate those rules here.

## Ordinary work

- Use the agent's native planning and execution flow.
- Do not start a skill workflow merely because a skill is installed.
- Read only the code, tests, and documentation needed for the current change.
- Prefer the existing project structure and conventions.

## Architecture safety

For ordinary changes, preserve these unless the task explicitly requires changing them:

- module ownership and lifecycle ownership;
- intended dependency direction;
- established public APIs/SPIs, persistence/wire/event contracts, and seams.

Before adding a module, interface, service, adapter, manager, registry, or layer, check whether an existing abstraction can coherently own the behavior.

If a structural change is unavoidable, state the concrete architecture impact briefly. Do not automatically start an architecture workflow; use `architecture` when architecture work is explicitly requested.

## Lightweight TDD

When the changed behavior is testable through the project's existing test setup:

1. Add or adjust the smallest useful test that fails for the current behavior.
2. Confirm the focused failure when practical.
3. Make the smallest implementation change that satisfies it.
4. Run the focused test and relevant nearby regression tests.

Test observable behavior rather than private implementation details. Do not create an abstraction solely to satisfy a testing ritual.

Skip test-first when there is no practical test setup, the change is documentation/generated/trivial configuration, or creating a harness would cost substantially more than the change. Use the lightest useful verification instead.

## Skill routing

Use a specialist skill only when the task genuinely matches it:

- `architecture` — explicit architecture design/change/review/documentation/health work.
- `codebase-design` — load-bearing module/interface/seam design.
- `domain-modeling` — unresolved domain concepts, terminology, state, or lifecycle ownership.
- `diagnosing-bugs` — difficult diagnosis, complex incidents, hard-to-reproduce failures, or performance regressions; not obvious local bug fixes.
- `grilling` — explicit stress-testing/interview of a plan, design, or decision.
- `writing-for-agents` — agent-facing instructions, context, or documentation.

Prefer at most one primary skill per task. Do not cascade skills into a fixed pipeline. A supporting skill is justified only when it solves a separate real problem.
