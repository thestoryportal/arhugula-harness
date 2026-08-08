# Implementation Plan: Operational Discipline — v2.32 (delta over v2.31)

*v2.32 is the OD plan leg of the **`B-116-t3`** arc — the NAMED closure gate `Spec_Harness_Runtime_v1.md` v1.112 §14.6.3 term **t3′** registered against the ratified `B-116` package. `Spec_Operational_Discipline_v1_37.md` §1 amends the C-OD-09 §9.2 always-sampled exception set **18 → 19**, adding `fallback.exhausted`; this delta authors **ONE NEW atomic unit, U-OD-58**, carrying that row's realization at the shipped substrate and its fixture conformance. All sections except the §0 change note and the NEW U-OD-58 body + coverage delta below are PRESERVED VERBATIM from v2.31 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.31 → v2.32)

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_31.md` (v2.31 — the `B-69` impl leg's OD plan delta; NEW U-OD-57).

### §0.2 Why this delta exists

OD spec v1.37 §1 adds a nineteenth row to a table whose shipped carrier — `ALWAYS_SAMPLED_EVENT_CLASSES` at `harness-od/src/harness_od/sampling_mode.py` — is asserted **byte-exact against that table** by an existing witness. The contract amendment and the substrate are therefore coupled by an assertion that is live in CI: landing the spec row without the substrate member would fail `test_always_sampled_event_class_members_byte_exact_per_9_2`, and landing the member without the row would be an unauthorized floor extension. **They land together, in one commit, under this unit.**

**Nothing is deferred to a later leg.** Unlike v2.31 — whose spec predecessor deliberately held the carrier's *shape* to impl discretion — the shape here is fully determined by the §9.2 table itself: one unconditional literal member, no new attribute, no new call site. There is no discretionary surface for a later leg to resolve, so the spec leg, the plan leg and the impl land in the same PR.

### §0.3 Sections revised

§0 (this change note); §1 (the NEW U-OD-58 body); §2 (coverage delta). All other sections — every existing `U-OD-NN` body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.31.

### §0.4 Scope discipline

ADDITIVE — ONE NEW atomic unit (U-OD-58), the next free OD unit ID after v2.31's U-OD-57 (verified: no `U-OD-58` occurrence anywhere in `design-substrate/` or `.harness/` before this filing). **ZERO amended units** — U-OD-11's existing acceptance criteria are not rewritten; this unit carries the roster delta and its own witnesses, per the `B-97`(a) → U-RT-149 and `B-96` → U-RT-150 precedent that a landed unit's acceptance criteria are not retroactively re-scoped by a later contract amendment. **ZERO new contract IDs** (C-OD-09 already exists; §9.2 is its own table). **ZERO new namespace** (C-OD-05 §5.1 roster UNCHANGED at 15). **ZERO new cluster.** **ONE new DAG node + ONE new intra-axis edge** (U-OD-11 → U-OD-58). **ZERO cross-axis edges; ZERO CXA rows.**

### §0.5 A pricing correction, recorded rather than silently absorbed

The council record `C-c7-reconcile.md` prices the fixture work as *"four fixture sites / five edit points (`test_sampling_mode.py:24,93,98`; `test_composite_sampler.py:29,55`)"*. Re-grounded by direct read at this filing, **four of those five edit points carry a literal that must move; the fifth (`test_sampling_mode.py:98`) does NOT.** That line is `assert ALWAYS_SAMPLED_EVENT_CLASSES == _EXPECTED_ALWAYS_SAMPLED` — both operands move together, so the *assertion* is byte-unchanged and only its docstring's count claim moves. The count is corrected here rather than carried forward, and the unit's AC #2 enumerates what the re-grounding actually found: **five edit points at the two fixture modules** (two literals + two `len` assertions + two test-function names carrying a spelled-out count, against three docstring/comment count claims that move alongside them), plus **two count claims in shipped `src/` the council never priced** (§0.6).

### §0.6 Two shipped `src/` count claims the pricing missed — found by sweep, reconciled here

A `grep` for count claims over `harness-od/` at this filing found two live carriers outside `sampling_mode.py` that assert the old cardinality in prose and would become **stale-as-described** at this landing:

| Carrier | Claim | Disposition |
|---|---|---|
| `harness-od/src/harness_od/alignment_floor_drift_detection.py` (module docstring, "Plan-vs-spec note") | *"The §9.2 always-sampled exception set (18 rows, landed at U-OD-11)"* and *"the §9.2 set stays closed at 18 rows"* | Reconciled to **19** under this unit. The note's *substance* — that `gen_ai.eval.alignment_floor.drift_detected` is **not** a §9.2 member and takes its head=1.0 posture from §18.2 itself — is UNCHANGED and still true; only the count moves |
| `harness-od/src/harness_od/substrate_seam_exports_aggregate_manifest.py:203` | `export_name="18-entry always-sampled set + 13-entry base-rate set + per-cell envelope"` | Reconciled to **19-entry**. No test asserts this string literal (verified by grep), so the change is a fidelity repair, not a witness-driven one |

Both are in scope for this unit: leaving either would create exactly the **stale-carry-text disposition** defect class the workspace review checklist names. `harness-od/src/harness_od/bridging_arc_table.py:34` was checked and **states no count** — it names the set only — so it is correctly untouched.

### §0.6a Out-of-family review outcome — the realization gap, registered as `B-133`

Out-of-family Codex round 1 against this arc's commit found that **both** §9.2 consumers classify span **names** (`composite_sampler.py:110`; `tail_keep_span_processor.py:259`, which never inspects `span.events`) while **three** §9.2 members are span **events** — `fallback.triggered`, `breaker.tripped` and the row this unit adds — so the head=1.0 floor is realized only insofar as the carrying wrapper span is kept. **Verified true, and verified PRE-EXISTING for the two siblings since original ingestion**, so it is a property of the floor mechanism rather than exposure created here. **Registered as NEW row `B-133`** (same family as `B-123` / `B-124`); the reviewer's redesign remedies were rejected at this leg as an unpriced X-AL-3 extension / an over-sampling of every dispatch wrapper. **U-OD-58's ACs are UNCHANGED** — roster, fixtures, disjointness and PD-8 are all decision- and conformance-level, none of them asserted an end-to-end outcome — but §1.2's scope statements are sharpened so the unit cannot be read as delivering more than it builds.

### §0.7 A witness gap the PD-8 probe found, and why it is closed here rather than registered

`[HIGH]` PD-8 probe (iii) — *revert one fixture literal only* — was run against `test_composite_sampler.py`'s `_LITERAL_ALWAYS_SAMPLED` tuple and came back **GREEN: 96 passed, zero failures.** The mutation was not load-bearing, and the reason is structural rather than incidental: that tuple is a **hand-maintained enumeration consumed only as a `pytest.mark.parametrize` argument**, so dropping a member merely generates *fewer* cases, and every case that remains still passes. Nothing in the module asserted the tuple was **complete** against the canonical set.

That is a live drift hole independent of this arc — any future §9.2 amendment could add a member to `ALWAYS_SAMPLED_EVENT_CLASSES`, update the byte-exact fixture in `test_sampling_mode.py`, and leave the composite-sampler tuple silently short, with the SDK-boundary resolution of the new member never exercised at all. **It is closed here rather than registered as a forward row** because (i) it is inside this unit's own file set, (ii) the repair is one assertion, and (iii) leaving it would make this unit's own AC #7(iii) unsatisfiable — a PD-8 criterion that cannot fail is not a criterion. New witness: `test_literal_fixture_is_complete_against_the_canonical_literal_arm` (`frozenset(_LITERAL_ALWAYS_SAMPLED) == ALWAYS_SAMPLED_EVENT_CLASSES - wildcards`, plus the 17-member count). With it in place probe (iii) re-run **FAILS as required.**

---

## §1 U-OD-58 — the §9.2 row-19 `fallback.exhausted` always-sampled roster addition

**Implements:** C-OD-09 §9.2 row 19 (NEW at OD spec v1.37 §1.1) — the `fallback.exhausted` always-sampled membership closing the CP §3.5 ↔ OD §9.2 ingestion gap.

**Depends on:** [**U-OD-11**] — the unit that owns `harness-od/src/harness_od/sampling_mode.py` and declares `ALWAYS_SAMPLED_EVENT_CLASSES`. *Verified by direct read rather than assumed: the module's own docstring line 1 names it (`"…always-sampled set — U-OD-11"`) and its Authority block cites `Implementation_Plan_Operational_Discipline_v2_5.md §3.4.1 U-OD-11`.* No other dependency is owed — the `is_always_sampled` literal/prefix decomposition and the `HarnessCompositeSampler` / `TailKeepSpanProcessor` consumers all derive from the set at module load and require no edit.

**Consumed by (cross-axis):** **NONE.** The set is OD-owned and consumed only within `harness-od/`; the amendment introduces no cross-package consumption, which is why CXA is unchanged and no seam row is owed.

**Files affected (logical):**

- `harness-od/src/harness_od/sampling_mode.py` — the roster member + every count claim in the module's docstring and inline comments + an Authority-block cite for the amending spec/plan pair.
- `harness-od/tests/test_sampling_mode.py` + `harness-od/tests/test_composite_sampler.py` — the five fixture edit points (§0.5) + THREE new witnesses (the row-19 member witness at the discriminating multi-tenant cell; the unconditional-literal/prefix decomposition witness; the fixture-completeness witness §0.7's probe finding requires).
- `harness-od/tests/test_base_rate_set_and_envelope.py` — **NOT EDITED, deliberately.** AC #4 is satisfied by running it unmodified.
- `harness-od/src/harness_od/alignment_floor_drift_detection.py` + `harness-od/src/harness_od/substrate_seam_exports_aggregate_manifest.py` — the two prose count claims found by sweep (§0.6).

**Scale:** ~1 functional `src` line (the set member); the remainder is count-claim reconciliation and witnesses.

### §1.1 Acceptance criteria — by EXECUTION

1. **`ALWAYS_SAMPLED_EVENT_CLASSES` gains exactly `"fallback.exhausted"`, 18 → 19, and the member set is byte-exact against the v1.37 §9.2 table.** Assert `len(...) == 19` **and** set-equality against the fixture literal. **Byte-exact means both directions**: no member added beyond the table's nineteen, and none dropped. The module's docstring and inline count claims (`"19-entry always-sampled set"` ×2, `"the §9.2 table (19 rows)"`, `"exactly 19 entries per §9.2"`, `"the §9.2 19-entry set"`) are updated in the same edit — a set whose declared cardinality contradicts its own literal is the drift this criterion exists to foreclose. Witnesses: `test_always_sampled_event_classes_cardinality_nineteen`, `test_always_sampled_event_class_members_byte_exact_per_9_2`.
2. **The five fixture edit points are updated, and the enumeration is exhaustive.** (i) `test_sampling_mode.py` `_EXPECTED_ALWAYS_SAMPLED` literal gains the member; (ii) its `len == 18` → `== 19`; (iii) its cardinality test **name** carries a spelled-out count (`…_cardinality_eighteen` → `…_cardinality_nineteen`) and moves with it — *a test name that asserts a stale number is a count claim like any other*; (iv) `test_composite_sampler.py` `_LITERAL_ALWAYS_SAMPLED` tuple gains the member; (v) its `len == 18` → `== 19` and its test name (`…_carries_18_entries_…` → `…_carries_19_entries_…`) with it. The set-equality **assertion** at `test_sampling_mode.py` is byte-unchanged by construction (§0.5); only its docstring count moves.
3. **A member-specific witness exists, at the discriminating cell.** Assert `"fallback.exhausted" in ALWAYS_SAMPLED_EVENT_CLASSES`, that `is_always_sampled("fallback.exhausted")` is `True`, **and** that `sampling_decision` returns `SAMPLE_ALWAYS` at a **multi-tenant-compliance production cell with `base_rate=0.2`** — the cell whose §10.3 base rate is the one §9.2 membership actually overrides in production. *(Precision, per the merge-gate lens-3 review: `sampling_decision` is by contract invariant to its `cell_id`/`base_rate` arguments — the §9.2 membership test alone branches — so this witness discriminates pre- vs post-amendment at EVERY cell equally; the cell choice documents the production stakes, and the base-rate-actually-consulted evidence lives at the composite-sampler `base_rate=0.0` witness.)* Sibling to the existing `test_breaker_tripped_in_always_sampled_set` spot check. Witness: `test_fallback_exhausted_in_always_sampled_set`. **Scope, stated so it is not over-read:** this asserts the **sampling DECISION** the §9.2 substrate returns for the event class — *not* that the event survives to a backend at that cell. Both consumers classify **span names** while this member is a span **event** (OD spec v1.37's honest-scope paragraph), so end-to-end realization is bounded pending **`B-133`**, whose close-out step (1) owns exactly that positive control. An AC here that claimed the end-to-end outcome would be asserting something this unit does not build.
4. **The base-rate disjointness witness is UNMOVED, and this is asserted by RUNNING it unmodified.** `test_regime_disjoint_over_non_kind_discriminated_classes` (`harness-od/tests/test_base_rate_set_and_envelope.py`, the `overlap == DUAL_REGIME_EVENT_CLASSES` assertion) must pass **with zero edits to that module**, because `fallback.exhausted` is absent from the thirteen-member `BASE_RATE_SAMPLED_EVENT_CLASSES` and so contributes nothing to the intersection. *The council record predicted this ("verified NOT to move"); the criterion is that it is verified by execution here, not carried on the prediction.* Corollary: `BASE_RATE_SAMPLED_EVENT_CLASSES` stays at **13** and `DUAL_REGIME_EVENT_CLASSES` stays at **2**.
5. **The literal/prefix decomposition moves to 17 + 2, and the prefix set is UNCHANGED.** Row 19 is an **unconditional literal**, not a wildcard and not a conditional-by-attribute row — so `_ALWAYS_SAMPLED_LITERALS` goes 16 → 17 while `_ALWAYS_SAMPLED_PREFIXES` stays exactly `("audit.", "validator.fail.")`. Assert the new member resolves through the **literal** arm and that `is_always_sampled("fallback.exhausted.detail")` is `False` — *a member that accidentally acquired a `.*` suffix would silently always-sample every `fallback.exhausted.*` descendant.* Witness: `test_row_19_is_an_unconditional_literal_not_a_prefix`. **The composite-sampler fixture tuple is asserted COMPLETE against that same literal arm** (§0.7) — without it the tuple is a parametrize argument that drifts silently. Witness: `test_literal_fixture_is_complete_against_the_canonical_literal_arm`.
6. **The two shipped `src/` count claims found by sweep are reconciled (§0.6),** and `bridging_arc_table.py` is confirmed to carry no count and stay untouched.
7. **PD-8 — the change is load-bearing in BOTH directions, demonstrated by mutation.** (i) Removing `"fallback.exhausted"` from the roster **must fail** the set-equality witness, **both** `len == 19` witnesses, the row-19 member witness, the literal-arm witness, and **both** parametrized composite-sampler cases for the new member. (ii) Adding it to the thirteen-member base-rate set must fail a named base-rate-regime witness — *this is the arm that proves the amendment put the event in the right regime, not merely in a regime*. **Killer named precisely (merge-gate lens-3 correction, verified by off-tree simulation):** in the **added-to-both** direction the AC #4 disjointness witness fails (`overlap` grows past `DUAL_REGIME_EVENT_CLASSES`); in the **moved** direction (removed from always-sampled AND added to base-rate) disjointness still passes — the kills are the base-rate **cardinality-thirteen** witness, the base-rate **byte-exact-per-§10.1** witness, and every always-sampled witness from arm (i). Both directions are killed; neither escapes. (iii) Reverting **one** fixture literal alone must fail the corresponding completeness witness — **and this arm is only satisfiable because §0.7's new witness exists; the probe was GREEN before it, which is the gap §0.7 records.** Each probe: apply, observe the named failures, restore, re-verify green. **Restoration is by file copy from a pre-probe backup, never `git checkout`** — the working tree carries uncommitted arc content a checkout would destroy.
8. **Zero new attributes, zero emission-site changes, zero CP delta, zero CXA rows.** Assert by absence: `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py` (the single `fallback.exhausted` emission site, `:947`) is **untouched** in this arc's diff, as is every `harness-cp/` file. *This unit moves a sampling disposition; if the diff reaches an emission site, the scope claim is false.*

### §1.2 What this unit does NOT own

- **The `B-116` waiver guard and its t1/t2 waived-charge attributes.** Runtime-owned at U-RT-152 (Runtime plan v2.60), merged separately as PR #1271. This unit discharges the *other* half of the `B-116` gate — the observability-floor **membership**, which is the content §14.6.3 t3′ and the council's own pricing named — and touches none of that surface.
- **The floor's END-TO-END REALIZATION at the SDK boundary.** Registered as **`B-133`**. This unit lands the roster row and its witnesses; it does **not** make the event survive a base-rate drop of the wrapper span that carries it, because both §9.2 consumers classify span **names** while this member is a span **event** — a **pre-existing** property of the mechanism, shared with `fallback.triggered` and `breaker.tripped` since original ingestion. *Stated here rather than left implicit: the gate's ratified content was the roster + fixtures, so discharging it is not the same as delivering the realized floor, and conflating the two would let this unit claim more than it built.*
- **Whether the CP `:409` tail-keep mitigation is live.** Registered as `B-123`. The §9.2 head=1.0 **contract** does not depend on that trigger's answer (OD spec v1.37 change-note ground 3) — but its **realization** shares `B-123`'s root cause (span-name-vs-span-event) and is `B-133`'s scope; the two rows are one family and should be dispositioned together.
- **The inert `validator.fail.permanence` §9.2 row** (`B-124`) and the `harness.breaker.tool_id` homonym (`B-125`). Both are pre-existing §9.2-adjacent conditions, neither is a precondition of row 19, and neither is repaired here.
- **The multi-tenant chain-exhaustion volume question.** OD spec v1.37's rider-(a) record establishes the **structural** result (the per-cell budget enforces downstream of sampling); the population figure is explicitly unmeasured and no acceptance criterion depends on one.

---

## §2 Coverage matrix delta (v2.31 → v2.32)

| Contract surface | Units covering (delta) |
|---|---|
| C-OD-09 §9.2 row 19 (NEW at OD spec v1.37 — the `B-116-t3` `fallback.exhausted` always-sampled membership) | **U-OD-58 (NEW)** |

DAG: U-OD-58 added as a new node; in-degree per its `Depends on` (**U-OD-11**) — **one new intra-axis edge, U-OD-11 → U-OD-58**; no existing edge removed or rewired; **no cross-axis edge**.

---

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_32.md` (delta over v2.31) |
| Authored at | Phase 7 — the `B-116-t3` OD leg (2026-08-08) |
| Authoring authority | `Spec_Operational_Discipline_v1_37.md` §1 (the row this unit realizes); `Spec_Harness_Runtime_v1.md` v1.112 §14.6.3 term **t3′** (the NAMED closure gate); council record `.harness/council/b116-breaker-semantics/01-council/contributions/C-c7-reconcile.md` t3-leg registration (the pricing, corrected at §0.5/§0.6) |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_31.md` (v2.31 — the `B-69` impl leg) |
| Siblings (same arc) | `Spec_Operational_Discipline_v1_37.md` — filed in the SAME PR, together with the implementation. `Implementation_Plan_Harness_Runtime_v2_60.md` U-RT-152 is the `B-116` arc's OTHER half and merged separately at PR #1271 |
| Unit-count change | **+1** (NEW U-OD-58) |
| Cluster-count change | None |
| DAG topology change | One new node (U-OD-58); one new intra-axis edge (U-OD-11 → U-OD-58); **zero cross-axis edges** |
| Cross-axis cascade | **NONE** — the amended set is OD-owned and OD-consumed; no new cross-package consumption, so the CXA aggregate stays frozen at 111 and no row is owed |
| Register consequence | **`B-116` CLOSES at this leg** — §14.6.3 t3′ required BOTH the impl leg (U-RT-152, PR #1271) and this t3 leg; with this delta both have landed |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
