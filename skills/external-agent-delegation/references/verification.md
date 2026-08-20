# Verification, parallelism, and failure handling

External-agent output is evidence, not an authoritative final answer. Codex verifies it proportionally to risk.

## Verification

- Test/build result: verify exit status or rerun the decisive narrow command when needed.
- Log extraction: spot-check representative source records.
- Repository search: open important files/symbols before making a design decision.
- Review finding: reproduce or inspect cited code before changing it.
- Documentation: ensure statements describe verified repository reality; planned architecture must not be presented as current architecture.

Never use an external agent's confidence score as a substitute for evidence.

## Parallelism

External agents are most useful when they remove context-heavy chores while Codex continues work that does not depend on their result.

Safe shapes:

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

1. Retry once only when the failure is transient or the command/prompt is trivially correctable.
2. Otherwise continue in Codex or use another appropriate mechanism.
3. Do not create an orchestration loop where agents repeatedly repair each other.
4. Report external-agent unavailability only when it materially affects the result.
