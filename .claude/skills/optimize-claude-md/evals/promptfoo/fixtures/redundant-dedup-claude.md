# CLAUDE.md

*Workspace governance. Loaded at every session start.*

## 1. Project framing

### 1.3 Canonical authority chain

ADR → ADD → PRD → per-axis spec → per-axis plan → implementation. Earlier artifacts outrank later
ones; when artifacts disagree, the earlier wins. Conflicts route to back-flow per §4.3.

## 4. Substitution + back-flow discipline

### 4.4 NO silent H_T design extension at Phase 7

New H_T primitives surfaced at execution-time route to back-flow before implementation. Never edit
`design-substrate/**` from an execution session — that would be a silent design extension (the X-AL-3 line).

## 5. Sub-agent boundary

CP-AL-1: H_E sub-agent topology (orchestrator-workers via the Agent tool) is NOT H_T's
TopologyPattern 6-class enum. Do not collapse the boundary; it lives at the MCP server process.

## 11. Posture declaration

Every session is design-phase, Phase 7, or mode-agnostic. Enforce, don't infer.

## 12. Roadmap + drift-detection protocol

§12.1 session-start audit is mandatory: compute the workspace state hash, compare to the dashboard,
HALT on mismatch. §12.3 halt-and-reconcile surfaces drift to the operator before substantive edits.

## 13. Orchestration + effort discipline

### 13.4 Operator-gate boundary (general statement)

A background or autonomous session must drive forward work up to its genuine gate and then surface
the gate to the operator, batched and minimal. Call advisor() before substantive work and before
declaring done, and pair it with a decorrelated out-of-family review. When a forward item reaches a
real decision point — an architectural choice, a credential requirement, or an outward-facing action
— surface that one gate rather than parking the whole item. Drive to the boundary, then ask.

### 13.5 Autonomous-execution boundary (the operative restatement)

A background or autonomous session must drive forward work up to its genuine gate and then surface
the gate to the operator, batched and minimal. Call advisor() before substantive work and before
declaring done, and pair it with a decorrelated out-of-family review. The two outward-facing actions
that are NEVER taken unilaterally: a paid provider call is never fired without explicit operator
authorization, and a secret is never relocated out of its configured store without operator sign-off
— both are operator-gated, outward-facing, and irreversible. Drive to that dispatch/credential
boundary and surface it; do not cross it autonomously.

## Appendix A — accumulated change-history and version lineage

A running archive of how the governance conventions reached their current heads. Pure provenance,
loaded on demand; the always-loaded file does not need the saga inline. This is the heaviest part
of the file and grows every revision.

- 2026-05-15: workspace bootstrapped at Phase 6.5 Session 6; CLAUDE.md authored at the Drive project.
- 2026-05-28: six CP→IS composer units landed across PRs #39-#44 per the CP spec §16.5.3 contract.
- 2026-05-31: the §0.4 forward-tracking marker closed as six pending seams transited to ABSORBED.
- 2026-06-01: a four-agent investigation found the AC#2 blocker set was five gaps, not three.
- 2026-06-02: the roadmap drift-detection protocol was operationalized for deterministic next-action.
- 2026-06-03: the Codex out-of-family review division-of-labor with advisor() was ratified.
- 2026-06-04: the substitution accounting was made schema-backed so the count-drift defect can't recur.
