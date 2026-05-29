# Class 1 (halt-execution) — U-RT-35 CP→IS wiring gaps

**Filed at:** U-RT-35 PARTIAL-LAND (2026-05-19)
**Locus:** `Spec_Harness_Runtime_v1.md` §12.3 (CP → IS, 17 edges) vs CP-axis materialized surface
**Status:** **RE-OPENED 2026-05-28 — operator authorized full Phase 6 back-flow (Option A) per deployment-readiness audit AskUserQuestion.** Path D `DEFERRED 2026-05-20` posture supersedes at this re-open. The harness deployment-readiness audit 2026-05-28 identified this fork as the sole remaining genuine deployment-blocker against canonical spec authority (8 other audited rows confirmed bounded-residual per X-AL-2 + 1 stale-ledger row CXA-4 owed separate supersession arc per CXA-5 batch-3 precedent). Empirical re-verification at HEAD `1b46903` 2026-05-28: scope unchanged since 2026-05-20 — all 7 unmaterialized CP source units still absent ledger composers (`per_class_attribute_composition.py` + `workload_binding_engine_class_selection.py` + `pause_resume_protocol.py` adds `emit_pause_captured_span` / `emit_resume_attempted_span` OTel-span emitters but NOT ledger composers + `hitl_as_tool_call_rewriting.py` + `hitl_placement.py` + 2 pause_resume_protocol shared-module entries); U-CP-14 `per_step_override_evaluator.emit_override_audit_entry` shape divergence preserved (still returns `CPAuditLedgerEntry` with 5 missing fields enumerated at §"Gap class B" below). **Phase 7 sub-phase execution HALTED at this workspace** pending operator Phase 6 back-flow authoring at design-phase workspace per workspace `CLAUDE.md` §4.3 + I-5. Resolution requires: (1) CP plan v2.27 → v2.28 revision-pass authoring 7 new composer-units + U-CP-14 shape revision (~20-25 atomic units); (2) CP spec v1.24 amendment widening `CPAuditLedgerEntry` field-set (or authoring sibling `emit_override_state_ledger_entry` variant) per §"Gap class B"; (3) CXA v2.15 → v2.16 bucket refresh at §2.3.1 CP→IS bucket. Authoring composers at the runtime layer would be X-AL-3 silent H_T design extension per workspace `CLAUDE.md` §4.4. U-RT-35 PARTIAL-LAND (1 of 17 edges wired) remains the honest Track-A close state at this workspace.

**Prior status (preserved):** **DEFERRED 2026-05-20 — Path D applied.** Parked with `[[fork-u-rt-44-workflow-loop-drain]]` as a cross-axis future-phase concern. Resolution requires CP-axis composer authoring (7 modules need ledger composers; U-CP-14 needs shape revision) — that's Phase 6 CP plan revision work, NOT Phase 7 runtime work. Authoring composers at the runtime layer would be X-AL-3 silent H_T design extension. U-RT-35 PARTIAL-LAND (1 of 17 edges wired) is the honest Track-A close state.
**Routing:** Phase 6 CP plan revision-pass OR phased per-CP-unit re-land OR scope re-classification of §12.3
**Precedent:** U-RT-30 (trace-storage PathClass gap) — same halt-route-split-AC pattern

## What was landed (PARTIAL-LAND scope)

U-RT-35 landed against the **1 of 9** materialized CP source unit:

- **U-CP-34 (`sibling_ledger_entry_composition`)** — composer exists
  (`construct_sibling_ledger_entry → EntryPayload`) + IS append wrapper
  exists (`append_sibling_ledger_entry → WriteResult`). The runtime
  callback `emit_sibling_ledger_entry` wires this seam end-to-end through
  `ctx.ledger_writer`. Per-edge contract per spec §12.3 satisfied.

## What is STRUCK / DEFERRED

### Gap class A — 7 unmaterialized CP source units (NO composers)

Spec §12.3 enumerates 9 CP source units; 7 have NO ledger-emission
composer module at HEAD:

| CP source unit | Module presence | Composer surface |
|---|---|---|
| U-CP-12 | `per_class_attribute_composition.py` | NO StateLedgerEntry/EntryPayload composer |
| U-CP-27 | `workload_binding_engine_class_selection.py` | NO ledger composer |
| U-CP-30 | `pause_resume_protocol.py` | NO ledger composer |
| U-CP-37 | `hitl_as_tool_call_rewriting.py` | NO ledger composer |
| U-CP-49 | `pause_resume_protocol.py` (shared module) | NO ledger composer |
| U-CP-50 | `pause_resume_protocol.py` (shared module) | NO ledger composer |
| U-CP-52 | `hitl_placement.py` | NO ledger composer |

Each cited spec-§12.3 edge here requires CP-side composer authoring before
the runtime can wire it. Authoring composers at the runtime layer would be
X-AL-3 silent H_T design extension at execution time (per workspace root
`CLAUDE.md` §4.4).

### Gap class B — U-CP-14 composer shape divergence (PARTIAL composer)

`per_step_override_evaluator.emit_override_audit_entry` returns
`CPAuditLedgerEntry`, not `StateLedgerEntry`. Bridging at the runtime
layer would require inventing values not present in the materialized CP
surface:

- `CPAuditLedgerEntry.timestamp: str` is `""` empty placeholder at the
  emission site — no real timestamp on output
- `CPAuditLedgerEntry.prior_event_hash: str` is `"0" * 64` placeholder
- No `idempotency_key` field on CPAuditLedgerEntry; CP spec has no
  idempotency-key formula declared for the override-application surface
- `CPAuditLedgerEntry` carries no `actor: Actor` (it accepts
  `actor: ActorIdentity` as input to `emit_override_audit_entry` but
  doesn't carry it on the returned record)
- `CPAuditLedgerEntry` carries no `response_hash` (StateLedgerEntry's
  6-field shape requires one)

Inventing an `idempotency_key` formula, a `timestamp` value, and an
`Actor` mapping at the runtime layer would author CP spec extensions
inline — exactly what CP-AL-2 (typed taxonomy boundary) and X-AL-3
(no silent H_T design extension at Phase 7) foreclose.

### Gap class C — Spec callable-signature drift (informational, Class 3 weight)

Spec §12.3 declares the wiring contract callable as
`Callable[[StateLedgerEntry], EntryHash]`:

- `StateLedgerEntry` is the IS-exported 6-field shape, but the
  IS `append_ledger_entry` consumes `EntryPayload` (which omits
  `response_hash` + `prior_event_hash` — IS computes both internally).
  Spec implies caller fully composes a `StateLedgerEntry`; IS API
  contract says caller supplies `EntryPayload` and IS computes the
  hash-chain fields.
- `EntryHash` is not a declared IS type. IS append returns
  `WriteResult` (the `APPENDED` / `IDEMPOTENT_NOOP` enum).

This is the same shape as the U-RT-34 Class 3 (spec-prose-plan-body
drift). The materializable surface is unambiguous; spec wording can be
revised in a future runtime spec revision pass.

## Routing options (operator decision pending)

### Option A — CP plan revision-pass (full Phase 6 back-flow)

Author composer modules for the 7 unmaterialized CP source units; extend
`CPAuditLedgerEntry` (or add a CP-side `emit_override_state_ledger_entry`
variant) with the missing fields (`idempotency_key`, `actor`,
`response_hash`, real `timestamp`). Cascade through CP plan v2.x →
spec v1.x revision per `harness-cp/CLAUDE.md` §5.1.

- Blast radius: large (8 CP units affected; CP spec amendment likely
  required for U-CP-14)
- Time: weeks
- Defect risk: low (matches spec intent literally)

### Option B — Phased per-CP-unit re-land (recommended)

Treat U-RT-35 as a deferred-aggregate unit; re-land per-CP-unit when each
source unit's composer lands at CP-axis-stream work. Spec §12.3 already
authorizes split: "Plan v2 U-RT-35 (split-allowed per the plan if
signature divergence surfaces at any source unit)." This is exactly the
split authorization.

Land follow-on units U-RT-35.1 (U-CP-14, after CP spec adds the missing
fields), U-RT-35.2..7 (U-CP-12, 27, 30, 37, 49, 50, 52, after each gets
its composer module). U-RT-35.0 (the U-CP-34 seam) is what landed here.

- Blast radius: small (incremental, per-edge)
- Time: piecemeal as CP units mature
- Defect risk: low (each re-land is bounded to one composer)
- Recommended

### Option C — Re-classify §12.3 to enumerate only materialized edges

Update spec §12.3 to list 1 edge (U-CP-34 → U-IS-11) at HEAD; track the
remaining 16 as deferred per cluster-table notation. CP plan v2.x +
spec v1.x untouched.

- Blast radius: smallest (runtime spec edit only)
- Time: hours
- Defect risk: higher — masks the gap rather than tracking it; risks
  CP→IS wiring being silently underprovisioned at L9 verification

## Recommendation

**Path B.** Smallest incremental risk; matches the spec's own
split-allowed authorization; preserves the 16-edge target as a tracked
backlog (one Class 1 record per re-land) rather than masking it.

## Acceptance criterion split applied

- AC #1 (U-CP-34 → U-IS-11 seam wires; chain integrity passes) — LANDED
- AC #2 (all 17 edges across all 9 source units wire) — STRUCK; routed to
  this Class 1 record
- AC #3 (each per-source-unit emission site invokes the runtime callback
  with `StateLedgerEntry` payload) — STRUCK; routed to Class 1 (depends
  on AC #2 materialization)

## Cross-axis observability

When this Class 1 clears via Path B, the follow-on per-CP-unit landings
(U-RT-35.1..7) close the 16 remaining edges incrementally. Each
follow-on commit records its closure-back-reference in this file.

## See also

- `[[fork-trace-storage-pathclass-gap]]` (U-RT-30 — same halt-route-split-AC pattern)
- `[[spec-prose-plan-body-drift-pattern]]` (Gap class C precedent)
- `[[halt-route-split-ac-pattern]]` (the workspace pattern this applies)
- `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3 (no silent design extension)
- `harness-cp/CLAUDE.md` §4.2 CP-AL-2 (typed taxonomy boundary)

---

## Audit reconciliation (2026-05-20)

**Verified status:** DEFERRED-PARTITION

**Resolving artifact / evidence:** Path D applied 2026-05-20 (U-RT-35 partial-lands 1/17 edges — U-CP-34; remaining 16 deferred to 7c per-CP-unit re-lands as composers materialize). Bounded operator-ratified partition, not open defect.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.


---

## Phase 6 design arc landing (2026-05-28)

Closure-back-reference per §"Cross-axis observability" closure-back-reference discipline. The Phase 6 back-flow authorized at the RE-OPEN (Option A) absorbed across 4 design-substrate artifacts within a single in-CLI design arc, with impl-time grounding pass against `harness-cp/src/harness_cp/` HEAD identifying 2 NOT-APPLICABLE source units (U-CP-12 declarative-only + U-CP-52 runtime-axis-composed) + 3 naming-mismatch corrections (U-CP-27/37/49) at PR #37 in-flight revision:

| Layer | Artifact | Status |
|---|---|---|
| Architect recommendation (within-Path-A Gap B (W/S) resolution + 6 sub-question Q-set) | `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` | **FILED** 2026-05-28 (operator-ratified at AskUserQuestion: (W/S)=S sibling-variant; Q1=Q1(b); Q3=Q3(a); Q4=Q4(b); Q5=Q5(a); Q6=Q6(a)) |
| CP spec v1.24 → v1.25 NEW §16.5 CP→IS state-ledger emission contract (6 composer surfaces at §16.5.2 + 2 NOT-APPLICABLE reclassifications at NEW §16.5.10 per impl-time grounding pass; idempotency-key formulas at §16.5.4; response-hash recipes at §16.5.5; firing-site discipline at §16.5.7; dual-emission discipline at U-CP-14 per §16.5.6; 7 invariants at §16.5.9) | `design-substrate/Spec_Control_Plane_v1_25.md` | **FILED** 2026-05-28 (in-flight revised at PR #37 post impl-time grounding pass) |
| CP plan v2.27 → v2.28 NEW units U-CP-74..79 (6 NEW atomic units per §16.5.2 enumeration; unit count 74 → 80; impl-grounded function refs `select_engine_class`/`rewrite_tool_call_to_hitl`/`capture_pause_snapshot`/`attempt_resume`/`PauseResumeProtocol` class) | `design-substrate/Implementation_Plan_Control_Plane_v2_28.md` | **FILED** 2026-05-28 (in-flight revised at PR #37 post impl-time grounding pass) |
| CXA v2.15 → v2.16 §0.4 forward-tracking marker for §2.3.2 CP→IS bucket evolution (6 PENDING + 2 NOT-APPLICABLE rows; annotation-only; ZERO aggregate count change; per-CP-unit Pattern-P1 enforcement absorption + §2.3.2 canonical revision DEFER to Phase 7 7b consumption arcs) | `design-substrate/Cross_Axis_Composition_Document_v2_16.md` | **FILED** 2026-05-28 (in-flight revised at PR #37 post impl-time grounding pass) |

**Two CP source units reclassified as NOT-APPLICABLE at CP spec v1.25 §16.5.10 per impl-time grounding pass (PR #37 in-flight revision 2026-05-28):**

- **U-CP-12** `per_class_attribute_composition.py` — DECLARATIVE-ONLY module (static `PER_CLASS_ATTRIBUTE_SETS` tuple per C-CP-05 §5.2 + helper `required_attributes_for(...)`; NO runtime composer-action moment; consumers import `SamplingRate` enum only). ZERO CP-axis state-ledger emission edge owed. Runtime spec §12.3 17-edge canonical enumeration carries U-CP-12 as not-applicable-at-CP-side; runtime spec revision aligning the canonical-vs-materialized differential deferred to Gap C resolution arc.
- **U-CP-52** `hitl_placement.py` — RUNTIME-AXIS-COMPOSED (canonical §17.4 `hitl_gate(...)` signature at line 205 raises `NotImplementedError`; production gate body composed at runtime-side `RuntimeHITLGateComposer` per C-RT-18 §14.8). ZERO CP-axis state-ledger emission edge owed at this surface. Future runtime-plan revision should author `emit_hitl_gate_state_ledger_entry` at the runtime composer site — distinct from CP-axis emission discipline.

**Decisive structural argument for (S) sibling-variant.** CPAuditLedgerEntry carries signing contract at C-CP-20 §20.4 → `CPSignedAuditLedgerEntry` signs over the 8-field shape. CP spec v1.7 §13.5.1 NOTE 3 canonicalizes hash-bytes-immutability at signed-payload surfaces. Widening C-CP-16 §16.2 8-field shape would break C-CP-20 §20.4 signing contract OR defeat the widening. (S) preserves §16.2 + §20.4 verbatim → CP→OD converter at v1.7 §13.5.1 unchanged → CP-AL-2 typed taxonomy boundary respected per `harness-cp/CLAUDE.md` §4.2.

**Pending post-Phase-6-design-arc closure of this Class 1 record.** Closure of this fork to RETIRE-READY requires full CP-materializable §12.3 wired:

- 1 edge LANDED at U-CP-34 → U-IS-11 (U-RT-35 PARTIAL-LAND at `2e417e0` 2026-05-21) ✓
- 6 edges PENDING per-CP-unit Phase 7 7b consumption arcs (6 CP plan v2.28 composer landings at U-CP-74..79 + 6 runtime-side materialize-stage helpers at separate runtime-plan revision arc + Pattern-P1 enforcement test absorption + CXA §2.3.2 canonical enumeration revision)
- 2 edges NOT-APPLICABLE at CP-side per CP spec v1.25 §16.5.10 reclassification (U-CP-12 declarative-only + U-CP-52 runtime-axis-composed); Gap C canonical-vs-materialized differential resolution at runtime spec revision pass

H_T-RT-35 PARTIAL → RETIRE-READY transit GATED on full CP-materializable 6-edge wired + Gap C canonical-vs-materialized differential resolution at runtime spec revision. Per-CP-unit landing cadence is operator-discretion at Phase 7 7b consumption rhythm per `Implementation_Plan_Control_Plane_v2_28.md` §0.8(d) and CXA v2.16 §0.4 forward-tracking discipline.

**Carry-forward to Phase 7 7b consumption arcs.** Each per-CP-unit landing at U-CP-74..79 MUST annotate this fork doc with a closure-back-reference per §"Cross-axis observability" discipline. Bundling multiple per-CP-unit landings into a single CXA narrow-scope revision is acceptable per discretion per the v2.9 / v2.15 / v2.16 pattern precedent.

**Impl-time grounding pass catalogued as workspace pattern candidate `[[impl-time-grounding-pass-pre-merge-revision]]`.** When design-substrate authoring depends on assumed function names / module shapes, run a grep sweep against the target modules BEFORE committing to the design-substrate enumeration. Catches catalogued at PR #37 in-flight revision 2026-05-28: 2 declarative-only / runtime-axis-composed architectural reclassifications + 3 function-name mismatches against `harness-cp/src/harness_cp/` HEAD. Force-push pre-merge is cheaper than merge-then-supersede (avoids 5+ sub-species-3 stale-row carry events). Pattern is the inverse temporal direction of the v2.9 / v2.15 CXA narrow-scope-revision precedent — design-substrate followed impl reality at v2.28, rather than impl following spec.

---

## Nested fork surfaced at 7b consumption (2026-05-29)

First 7b consumption attempt against the landed design substrate (PR #37 merge `e6c2f2c` ~30 min prior) surfaced a NESTED Class 1 fork at U-CP-74 pre-substantive: `class_1_tension_u_cp_74_entrypayload_field_set_drift.md`. Two compounding drifts at CP spec v1.25 §16.5.3 + §16.5.5 vs IS HEAD `EntryPayload` (`harness-is/src/harness_is/state_ledger_write.py:62`) + `compute_response_hash` (`harness-is/src/harness_is/entry_hash.py:73`):

1. Field-set drift — spec declares `EntryPayload(action_id, idempotency_key, actor, response_hash)`; IS HEAD has `(action_id, idempotency_key, actor, timestamp)`.
2. Response_hash semantic drift — spec defines as SHA-256 over composer-specific OUTCOME canonical bytes (post-override step-config etc.); IS HEAD defines as SHA-256 over the entry's own canonical form per C-IS-06 §6.2.

Distinct from Gap C drift the spec already acknowledges at §16.5.8 (which is sync/async + StateLedgerEntry-vs-EntryPayload type). Three resolution shapes documented at nested fork: (α) extend IS HEAD; (β) hold IS HEAD, rewrite spec §16.5.3+§16.5.5 to map to actual 4 fields; (γ) sibling typed wrapper CPStateLedgerEntryPayload + runtime translation stage. Recommend **(β.i)** — hold IS HEAD verbatim, fold outcome-bytes hash into idempotency_key derivation suffix; preserves Q5(a) "hash-over-outcome-bytes" ratification at idempotency_key discriminator; ZERO IS-axis cascade; structural mirror of parent fork's (S) sibling-variant resolution.

**Impl-time-grounding-pass pattern sharpened.** PR #37 grounding caught module/symbol existence (2 reclassifications + 3 function-name mismatches) but did NOT verify type-definition field-sets of consumed types. `[[impl-time-grounding-pass-pre-merge-revision]]` candidate pattern sharpened: grounding MUST verify type field-sets when design substrate enumerates per-field semantics for an externally-defined type.

Phase 7 sub-phase 7b cluster {U-CP-74..79} HALTED pending nested-fork resolution. CP spec v1.25 → v1.26 + plan v2.28 → v2.29 cascade owed.

---

## Nested fork β.i resolution applied (2026-05-29)

Closure-back-reference to nested fork `class_1_tension_u_cp_74_entrypayload_field_set_drift.md` filed 2026-05-29 at first 7b consumption attempt against PR #37 design substrate. Operator-ratified β.i resolution + Q-β.i-1(a) + Q-β.i-3(b) absorbed across 2 design-substrate artifacts within a single in-CLI design arc on branch `worktree-u-cp-74-state-ledger-canonicalization` (PR #38):

- **CP spec v1.25 → v1.26** at `design-substrate/Spec_Control_Plane_v1_26.md` (commit `ec4a2f7`) — surgical amendment at §16.5.3 (EntryPayload field set rewritten to IS HEAD's actual 4 fields `(action_id, idempotency_key, actor, timestamp)`) + §16.5.4 (idempotency-key formulas appended with `|| sha256(outcome_canonical_bytes).hex()` suffix per Q-β.i-1(a)) + §16.5.5 chapeau (reframed as outcome-bytes scheme consumed by idempotency_key per Q-β.i-3(b); per-composer outcome-bytes recipe table preserved verbatim) + §16.5.8 Q4 attribution + §16.5.9 invariant 2.
- **CP plan v2.28 → v2.29** at `design-substrate/Implementation_Plan_Control_Plane_v2_29.md` (commit `4cc730b`) — surgical cascade at U-CP-74..79 AC #2 (idempotency_key formula adds outcome-hash suffix) + AC #3/#4 (response_hash reframe — IS-internal not composer-controlled) + Implements citation refresh to spec v1.26 + Tests-list rename at response_hash test entries.

**ZERO IS-axis cascade.** β.i is the structural mirror of (S) sibling-variant from the parent within-Path-A Gap B resolution at architect recommendation: hold the downstream-axis HEAD verbatim, adapt the producer-side composer surface. The (S) precedent's ZERO CP-audit-axis cascade and β.i's ZERO IS-axis cascade share the same architectural commitment.

**`[[impl-time-grounding-pass-pre-merge-revision]]` workspace pattern SHARPENED** at nested fork filing: PR #37's impl-time grounding pass caught module/symbol existence (2 architectural reclassifications + 3 naming mismatches) but did NOT verify type-definition field-sets of externally-consumed types. Pattern update: when design substrate enumerates per-field semantics for an externally-defined type, the grounding MUST verify the type's actual field set against the substrate's claimed field set. This is a strict superset of the v1.25 grounding shape.

Parent fork H_T-RT-35 PARTIAL → RETIRE-READY transit gating per §"Pending post-Phase-6-design-arc closure" section UNCHANGED at nested fork closure: 6 CP-materializable §12.3 edges PENDING per-CP-unit Phase 7 7b consumption arcs at U-CP-74..79; nested fork closure unblocks the 7b consumption (cluster resumption owed at this worktree against v1.26 + v2.29 substrate); 7b consumption landings progressively close the 6 PENDING edges per `Implementation_Plan_Control_Plane_v2_28.md` §0.8(d) + CXA v2.16 §0.4 forward-tracking discipline.

---

## Cluster A library-side COMPLETE (2026-05-29) — runtime-plan revision is the sole remaining design-phase ask

**Cluster A CP→IS wiring library-side 6 of 6 landed on main as of `35744ab` 2026-05-29.** PR ledger:

| PR | Unit | Module | Merge commit |
|----|------|--------|--------------|
| #39 | U-CP-74 | `state_ledger_canonicalization.py` (helper) + `per_step_override_evaluator.py` (sibling) | `e63a600` |
| #40 | U-CP-75 | `workload_binding_engine_class_selection.py` | `332edac` |
| #41 | U-CP-76 | `pause_resume_protocol.py` (workflow-layer + PauseResumeProtocolEventKind enum) | `d745450` |
| #42 | U-CP-77 | `hitl_as_tool_call_rewriting.py` | `4765aaf` |
| #43 | U-CP-78 | `pause_resume_protocol.py` (engine-layer pause-captured) | `a815ac9` |
| #44 | U-CP-79 | `pause_resume_protocol.py` (engine-layer resume-attempted) | `35744ab` |

6 composer surfaces materialized + 1 shared canonicalization helper + 67 new tests + ZERO IS-axis cascade preserved + ZERO CP-audit-axis cascade preserved per β.i resolution. **Per CP spec v1.25 §16.5.10 the 2 NOT-APPLICABLE reclassifications stand**: U-CP-12 declarative-only (no atomic unit owed); U-CP-52 runtime-axis-composed (composer body owed at runtime spec C-RT-18 §14.8 — separate runtime arc).

## What remains — runtime-side wiring atomic unit ABSENT at runtime plan v2.32

**Empirical grep at HEAD against `design-substrate/Implementation_Plan_Harness_Runtime_v2_32.md`:** ZERO occurrences of `ledger_writer`, `U-RT-35`, `16.5`, `resolve_step_binding`, `emit_*_state_ledger`, `append_ledger_entry`. The runtime plan does not have an atomic unit decomposing the runtime-side wiring of the 6 §16.5 composers to `ctx.ledger_writer.append_ledger_entry`. CP plan v2.28 §0 line 55 + line 72 explicitly defer this work to a "separate runtime-plan arc."

The wiring scope (per CP spec v1.26 §16.5.8 + runtime spec v1.7 §14.7.2 step 8 + line 2315):

1. **Binding-registry shape** for the 6 composer surfaces at runtime composition time, calling `ctx.ledger_writer.append_ledger_entry` with the producer-side 4-field `EntryPayload`.
2. **Dual-emission at `resolve_step_binding:179`** per CP spec v1.26 §16.5.8 (the canonical-vs-materialized differential closure noted at the parent fork's §"Gap C").
3. **Bootstrap stage placement** — likely stage-5 LOOP_INIT alongside other CP-axis composer factories, OR a new dedicated stage if cluster-shape diverges.
4. **Factory shape** — operator-discretion: per-source-unit factories (mirrors L9-undecies/L9-quaterdecies precedent) vs single binding registry with composer dispatch table.

Implementing the wiring in-CLI without a runtime-plan atomic unit = **X-AL-3 silent H_T design extension at Phase 7 execution** (workspace `CLAUDE.md` §4.4 + I-2). The spec authority exists (CP spec v1.26 §16.5 + runtime spec v1.7 §14.7.2 step 8); only the plan-side atomic-unit decomposition is missing.

## Phase 6 back-flow ask

| Element | Detail |
|---|---|
| **Routing target** | Phase 6 runtime plan revision-pass at design-phase workspace |
| **Artifact owed** | Runtime plan v2.32 → v2.33 NEW atomic unit (or cluster) decomposing the runtime-side wiring |
| **Architectural choices for the design-phase to ratify** | (a) one unit covering all 6 source-unit wirings, OR split per spec line 2315 if signature divergence surfaces at any source unit; (b) bootstrap stage placement (stage-5 LOOP_INIT vs dedicated stage); (c) factory shape (per-source-unit factories vs single binding registry) |
| **Estimated in-CLI work post-design** | ~30-45 min CC for the wiring unit (binding registry + factory + 6 callsite wirings + stage integration + e2e test against in-process ledger) |
| **Cascade owed at landing** | H_T-RT-35 PARTIAL → RETIRE-READY transit batch (workspace retirement-event ledger filing per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline) + CXA v2.16 §0.4 forward-tracking 6 PENDING → 6 LANDED |
| **Non-blocking carry** | `harness-cp/CLAUDE.md` §1.2 row stale-cite refresh; CXA v2.16 §0.4 narrow-scope revision-pass; both Class 3 informational |

## Status

**Phase 7 sub-phase execution HALTED at this workspace pending operator Phase 6 back-flow authoring at design-phase workspace.** All in-CLI work that was structurally possible against the canonical authority chain has landed. The remaining wiring requires the design-phase to author the runtime-plan atomic unit before in-CLI implementation can proceed without X-AL-3 violation.

Alternative resolution paths the operator may also consider per parent fork's original Path enumeration:

- **Path α (recommended):** Author runtime plan v2.33 at design-phase workspace with NEW U-RT-XX wiring unit. Estimated ~1 short Phase-6 session at design-phase per implementation-planner skill.
- **Path β:** Fork-doc the gap as a sibling Class 1 architectural-tension if the wiring shape surfaces further ambiguity at runtime composition time (not currently anticipated — spec authority is well-defined).
- **Path γ:** Defer indefinitely with bounded-residual H_E-substitution carry if deployment scope does not require the wiring (assistant does NOT recommend — the wiring IS the deployment-readiness gate per the 2026-05-28 audit re-open of this fork).

---

## Path α AUTHORIZED (2026-05-29)

Operator authorized Path α at this session post-PR #45 fork doc closure-event publication. Phase 6 runtime plan revision-pass opens at design-phase workspace for authoring runtime plan v2.32 → v2.33 NEW U-RT-XX wiring unit per §"Phase 6 back-flow ask" above. Phase 7 sub-phase execution at this workspace remains HALTED pending revised runtime plan re-load.

**Next event in this workspace:** Operator pushes revised `Implementation_Plan_Harness_Runtime_v2_33.md` (or higher) to design-phase substrate. On re-load, verify byte-exact integrity + that the NEW wiring unit's signature is materializable against `harness-cp/src/harness_cp/{state_ledger_canonicalization,per_step_override_evaluator,workload_binding_engine_class_selection,pause_resume_protocol,hitl_as_tool_call_rewriting}.py` HEAD per `[[impl-time-grounding-pass-pre-merge-revision]]` sharpened workspace pattern.

---

## Path α first deliverable FILED (2026-05-29)

Closure-back-reference per §"Cross-axis observability" closure-back-reference discipline. Runtime plan v2.32 → v2.33 authored at design-phase per operator AskUserQuestion 2026-05-29 ratifications **Q1=(F) FULL-WIRE-paired + Q2=(C-defer) Gap C deferred**:

| Layer | Artifact | Status |
|---|---|---|
| Runtime plan v2.32 → v2.33 NEW atomic unit U-RT-110 (extends `RuntimeCpIsWiring` with 6 async methods + per-call adapter; preserves `materialize_cp_is_wiring_stage` factory signature; 10 ACs + 6 unit + 1 integration + 1 idempotent-on-replay tests) | `design-substrate/Implementation_Plan_Harness_Runtime_v2_33.md` | **FILED** 2026-05-29 |
| Workspace `CLAUDE.md` §2.4 row bump runtime plan v2.32 → v2.33 | `CLAUDE.md` | **FILED** 2026-05-29 (sibling co-publication this arc) |

**(F) FULL-WIRE-paired cascade owed at runtime plan v2.33 → v2.34 separate arc (corrected per v2.33 §0.3 authoring correction).** v2.33 §0.3 initial draft named "CP plan v2.30" as cascade target; impl-time grounding pass surfaced that U-RT-110's methods (which take `(workflow_id, step_id, per-composer-args, actor)` and orchestrate the composer call) ARE the firing-site at the runtime axis — mirroring U-CP-34 LANDED precedent at `RuntimeCpIsWiring.emit_sibling_ledger_entry`. The 6 LANDED §16.5 composers are pure functions; orchestration belongs at runtime axis per (S) sibling-variant architectural commitment. Cascade target corrected to runtime plan v2.34: 1-3 NEW caller-site invocation units threading U-RT-110's methods into production paths (workflow_driver post-resolve hooks + HITL composer + pause-resume composer + engine-layer free-function callers). PR #52 force-pushed pre-merge to absorb the correction; mirrors PR #37 / PR #38 in-flight-revision-pre-merge precedent.

**H_T-RT-35 PARTIAL → RETIRE-READY transit posture UNCHANGED at v2.33 publication.** Transit requires BOTH halves LANDED (U-RT-110 binding-surface impl + runtime v2.34 caller-site invocation units impl) + e2e verification per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline. Filing the retirement-event-tier transit at v2.33 publication alone is X-AL-2 second-conjunct violation (substituted H_E surface still invoked: production callers bypass U-RT-110's wiring methods until paired runtime v2.34 impl lands). Retirement event filing owed at workspace retirement-event ledger per `[[h-t-cp-19-default-gate-level-spec-extension]]` precedent when both halves materialize.

**CP plan v2.29 → v2.30 NOT OWED.** Initial v2.33 draft named CP plan v2.30 as cascade target; the corrected architectural framing under (S) sibling-variant commitment routes the second half entirely at runtime axis. CP-axis spec v1.26 §16.5 + plan v2.29 composer bodies PRESERVED VERBATIM; ZERO CP-axis cascade owed at the (F) second half.

**Gap C deferred per (C-defer) ratification.** Runtime spec §12.3 prose drift (`Callable[[StateLedgerEntry], EntryHash]` vs IS HEAD `Callable[[EntryPayload], Awaitable[WriteResult]]`) carries to next runtime-spec revision pass per FM-2 + plan-revision-cannot-amend-spec discipline; v2.33 impl conforms to IS HEAD directly per CP spec v1.26 §16.5.8 Q4 ratification anchor; doc-hygiene STRIKE-and-rewrite with ZERO production-code impact.

**CXA v2.16 §0.4 forward-tracking PRESERVED** at v2.33 publication. 6 PENDING entries transit to 6 LANDED at paired-cascade-completion (CXA narrow-scope revision at v2.16 → v2.17 absorbs §2.3.2 CP→IS bucket canonical enumeration refresh per v2.9 / v2.15 / v2.16 precedent at retirement-batch filing arc).
