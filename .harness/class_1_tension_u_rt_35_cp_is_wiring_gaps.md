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
