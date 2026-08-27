---
name: tdd-guard
description: "Lightweight TDD behavior guardrail. Use implicitly during implementation when tests are practical: prefer a failing test before production code, then make it pass with the smallest reasonable change, without starting a separate TDD analysis workflow."
---

# TDD Guard

Use TDD as an implementation discipline, not as a separate reasoning workflow.

Do not create an extra TDD plan, seam-design session, test strategy document, or user confirmation step unless the task genuinely needs one.

## Default loop

When a change is testable with the project's existing test setup:

1. Identify the observable behavior being changed.
2. Add or modify the smallest useful test that should fail for the current behavior.
3. Run that focused test and confirm it fails for the expected reason when practical.
4. Make the smallest reasonable production change that satisfies the behavior.
5. Run the focused test again.
6. Run nearby/regression tests as appropriate.
7. Refactor only when it improves the code without changing behavior.

Keep the loop compact. Do not narrate every red/green cycle unless useful to the user.

## Test behavior, not implementation

Prefer tests through an existing public or stable project boundary.

Avoid:

- testing private methods merely to achieve coverage;
- mocks of internal collaborators when behavior can be tested directly;
- assertions coupled to implementation details;
- duplicating the production algorithm inside the expected value;
- creating a new abstraction only to make a test possible unless that abstraction is independently justified.

## Do not redesign the architecture for TDD

Use existing seams whenever they are adequate.

Do not invoke `codebase-design`, `domain-modeling`, or architecture skills merely to decide where one ordinary test belongs.

Escalate design only when the current code has no practical observable boundary and testability exposes a real design problem relevant to the requested change.

## Scope

Prefer one behavior at a time, but do not enforce ritualistic one-assertion or one-test cycles.

For a small bug, a single regression test plus the fix is enough.

For a feature, add tests incrementally around meaningful behavior. Do not write the entire imagined test suite before implementation.

## Exceptions

Do not force test-first when:

- the repository has no usable automated test setup for the affected area;
- the change is documentation, generated output, trivial configuration, or otherwise not meaningfully testable;
- adding the test harness would cost substantially more than the requested change;
- the user explicitly asks not to add tests.

In those cases, use the lightest available verification instead.

## Existing tests

Follow the repository's existing test framework, location, naming, fixtures, and conventions. Read only the nearby tests/configuration needed to do so.

Do not load broad testing guides by default.

## Completion rule

A code change should normally finish with relevant tests passing.

If a test-first step was skipped for a concrete reason, continue the task rather than blocking on process; mention the reason briefly only when it matters.
