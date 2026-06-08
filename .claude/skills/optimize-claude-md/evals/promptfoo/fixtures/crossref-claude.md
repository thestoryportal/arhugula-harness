# CLAUDE.md

*Workspace governance. Loaded at every session start.*

## 1. Project framing

### 1.2 Conflict resolution

When two artifacts disagree, do not pick by recency or by which you read first. Resolve the
conflict strictly by the precedence defined in §2.3 — the rule there is the one operative tie-breaker
for the whole workspace, and every other "who wins" decision in this file defers to it.

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

## 2. Canonical artifact pointers + precedence reference

This is the longest section in the file. It records which version of each artifact is canonical,
the full per-artifact amendment lineage so a reader can trace how each one reached its head, and
the precedence rule the rest of the file refers back to. It grows every time any artifact is revised
and is by a wide margin the single heaviest part of the always-loaded file — almost pure reference.

### 2.1 Version lineage table

| Artifact | Version | Lineage |
|---|---|---|
| Spec_Control_Plane | v1.30 | v1.30 collapsed the workflow/engine composer signature split per the PR-2 fork Reading C operator-ratified, superseding v1.29's per-composer table; v1.29 added §16.5.12 sidecar discipline; v1.28 fixed the audit-stub timestamp at three composer sites; v1.27 dropped override_id/policy_id from the idempotency formula; v1.26 rewrote EntryPayload to the IS-HEAD field set; v1.25 authored §16.5 CP→IS emission for six source units. |
| Spec_Operational_Discipline | v1.27 | v1.27 closed the §9.3 tail-keep-on-classification clause via TailKeepSpanProcessor; v1.26 clarified §10.3 per-deployment persona_tier; v1.25 corrected three phantom U-RT-30 cite sites; v1.24 retired derivative AttributeTier naming; v1.23 split requirement-level from stability at §4.3. |
| Spec_Harness_Runtime | v1.41 | v1.41 authored §14.9.8 sandbox-decision-resolver per Reading B; v1.40 added the default-policy converter; v1.39 swapped strictyaml for a pyyaml StrictSafeLoader; v1.38 deferred topology admissibility to runtime; v1.37 added RuntimeConfig.persona_tier. |
| Implementation_Plan_Control_Plane | v2.31 | v2.31 absorbed the v1.30 canonical-reading collapse across U-CP-74..79; v2.30 trimmed the U-CP-14 formula; v2.29 cascaded the EntryPayload suffix; v2.28 authored six new composer units. |
| Cross_Axis_Composition | v2.19 | v2.19 corrected v2.18's erroneous §2.1 matrix and aggregate (105 → 107); v2.17 absorbed six CP→IS Pattern-P1 seams; v2.16 added the §0.4 forward-tracking marker. |

### 2.3 Precedence rule (the tie-breaker §1.2 defers to)

The canonical authority chain is ADR → ADD → PRD → per-axis spec → per-axis plan → implementation.
Earlier artifacts in the chain outrank later ones; when any two artifacts disagree, the earlier link
wins and the conflict routes to back-flow per §4.3. This is the single precedence rule the rest of
the file refers back to — §1.2's tie-breaker has no content of its own; it points here.
