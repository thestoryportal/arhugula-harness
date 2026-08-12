# Spec: Operational Discipline — v1.41 (delta over v1.40)

*Delta-only file. The v1.40 body + the entire C-OD-01 … C-OD-34 contract body are
PRESERVED VERBATIM (delta-only-spec-file convention). This delta carries exactly ONE
amendment — **C-OD-14 §14.5.3's escalation-on-mismatch table's `validator.fail.class`
row moves `terminal-fail-exit` → `semantic_inconsistency`**, carrying the B-138
operator-ratified disposition (a) (CP spec v1.116, 2026-08-09) into the one OD surface
that still bound the old C5 retry-exit domain to the wire name. The §14.5.3 invariance
check, escalation prose, catalog-extension paragraph, and the table's other three rows
— including `validator.fail.permanence = permanent` and its C-OD-09 §9.2 always-sampled
arm — are UNTOUCHED and PRESERVED VERBATIM.*

**Filed:** 2026-08-12
**Authoring authority:** Register row `B-141`'s owed cascade (surfaced at the B-138
spec-leg out-of-family review round 3, 2026-08-09) under the B-138 operator-ratified
disposition (a): the wire attribute `validator.fail.class` carries the C-CP-25→C-CP-28
§25.2 `ValidatorFailClass` domain (CP spec v1.116; ADR-D5 v1.6 §1.10.1; ADR-D6 v1.3
§1.5.2 amended at this same arc). Applied per workspace `CLAUDE.md` §4.3 back-flow +
§4.5 clearance discipline; back-flow record
`.harness/b-141-validator-fail-class-cascade-2026-08-12.md`.
**Predecessor:** `Spec_Operational_Discipline_v1_40.md` (v1.40 — the `B-144` venue-A
re-table's OD ingestion-count leg; cleared 2026-08-11)
**Revision shape:** Delta-only spec file. v1.41 carries this change-note + exactly ONE
amendment row. **ZERO new contract numbers**; **ZERO roster change**; **ZERO new
namespace**; **ZERO new attribute minted**; **ZERO emission-site change** (zero
production sites construct `ReplaySemanticDivergenceError` at HEAD — declaration +
witness only); **ZERO sampling change** (the always-sampled arm keys on
`validator.fail.permanence`, preserved verbatim); **ZERO Runtime delta**; **ZERO CXA
rows**; **ZERO hash impact**.

---

## Change-note (v1.40 → v1.41)

### §0.1 The defect

C-OD-14 §14.5.3's escalation-on-mismatch table
(`Spec_Operational_Discipline_v1_3.md:223`, the defining venue) fixes
`validator.fail.class = terminal-fail-exit (C5 5-class taxonomy per C-CP-21 §21.5)` on
a cause_attribution-invariance mismatch under `deterministic_replay`. B-138's
operator-ratified disposition (a) settled the wire attribute `validator.fail.class` on
the C-CP-25→C-CP-28 §25.2 `ValidatorFailClass` domain (`schema_violation` /
`semantic_inconsistency` / `safety_policy` / `resource_constraint` /
`external_rejection` — CP spec v1.116), so `terminal-fail-exit` — a
`ValidatorRetryExitClass` retry-exit ROUTING value — is out-of-domain at the wire name.
The as-built carrier tracked the stale value
(`harness-od/src/harness_od/idempotency_join_dedup.py`
`ReplaySemanticDivergenceError.validator_fail_class = "terminal-fail-exit"`, witnessed
at `harness-od/tests/test_idempotency_join_dedup.py`). Zero production emission sites
construct the carrier at HEAD, so the divergence is declared-shape-only — no live wire
value violated the ratified domain before this delta.

### §0.2 The amendment

The §14.5.3 escalation-on-mismatch table's `validator.fail.class` row is superseded:

> `terminal-fail-exit` (C5 5-class taxonomy per C-CP-21 §21.5)

becomes

> `semantic_inconsistency` (v1.41 — `ValidatorFailClass` domain member per CP spec
> v1.116 / B-138 disposition (a): the replay contradicts the F2 ledger's prior recorded
> state. The C5 retry-exit ROUTING classification of this failure remains
> `terminal-fail-exit` per ADR-D5 v1.6 §1.10 — halt + HITL escalation with no recovery
> path — carried by routing and by the §14.5.3 escalation prose, not by this wire
> attribute)

The table's other three rows are PRESERVED VERBATIM: `validator.fail.cause_attribution
= replay_semantic_divergence` (the specific cause, unchanged),
`validator.fail.permanence = permanent` (unchanged — and the always-sampled arm keys on
THIS attribute per C-OD-09 §9.2, so the escalation's always-sampled guarantee is
structurally unaffected by the class-value correction), and the always-sampled row
itself. The §14.5.3 invariance check, the escalation-semantics paragraph (substrate-level
integrity violation requiring operator investigation / HITL escalation), and the
cause_attribution catalog-extension paragraph are PRESERVED VERBATIM.

### §0.3 Same-PR cascade

`ReplaySemanticDivergenceError.validator_fail_class` default `"terminal-fail-exit"` →
`"semantic_inconsistency"` (+ docstring) at
`harness-od/src/harness_od/idempotency_join_dedup.py`, with its witness at
`harness-od/tests/test_idempotency_join_dedup.py` following; all four §14.5.3 fixed
attributes are additionally `Literal`-pinned on the carrier (out-of-family review
round 2) so an out-of-domain override is a construction error — faithful to §14.5.3's
own "fixed" declaration, no value change beyond the class row. Sibling venue legs landing
in the same PR: ADR-D6 v1.2 → v1.3 (§1.5.2 escalation table + §1.2.2.1
`retry.fail_class` cross-reference clause, in place per the ADR-D5 v1.6 mechanics) and
CP plan v2.51 → v2.52 (U-CP-41 / U-CP-47-era as-domain supersession notes; landed units
NOT amended per the B-97(a)/B-118 new-unit precedent).

### §0.4 What this delta is NOT

Not an emission-wiring arc: no production path constructs the carrier at HEAD, and
wiring the §14.5.3 escalation into a live ingestion path stays out of scope per the
register row's own step (3). Not a `retry.*` domain change: `retry.fail_class` keeps
the five-value retry-exit domain (a retry-site routing classification; only ADR-D6
§1.2.2.1's cross-reference CLAUSE is reworded, at the D6 venue). Not a B-124 / B-139 /
B-140 absorption: the permanence-derivation sub-decision stays routed to `B-124`
(CP v1.116 §1.3), `cause_attribution`'s zero-producer state stays tracked at `B-139`,
and the validator.fail span-site/keying divergence stays tracked at `B-140` — the
coordination notes live at the back-flow record §4.

---

*End of v1.41 delta. The v1.40 body and all prior deltas stand unchanged beneath this
file per the delta-only-spec-file convention.*
