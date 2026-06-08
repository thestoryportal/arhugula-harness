# CLAUDE.md

*Workspace governance, loaded every session.*

## 1. Project framing

### 1.3 Canonical authority chain

ADR → ADD → PRD → per-axis spec → plan → implementation. Earlier artifacts outrank later ones;
when artifacts disagree, the earlier wins. Conflicts route to back-flow per §4.3.

## 4. Substitution + back-flow discipline

This section governs how execution-time forks route back to the design phase. The routing rules
below are operative — the agent obeys them every session.

### 4.3 Back-flow routing

Class 1 forks halt sub-phase execution and route to the design-phase channel; Class 2 surface to
the operator; Class 3 are logged. Silent absorption of a design defect is the worst failure mode.

### 4.4 NO silent H_T design extension at Phase 7

New primitives surfaced at execution-time route to back-flow before implementation. Never edit
`design-substrate/**` from an execution session — that would be a silent design extension (X-AL-3).

### 4.5 Amendment log for §4

*Provenance only — every revision this discipline has been through. This is the bulk of the
section and is reference, not rule; it belongs in git, loaded on demand.*

- 2026-06-01: v1.41 split Class-2 from Class-3 after the four-agent investigation showed operator
  surfacing and logging are distinct routes; eleven new routing sanity tests added that day.
- 2026-05-31: v1.40 reworded the §4.4 imperative from "avoid editing" to "never edit" after a
  near-miss where an execution session opened a spec file; the stronger verb was deliberate.
- 2026-05-29: v1.39 folded the old §4.6 "escalation ladder" back into §4.3 as redundant; the
  ladder restated the Class-1/2/3 split with different words and drifted out of sync twice.
- 2026-05-28: v1.38 added the "silent absorption is the worst failure mode" line to §4.3 after a
  retro found three silently-absorbed defects had each propagated to multiple dependent units.
- 2026-05-27: v1.37 first separated back-flow routing from the substitution-retirement prose that
  had been fused into one wall of text since the original draft; readability win, no rule change.

## 5. Sub-agent boundary

CP-AL-1: H_E sub-agent topology (orchestrator-workers via the Agent tool) is NOT H_T's
TopologyPattern 6-class enum. Do not collapse the boundary; it lives at the MCP server process.

## 11. Posture declaration

Every session is design-phase, Phase 7, or mode-agnostic. Don't infer posture silently.

## 12. Roadmap + drift-detection protocol

§12.1 session-start audit is mandatory: compute the workspace state hash, compare to the dashboard,
HALT on mismatch. §12.3 halt-and-reconcile surfaces drift to the operator before substantive edits.

## 13. Orchestration + effort discipline

§13.1 always-on: call advisor() before substantive work and before declaring done; pair it with
decorrelated review. Never fire a paid provider call or relocate a secret unilaterally.
