# Implementation Plan: Operational Discipline — v2.36 (delta over v2.35)

*v2.36 is the OD plan leg of the **`B-137` step-(3) candidate C1** arc — the posture the operator ratified on 2026-08-16 and that `Spec_Operational_Discipline_v1_42.md` §0.2 lands as C-OD-09 §9.2 **row 20**. Delta-only file: the v2.35 body and every existing `U-OD-NN` body are PRESERVED VERBATIM.*

**Status:** Proposed

---

## §0 Change-note (v2.35 → v2.36)

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_35.md` (v2.35 — the prior OD plan head).

### §0.2 Why this delta exists

OD spec v1.42 §0.2 adds a **twentieth** row to a table whose shipped carrier —
`ALWAYS_SAMPLED_EVENT_CLASSES` at `harness-od/src/harness_od/sampling_mode.py` — is asserted
byte-exact by its own witnesses and whose declared cardinality is restated at five separate
carriers. A spec row that lands without a plan unit leaves the implementation with no
execution-authority carrier and no acceptance criteria, which is the asymmetry v2.32 closed
for the *nineteenth* row (`U-OD-58`, the `B-116-t3` leg). This delta applies the identical
treatment to row 20.

### §0.3 Sections revised

§0 (this change note); §1 (the NEW `U-OD-61` body). All other sections — every existing
`U-OD-NN` body, all dependency graphs, cross-cutting units and coverage tables — are
PRESERVED VERBATIM.

### §0.4 Scope discipline

ADDITIVE — **ONE NEW atomic unit (`U-OD-61`)**, the next free OD unit ID after `U-OD-60`
(verified at authoring: no `U-OD-61` occurrence anywhere in `design-substrate/` or
`.harness/`). **ZERO existing unit amended**; **ZERO new contract number** (C-OD-09 already
exists and v1.42 amends its own table); **ZERO signature change** to any landed unit; **ZERO
CXA rows**. The unit is a membership + count-contract reconciliation, not a new mechanism.

### §0.5 What this delta does NOT carry

Not the C11 volume pricing — the exported-volume multiplier against the C-OD-11 §11.1
per-cell budgets stays at register rows `B-182` / `B-183` and is untouched here. Not
`B-137`'s candidate **A** — no mode-conditional sampler is planned, and A's defining tail
half remains unbuilt. Not a repair for `B-186` (C1's floor under an unsampled ambient OTel
parent), which v1.42 §0.3.1 states as a bound and routes to the register, because the fix is
an emission-site change trading the floor against distributed-trace continuity.

---

## §1 NEW atomic unit — U-OD-61

### U-OD-61 — §9.2 row 20 (`workflow.envelope`) membership + count-contract reconciliation

- **Cluster:** 7 (in-process OTLP collector + sampling discipline)
- **Contract:** C-OD-09 §9.2 (as amended at `Spec_Operational_Discipline_v1_42.md` §0.2)
- **Depends on:** `U-OD-11` (the `ALWAYS_SAMPLED_EVENT_CLASSES` carrier + the SDK-boundary
  literal/prefix decomposition), `U-OD-58` (the row-19 precedent this mirrors)
- **Signatures:** no new signature. `ALWAYS_SAMPLED_EVENT_CLASSES` gains the literal
  `"workflow.envelope"`; the derived `_ALWAYS_SAMPLED_LITERALS` moves 17 → 18 and
  `_ALWAYS_SAMPLED_PREFIXES` is unchanged at 2.

**Acceptance criteria.**

1. **`ALWAYS_SAMPLED_EVENT_CLASSES` gains exactly `"workflow.envelope"`, 19 → 20, and the
   member set is byte-exact against the v1.42 §9.2 table.** Assert `len(...) == 20` **and**
   set-equality against the fixture literal. Byte-exact in both directions: no member added
   beyond the table's twenty, none dropped.
2. **Every live count claim moves in the same commit.** The five carriers are
   `sampling_mode.py` (module docstring, set comment, decomposition note, set literal),
   `alignment_floor_drift_detection.py` (×2), `substrate_seam_exports_aggregate_manifest.py`,
   `tests/test_sampling_mode.py` and `tests/test_composite_sampler.py`. A set whose declared
   cardinality contradicts its own literal is the drift this criterion forecloses.
   **Point-in-time carrier landscapes are NOT amended** — `Spec_Operational_Discipline_v1_27.md:19`
   and v1.37's own nineteen-row statements are timestamped records, correct as of their own
   filing (the v1.37 precedent).
3. **Row 20 resolves through the LITERAL arm, not the prefix arm.** `is_always_sampled("workflow.envelope")`
   is `True`; `is_always_sampled("workflow.envelope.partial")` is `False`. Both directions
   asserted, so a member that accidentally acquired a `.*` suffix cannot silently
   always-sample every descendant.
4. **The floor reaches in-envelope member spans end-to-end at the real venue.** Driving the
   shipped `api.run` path at `base_rate=0.0` with the production sampler exports the envelope
   and its §9.2 children; the same run reconstructed in the pre-v1.42 world exports nothing.
   Both arms required — the as-built assertion alone cannot distinguish "the row works" from
   "the assertion is vacuous".
5. **The ratified cost is measured before the row is called closed — by IDENTITY, not by
   count.** `B-137`'s ratification required the ordinary-child population to be measured at a
   production-bounded cell. Through the real `TailKeepSpanProcessor` at `team-binding ×
   self-hosted-server`: 0 buffered / 0 evicted sequentially. The comparison must be made on the
   SET of traces preserved, not the cardinality — an earlier pass of this very arc concluded
   "no configuration loses a span the status quo would have kept" from equal counts of 8, and
   equal counts turned out to conceal disjoint sets under buffer pressure. At the shipped
   `max_buffered_traces` default the displacement set is empty and the change strictly
   dominates; above the cap it does not, and that residual is registered on its own row rather
   than left on the closed parent.
6. **Mutation-probed.** Removing row 20 from the canonical set must red the as-built witnesses,
   including the positive controls. A membership change no test detects is not landed.

**Tests.** `harness-od/tests/test_sampling_mode.py`,
`harness-od/tests/test_composite_sampler.py`,
`harness-runtime/tests/integration/test_b137_c1_discriminator.py`,
`harness-runtime/tests/integration/test_b137_ninety_two_floor_at_the_real_run_venue.py`.

**Known bound, carried not hidden.** Row 20 delivers the floor by inheritance through
`ParentBased`, which consults the inner sampler only for roots — so the floor holds exactly
while `workflow.envelope` is the trace root. Under an unsampled ambient OTel parent it does
not. Stated at v1.42 §0.3.1, witnessed, and registered at `B-186`.

---

## §2 Coverage delta

C-OD-09 coverage is unchanged in kind — the contract was already covered by `U-OD-11` and
`U-OD-58`; `U-OD-61` adds a third carrier for the same contract's §9.2 table. No contract
gains or loses coverage, and no coverage gap opens.

---

*End of v2.36 delta. The v2.35 body and all prior deltas stand unchanged beneath this file
per the delta-only convention.*
