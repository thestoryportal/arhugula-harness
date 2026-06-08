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

## 2. Canonical artifact pointers, per-axis version lineage, and the full accumulated amendment history of every design-substrate artifact since the Phase 6.5 bootstrap

The following is the complete, exhaustively-detailed, per-artifact canonical version-pointer table
together with the entire accumulated change-note lineage tracing how each artifact reached its
current head — the single longest and most verbose section in this governance file, preserved here
for readers who need to reconstruct the provenance of any individual design-substrate decision.

| Artifact | Version | Full accumulated amendment lineage |
|---|---|---|
| Spec_Control_Plane | v1.30 | v1.30 collapsed the workflow/engine composer signature split per the operator-ratified Reading C, superseding v1.29's per-composer table; v1.29 added the §16.5.12 sidecar discipline; v1.28 fixed the audit-stub timestamp at three composer sites; v1.27 dropped override_id and policy_id from the idempotency formula; v1.26 rewrote EntryPayload to the IS-HEAD field set; v1.25 authored §16.5 CP→IS emission for six source units. |
| Spec_Operational_Discipline | v1.27 | v1.27 closed the §9.3 tail-keep-on-classification clause via the TailKeepSpanProcessor; v1.26 clarified §10.3 per-deployment persona_tier; v1.25 corrected three phantom U-RT-30 cite sites; v1.24 retired the derivative AttributeTier naming; v1.23 split requirement-level from stability at §4.3. |
| Implementation_Plan_Control_Plane | v2.31 | v2.31 absorbed the v1.30 canonical-reading collapse across U-CP-74..79; v2.30 trimmed the U-CP-14 formula; v2.29 cascaded the EntryPayload suffix; v2.28 authored six new composer units across the §16.5 emission surface. |
| Cross_Axis_Composition | v2.19 | v2.19 corrected v2.18's erroneous §2.1 matrix and aggregate from 105 back to 107; v2.17 absorbed six CP→IS Pattern-P1 seams at rows 38-43; v2.16 added the §0.4 forward-tracking marker that v2.17 then closed. |
