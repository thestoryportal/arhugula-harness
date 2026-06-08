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

§13.1 always-on: call advisor() before substantive work and before declaring done; pair it with
decorrelated out-of-family review. Never fire a paid provider call or relocate a secret unilaterally.

## 14. Artifact version lineage

This section is one of two separate provenance archives the always-loaded file accumulated. It
records the per-artifact version history — which version of each spec and plan is canonical and how
each reached its current head. It is pure reference: a reader consults it to trace an artifact, and
it never changes what the agent does. Each entry's lineage is detailed; the retirement events that
drove several of these bumps are logged separately in the retirement archive at §15.

- Spec_Control_Plane v1.30 collapsed the workflow/engine composer signature split per the PR-2 fork
  Reading C; v1.29 added §16.5.12 sidecar discipline; v1.26 rewrote EntryPayload to the IS-HEAD set.
- Spec_Operational_Discipline v1.27 closed the §9.3 tail-keep clause; v1.25 corrected three phantom
  U-RT-30 cite sites; v1.24 retired the derivative AttributeTier naming.
- Implementation_Plan_Control_Plane v2.31 absorbed the v1.30 canonical-reading collapse across
  U-CP-74..79; v2.28 authored six new composer units feeding the CP→IS emission seam.
- Cross_Axis_Composition v2.19 corrected v2.18's erroneous §2.1 matrix and aggregate (105 → 107);
  v2.17 absorbed six CP→IS Pattern-P1 seams into the canonical enumeration.

## 15. Substitution retirement archive

This section is the second provenance archive — the running log of substitution retirement events
under the X-AL-2 criterion. It is likewise pure reference and never changes today's behavior; it
records which H_E substitutions were retired, when, and against which landed units, so the retirement
accounting can be reconstructed. It is referenced from the lineage archive above where a bump was
retirement-driven.

- 2026-05-20: H_T-IS-1 path-class convention substitution retired once U-IS-01 landed and the H_E
  filesystem-classification surface was no longer invoked at the substitution site.
- 2026-05-27: H_T-CP-1 routing substitution retired; this enabled the H_T-AS-8 anthropic.* namespace
  emission per the self-hosting milestone gradient §6.3.1.
- 2026-06-01: the OD condition-(B) live-vs-dormant discriminator closed the first bounded-residual
  retirement, the X-AL-2 condition that the H_E surface is no longer invoked.
- 2026-06-02: the Phase 8 graduation closed substitution accounting at 46 of 54 retired, with the
  derived tally gate guarding against the count-drift defect class.
