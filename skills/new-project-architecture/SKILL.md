---
name: new-project-architecture
description: "Design the initial architecture of a new software project or major subsystem before implementation. Use when starting from scratch, selecting module boundaries and dependency direction, defining core domain concepts, or establishing architecture constraints for future agent-driven development."
disable-model-invocation: true
---

# New Project Architecture

Design enough architecture to make the first implementation coherent **without freezing the project into speculative abstractions**.

Use the agent's native Plan Mode for the final implementation plan. This skill provides the architecture reasoning that must happen before that plan.

## 1. Understand the problem before the software shape

Resolve:

- primary user/system goals;
- core workflows;
- external systems and protocols;
- scale/performance constraints that materially affect design;
- reliability/durability/security constraints that materially affect design;
- deployment/operational constraints;
- explicit non-goals.

Do not begin with Controller/Service/Repository, DDD layers, microservices, or framework choices.

## 2. Establish domain language

If `domain-modeling` is installed, use it when core terms are still being defined.

Output a small canonical vocabulary. For each important term, know:

- what it represents;
- what it does not represent;
- who owns its lifecycle/state;
- how it relates to other core terms.

Write resolved vocabulary to `CONTEXT.md` using the domain-modeling conventions. Do not put implementation details there.

## 3. Design the initial modules and seams

If `codebase-design` is installed, use it.

For every proposed module answer:

- What coherent behavior does it own?
- What complexity does it hide?
- What must callers know?
- Why is this a module instead of just local code?
- What can vary independently behind the seam?
- How will behavior be tested through the interface?

Prefer a few deep modules over many shallow wrappers.

Do not create plugin/SPI/factory/provider layers solely because future variation is imaginable. Introduce extension seams when variation is a real requirement or strongly evidenced by the domain.

For load-bearing public interfaces, use a design-it-twice mindset: compare at least two materially different interface shapes before fixing the seam.

## 4. Define dependency direction

Create an explicit module dependency map.

Example style:

```text
application -> domain
application -> dataset-api
domain      -> dataset-api
connector-* -> connector-spi
connector-* -> dataset-api

Forbidden:
dataset-api -> connector-*
domain      -> connector-*
application -> concrete connector implementation
```

The exact architecture is project-specific. The important part is that allowed and forbidden directions are explicit enough for a future agent to check.

## 5. Define extension points only where needed

For each extension point record:

- what varies;
- what is stable;
- who owns the interface;
- at least one concrete reason the seam exists;
- compatibility expectations.

Avoid a type switch in upper layers when implementation-specific behavior belongs behind an existing seam.

## 6. Define runtime and data ownership

Describe the important flows:

```text
request/event
  -> owning module
  -> domain behavior
  -> storage/integration seam
  -> observable result
```

Be explicit about:

- source of truth;
- transaction/consistency boundaries where relevant;
- lifecycle ownership;
- async boundaries;
- failure propagation;
- checkpoints/positions/offsets if the domain needs them.

Do not over-document low-level call graphs.

## 7. Produce the architecture contract

Create `ARCHITECTURE.md` when the design is coherent.

Keep it compact and operational:

```markdown
# Architecture

## System shape
What the system is and the major execution shape.

## Modules and ownership
| Module | Owns | Does not own |

## Dependency rules
Allowed and forbidden dependency directions.

## Public seams
Stable interfaces and what callers may rely on.

## Extension points
Where variation is intentionally supported.

## Runtime / data flow
Only the load-bearing flows.

## Architectural invariants
Rules future changes must preserve.

## Known constraints
Constraints that explain otherwise surprising choices.
```

A good invariant is executable in spirit:

```text
Application code must not branch on connector/database type.
```

A weak invariant is:

```text
Keep the code maintainable.
```

## 8. ADR threshold

Create an ADR only when all are true:

- the decision is hard or expensive to reverse;
- a reasonable engineer could choose another option;
- the reason will be non-obvious later.

Do not create ADRs for ordinary framework defaults or trivial choices.

## 9. Hand off to native Plan Mode

The plan must include:

```markdown
## Architecture Impact
Initial modules:
Public seams:
Dependency rules:
Architecture invariants:
Deferred decisions:
First vertical slice:
Testing strategy:
```

Prefer implementing one end-to-end vertical slice before filling every module with scaffolding.

## Anti-patterns

Reject:

- empty architecture layers created before behavior exists;
- one class/interface per noun without hidden complexity;
- separate abstractions that model the same concept;
- generic "manager", "handler", "util", or "service" buckets without clear ownership;
- a future-proof SPI with only hypothetical adapters;
- architecture docs that describe aspiration rather than the code you are about to build.
