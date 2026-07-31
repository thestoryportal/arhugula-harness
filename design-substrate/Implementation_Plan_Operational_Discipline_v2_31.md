# Implementation Plan: Operational Discipline — v2.31 (delta over v2.30)

*v2.31 is the OD plan leg **OWED AT THE IMPL LEG** of the RATIFIED **B-69 durable-pause-state read accessor arc** (council record `.harness/council-b69-pause-state-accessor-2026-07-30.md`; **operator ratified OPTION A′ — CO-REQUISITE, SEQUENCED — 2026-07-30**). `Spec_Operational_Discipline_v1_36.md` §30.5.2 states the obligation **unconditionally**: "whichever option the impl leg selects, an OD plan delta is OWED AT THAT LEG, assigning the carrier to an OD unit with its own acceptance criteria (schema shape, frozen/`extra="forbid"` posture preserved, and — for option (a) — a byte-compat witness that every existing `PauseResumeAuditPayload` construction site is unaffected)." **The impl leg selected option (b) — a SIBLING payload type**, so this delta authors **ONE NEW atomic unit, U-OD-57**, carrying that carrier's acceptance criteria. All sections except the §0 change note and the NEW U-OD-57 body + coverage delta below are PRESERVED VERBATIM from v2.30 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.30 → v2.31)

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_30.md` (v2.30 — the B-33 arc's OD plan leg; NEW U-OD-56).

### §0.2 Why this delta exists, and why it could not have been filed at the spec leg

OD spec v1.36's change-note states the position exactly, and it is honored rather than re-litigated here: *"What is deferred is only the SHAPE, not the obligation: pre-authoring a unit for an unchosen carrier shape would fix by plan what §30.5.2 deliberately leaves to impl discretion, so the delta is registered as owed-at-that-leg rather than filed blind."* The shape is now chosen, by execution, so the unit can be authored against a real surface instead of a hypothetical one.

**The choice, and its grounding.** §30.5.2 authorizes **either** (a) an additive field on `PauseResumeAuditPayload` **or** (b) a sibling payload type. **Option (b) is selected.** The grounding is byte-compat cost, not taste: `PauseResumeAuditPayload` is `frozen=True` + `extra="forbid"` and is constructed at every existing pause/resume site through the two §C-OD-30.4 helpers. Option (a) would place a field on every already-shipped row that is never populated on any path those helpers serve — and the field set is not merely additive in effect, because the two new event kinds populate a DISJOINT subset of it (the read event has no `snapshot_hash`, no `step_index`, no `resume_outcome`; the existing events have no token and no counts). A single class serving both would make the union of two disjoint field sets optional on both, which is the illegal-state-representable shape the closed-schema posture exists to prevent. **A sibling leaves the existing field set, both existing helpers, and the existing converter branch unchanged for every event they already handle** — which is exactly what §30.5.2 requires of whichever option is taken.

**What is NOT owed and is stated so the absence reads as a decision.** No OD-side projection helper is authored: the emission's producer is the Runtime pre-bootstrap guard, not a CP lifecycle event, so there is no `(ResumeAttempt, ResumeOutcome)` pair for a helper to compose from — the §C-OD-30.5 obligation is discharged at the Runtime call sites U-RT-148 owns. No converter branch is added: the emission does not route through the CP→OD converter's `resume:` action-id branch at all.

### §0.3 Sections revised

§0 (this change note); §1 (the NEW U-OD-57 body); §2 (coverage delta). All other sections — every existing `U-OD-NN` body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.30.

### §0.4 Scope discipline

ADDITIVE — ONE NEW atomic unit (U-OD-57), the next free OD unit ID after v2.30's U-OD-56. ZERO amended units; ZERO new contract IDs (C-OD-30 already exists — §30.5 is a NEW subsection under it, same contract); ZERO new namespace (the C-OD-05 §5.1 roster is UNCHANGED). ZERO DAG topology change beyond the one new node.

**Dependency direction, stated because the arc's own Runtime plan depends on this unit.** `Implementation_Plan_Harness_Runtime_v2_55.md` records U-RT-148's dependency on "a PENDING, NOT-YET-NUMBERED OD unit" carrying this carrier, precisely so a scheduler would not treat U-RT-148 as ready once U-CP-64 alone landed. **That pending unit is U-OD-57, and it is numbered here.** The two land in the same merge at this impl leg, which satisfies the ordering constraint by simultaneity rather than by sequencing.

---

## §1 U-OD-57 — the §C-OD-30.5 pre-bootstrap pause-state audit carrier (sibling payload)

**Implements:** C-OD-30 §30.5 (NEW at OD spec v1.36) — the additive carrier §30.5.2 authorizes for (i) the Runtime §14.14.9 accessor-read event and (ii) the §30 staleness-refused resume event.

**Depends on:** [U-OD-51 (the C-OD-30 `pause.*` / `resume.*` namespace + `PauseResumeAuditPayload` this unit is a SIBLING to, and whose field set it must leave PRESERVED VERBATIM)].

**Consumed by (cross-axis):** `Implementation_Plan_Harness_Runtime_v2_55.md` U-RT-148 AC #13 — the emission is Runtime-side and pre-bootstrap, so the producing call sites and the sink live there. **A Runtime plan unit cannot own an OD schema surface; this unit owns the schema, that unit owns the emission.**

**Files affected (logical):** `harness-od/src/harness_od/pause_resume_namespace.py` (NEW `PauseStateAuditPayload` + `PauseStateEventKind` + `PAUSE_STATE_EVENT_HEAD_SAMPLING_RATE`; every existing symbol PRESERVED VERBATIM).

### §1.1 Acceptance criteria — by EXECUTION

1. **The carrier is a SIBLING, and the existing payload is PRESERVED VERBATIM.** Assert `PauseResumeAuditPayload`'s field set is byte-unchanged, that it still carries `frozen=True` + `extra="forbid"`, and that it declares NO staleness-token field. *This is §30.5.2's byte-compat witness under the option actually selected: the guarantee option (a) would have owed for every existing construction site is discharged here by the field set simply not moving.* Witness: `test_existing_pause_resume_payload_field_set_is_preserved_verbatim`.
2. **The sibling preserves the closed-schema posture.** `frozen=True` + `extra="forbid"`; an unexpected field is REFUSED, not silently absorbed. Witness: `test_sibling_payload_preserves_the_closed_schema_posture`.
3. **The outcome split is ENFORCED, not documented.** §30.5.1's content rule is asymmetric by construction — a successful read carries a token and FOUR per-variant counts and no cause; a failed read carries a cause and neither; a refusal carries the token and neither. Every illegal combination is REFUSED at construction. **Assert the refusals, not merely that the legal shapes validate** — a documented-only split is one careless call site away from an emission that satisfies the letter of §30.5.1 while carrying a shape the contract forbids. Witnesses: `test_successful_read_carries_four_counts_never_one_aggregate_total`, `test_failed_read_must_emit_and_carries_cause_but_no_token_and_no_counts`, `test_refusal_event_must_carry_the_pairing_token`.
4. **FOUR per-variant counts, never one aggregate total.** Assert a partial count set is refused. *A single scalar cannot express classification, and an aggregate-only carrier would let an implementation pass an execution-authority Runtime AC while violating this canonical OD contract.*
5. **The pairing token is REQUIRED on the refusal event.** §30.5.3 — assert a refusal constructed without it is REFUSED. *Without the pairing key an operator investigating a refusal sees a resume that failed and a read that succeeded with no evidence linking them, and the refusal's own operator-facing text becomes unverifiable after the fact.*
6. **No disclosure channel exists on the payload AT ALL.** Assert the type declares no field for: the locations themselves or their payload; `summary_text` / `state_summary`; `external_references` / `relevant_entries`; `snapshot_hash` / `state_ledger_anchor`; the never-keyable pre-dispatch or depth-0-root internal identity; exception text; a filesystem path. **Absence by TYPE, not by discipline at the call site** — §30.5.1's disclosure limits become invariants an implementation cannot violate even by accident. Witness: `test_no_disclosure_channel_exists_on_the_payload_at_all`.
7. **Both event kinds take the SAME declared head sampling rate.** §30.5.4 — assert the declared constant, and that the event-kind vocabulary is exactly TWO members. *Independent sampling of the two would break §30.5.3's causal-pair reconstruction at exactly the rate it drops either one; "inherit the existing convention" would have left these REQUIRED emissions with no rule at all.* Witness: `test_both_event_kinds_take_the_same_declared_head_sampling_rate`.
8. **NO new namespace, and the C-OD-05 §5.1 roster is UNCHANGED.** Assert the existing 8-attribute `pause.*` / `resume.*` span schema is untouched. *Minting a separate namespace for the middle event of one operator lifecycle would split a causal chain across namespaces for no gain.*

### §1.2 What this unit does NOT own

- **The emission call sites and the pre-bootstrap sink.** Runtime-owned at U-RT-148 (AC #13, including the (a′) fresh-process RETRIEVAL witness). This unit owns the schema the emission composes; it does not own where or when the emission fires.
- **Any OD-side projection helper.** Not owed under the selected option (§0.2) — there is no `(ResumeAttempt, ResumeOutcome)` pair to compose from on a pre-bootstrap path.
- **The redaction posture.** §30.5.4 rules it NOT ENGAGED precisely because nothing redactable is emitted; its reopening condition is registered at `B-99` and is not this unit's scope.

---

## §2 Coverage matrix delta (v2.30 → v2.31)

| Contract surface | Units covering (delta) |
|---|---|
| C-OD-30 §30.5 (NEW at OD spec v1.36 — the B-69 read + staleness-refusal carrier) | **U-OD-57 (NEW)** |

DAG: U-OD-57 added as a new node; in-degree per its `Depends on` (U-OD-51); no existing edge removed or rewired.

---

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_31.md` (delta over v2.30) |
| Authored at | Phase 7 — B-69 durable-pause-state read accessor arc, **impl leg** (2026-07-31) |
| Authoring authority | `Spec_Operational_Discipline_v1_36.md` §30.5.2 (the OD plan delta owed AT THE IMPL LEG under EITHER carrier option) + `.harness/council-b69-pause-state-accessor-2026-07-30.md`; operator ratification 2026-07-30 (OPTION A′) |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_30.md` (v2.30 — B-33 arc) |
| Siblings (same arc) | `Implementation_Plan_Control_Plane_v2_47.md` (U-CP-64 amended) + `Implementation_Plan_Harness_Runtime_v2_55.md` (U-RT-148) — both filed at the SPEC leg; this delta is the one piece §30.5.2 deliberately held for the impl leg |
| Carrier option selected | **(b) sibling payload type** — grounding at §0.2; option (a)'s cost is a never-populated field on every already-shipped row plus a union of two disjoint field sets optional on both |
| Unit-count change | **+1** (NEW U-OD-57) |
| Cluster-count change | None |
| DAG topology change | One new node (U-OD-57); it is the unit `Implementation_Plan_Harness_Runtime_v2_55.md` records as U-RT-148's PENDING, not-yet-numbered OD dependency — numbered here and co-landed |
| Cross-axis cascade | NONE introduced — this unit declares a schema an out-of-axis producer composes, exactly as C-OD-30 already does for the pause/resume pair |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
