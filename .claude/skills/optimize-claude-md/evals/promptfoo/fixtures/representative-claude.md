# CLAUDE.md — representative governance fixture (eval input, NOT the live file)

*Mirrors the real root CLAUDE.md shape: short load-bearing sections + a dominant §2
version-lineage section that is relocatable bulk. The optimization target: relocate §2 to a
referenced home, keep every load-bearing rule, break no pointer. Frozen for reproducible scoring.*

## 1. Project framing

### 1.3 Canonical authority chain

ADR → ADD → PRD → per-axis spec → per-axis plan → implementation. Earlier artifacts outrank
later ones; when artifacts disagree, the earlier wins. Conflicts route to back-flow per §4.3.

## 2. Canonical artifact pointers (version lineage — the relocatable bulk)

*This section is provenance. It carries which version of each artifact is canonical plus the
full amendment saga. Provenance lives in git; a CLAUDE.md does not need to carry the saga — this
is the bytes, and the relocation target (leave a resolving pointer; move the lineage to a home).*

| Artifact | Version | Lineage |
|---|---|---|
| Spec_Control_Plane | v1.30 | v1.30 collapsed the workflow/engine composer signature split per the PR-2 fork Reading C operator-ratified, superseding v1.29's per-composer table; v1.29 added §16.5.12 sidecar discipline; v1.28 fixed the audit-stub timestamp at three composer sites; v1.27 dropped override_id/policy_id from the idempotency formula; v1.26 rewrote EntryPayload to the IS-HEAD field set; v1.25 authored §16.5 CP→IS emission for six source units. |
| Spec_Operational_Discipline | v1.27 | v1.27 closed the §9.3 tail-keep-on-classification clause via TailKeepSpanProcessor; v1.26 clarified §10.3 per-deployment persona_tier; v1.25 corrected three phantom U-RT-30 cite sites; v1.24 retired derivative AttributeTier naming; v1.23 split requirement-level from stability at §4.3. |
| Spec_Harness_Runtime | v1.41 | v1.41 authored §14.9.8 sandbox-decision-resolver per Reading B; v1.40 added the default-policy converter; v1.39 swapped strictyaml for a pyyaml StrictSafeLoader; v1.38 deferred topology admissibility to runtime; v1.37 added RuntimeConfig.persona_tier. |
| Implementation_Plan_Control_Plane | v2.31 | v2.31 absorbed the v1.30 canonical-reading collapse across U-CP-74..79; v2.30 trimmed the U-CP-14 formula; v2.29 cascaded the EntryPayload suffix; v2.28 authored six new composer units. |
| Cross_Axis_Composition | v2.19 | v2.19 corrected v2.18's erroneous §2.1 matrix and aggregate (105 → 107); v2.17 absorbed six CP→IS Pattern-P1 seams; v2.16 added the §0.4 forward-tracking marker. |
| Architectural_Design_Document | v1.3 | v1.3 consolidated ADR-F1..F5 + D1..D6 into a coherent overview; v1.2 added the sandbox tier-set; v1.1 was the first consolidation. |
| PRD | v1.1 | v1.1 added the observable-behavior acceptance surface; v1.0 was the initial product requirements. |

## 4. Substitution + back-flow discipline

### 4.3 Back-flow routing

Class 1 forks halt sub-phase execution and route to the design-phase channel; Class 2 surface to
the operator; Class 3 are logged. Silent absorption of a design defect is the worst failure mode.

### 4.4 NO silent H_T design extension at Phase 7

New H_T primitives surfaced at execution-time route to back-flow before implementation. The skill
must never edit `design-substrate/**` — that would be a silent design extension (the X-AL-3 line).

## 5. Sub-agent boundary

CP-AL-1: H_E sub-agent topology (orchestrator-workers via the Agent tool) is NOT H_T's
TopologyPattern 6-class enum. Do not collapse the boundary; it lives at the MCP server process.

## 8. Execution invariants

I-6 framework-pull discipline holds — no tenacity / pybreaker / langgraph / temporal / LiteLLM.

## 11. Posture declaration

Every session is design-phase, Phase 7, or mode-agnostic. §11.5 enforcement layers: self-discipline,
skill-side §0 check, CI guard, clearance markers. Don't infer posture silently.

## 12. Roadmap + drift-detection protocol

§12.1 session-start audit is mandatory: compute the workspace state hash, compare to the dashboard,
HALT on mismatch. §12.3 halt-and-reconcile surfaces drift to the operator before substantive edits.

## 13. Orchestration + effort discipline

§13.1 always-on: call advisor() before substantive work and before declaring done; pair it with
decorrelated out-of-family review. Never fire a paid provider call or relocate a secret unilaterally.
