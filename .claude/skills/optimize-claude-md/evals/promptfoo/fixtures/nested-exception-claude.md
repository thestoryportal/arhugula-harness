# CLAUDE.md

*Workspace governance. Loaded at every session start.*

## 1. Project framing

### 1.3 Canonical authority chain

ADR → ADD → PRD → per-axis spec → per-axis plan → implementation. Earlier artifacts outrank later
ones; when artifacts disagree, the earlier wins. Conflicts route to back-flow per §4.3.

## 4. Substitution + back-flow discipline

### 4.4 NO silent H_T design extension at Phase 7

New H_T primitives surfaced at execution-time route to back-flow before implementation. A Phase 7
session must never edit `design-substrate/**` — except a bundled-absorption arc that already carries
back-flow documentation in the same change, which is not a violation but must first halt and route
through the §11 Posture declaration gate before any edit, so the mixed-edit scope is operator-acknowledged
rather than silently absorbed. Drop that exception and a legitimate absorption arc is wrongly blocked;
keep it without the gate and silent absorption slips through. Both halves are the rule.

## 5. Sub-agent boundary

CP-AL-1: H_E sub-agent topology (orchestrator-workers via the Agent tool) is NOT H_T's
TopologyPattern 6-class enum. Do not collapse the boundary; it lives at the MCP server process.

## 12. Roadmap + drift-detection protocol

§12.1 session-start audit is mandatory: compute the workspace state hash, compare to the dashboard,
HALT on mismatch. §12.3 halt-and-reconcile surfaces drift to the operator before substantive edits.

## 13. Orchestration + effort discipline

§13.1 always-on: call advisor() before substantive work and before declaring done; pair it with
decorrelated out-of-family review. Never fire a paid provider call or relocate a secret unilaterally.

## 9. Background + accumulated rationale

This section carries the accumulated rationale behind the disciplines above — the long-form
reasoning a reader can consult to understand why each convention exists. It is the heaviest block in
the file, almost entirely explanatory background, and none of it changes what the agent must do today.

The substitution discipline traces to the meta-architecture's 49-row mapping table and the X-AL-2
retirement criterion; the reason retirement is event-driven rather than scheduled is that a primitive
is only genuinely retired once its units have landed and the substituted surface is no longer invoked,
and trying to retire on a calendar produced partial-retirement defects in early sub-phases.

The authority chain ordering traces to the foundational ADR set: ADR-F1 through ADR-F5 plus the
derivative ADR-D1 through ADR-D6, consolidated into the Architectural Design Document and then the
PRD, so the ordering is not arbitrary but reflects which artifact each later one was derived from.

The roadmap drift-detection protocol was operationalized after repeated sessions silently drifted from
the dashboard's recorded next-action; the fixed-point refresh clause exists specifically to stop the
refresh PR from recursively triggering another refresh, which it would otherwise do on every merge.

The orchestration matrix distinguishing solo / advisor / council / workflow was distilled from a
retrospective that found the cheap verification disciplines, not heavy multi-agent fan-out, are what
actually catch the bugs, so the matrix deliberately makes the heavier machinery opt-in, not default.
