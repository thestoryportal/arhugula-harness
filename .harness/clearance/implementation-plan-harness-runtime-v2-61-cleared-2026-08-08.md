---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_61.md
version: v2.61
cleared_at: 2026-08-08T00:00:00-06:00
clearance_type: ratified-fork-apply-pass
back_reference:
  - .harness/forward-register.yaml row `B-115` (disposition (b′), recommended at the #1265 grounding commit `05abb419`; status `registered_finding` → `closed` at this PR)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.113 §14.6.3 (the spec leg, landing in the SAME commit — row 6 discharged, guard tuple four → five, `B-132` narrowed)
  - .harness/clearance/spec-harness-runtime-v1-113-cleared-2026-08-08.md (the paired spec marker)
  - design-substrate/Implementation_Plan_Harness_Runtime_v2_60.md U-RT-152 (LANDED + CLOSED at PR #1271 — NOT amended here; U-RT-153 is a NEW unit per the `B-97`(a) → U-RT-149 and `B-111` → U-RT-151 precedent)
  - PR '#pending' (this arc)
merge_commit: pending
reviewer_chain:
  - ratified-fork apply pass — U-RT-153 decomposes the (b′) disposition and NOTHING beyond it. Reading (a) (provider joining the capture identity) is NOT built, NOT re-priced and NOT reopened; the duplicate-RECORD half is explicitly retained; `B-132`'s remainder is explicitly out of scope.
  - unit-shape determination, stated because it is a judgement call — U-RT-152 is LANDED and CLOSED, so its ACs are NOT amended: a MUST added to a closed unit would falsify its closure criterion retroactively. A NEW unit is the shape, matching the two most recent precedents in this same plan file (`B-97`(a) → U-RT-149; `B-111` → U-RT-151). The v2.60 body, its closure criterion and its §2 rider are PRESERVED VERBATIM.
  - DAG-edge justification — the U-RT-152 → U-RT-153 edge is real rather than nominal: U-RT-153 extends the tuple and predicate U-RT-152 introduced, and AC #4 asserts over both. ZERO cross-axis edges: `harness_runtime` → `harness_is` is a pre-existing package dependency (`memory_capture.py` already imports the ledger's conflict type), and the determinism witnesses' placement in `harness-is/tests` creates no plan-graph edge. CXA aggregate frozen at 111 — determined, not assumed: the leg introduces no cross-package consumption, so nothing is owed.
  - build-time correction absorbed into the unit body — implement item 2 was authored as a propagation and REWRITTEN as a value discriminator after the existing suite falsified it (`FAILED`-on-conflict is contracted for two of `_capture`'s six entry points, U-MEM-26 / Codex R6+R8). AC #9 was ADDED to pin the correction: the two U-MEM-26 witnesses must pass UNMODIFIED, which is the only thing that demonstrates the leg left the other five entry points alone.
  - round-2 AC completion, recorded at §0.3-bis of the plan — out-of-family review round 1 found AC #2's chaining requirement unmet on the capture surface. The AC was NOT weakened to match the implementation; the implementation was completed to match the AC, and the AC was then STRENGTHENED (every surface must chain, plus a joint symmetry witness — the observed failure mode was two-of-three chaining, which per-surface witnesses alone do not catch). Two PD-8 probes added.
  - round-3 correction, recorded at §0.3-ter of the plan — the retained live exception regressed the publicly-exported result model's `model_dump_json()` and `model_json_schema()`. Round 2's "never serialized" grounding is RETRACTED as too narrow (it covered current callers, not the reachable API surface of an exported type). Fixed by exclusion + skip-schema rather than a string serializer, on one-source-of-truth grounds: `failure_reason` already carries the same fact, so a serialized copy would be a drifting duplicate. AC #2 gained the serialization-contract obligation and AC #8 an eighth probe.
  - acceptance-criteria review — NINE ACs, each traced to an obligation rather than to a code shape. AC #1 carries the four-part determinism definition the spec's row-6 condition demands and pins its LEDGER placement as required-not-incidental; AC #3 is structural (a source-level single-direct-append assertion) because a behavioural sweep cannot cover a fourth append site that does not exist yet; AC #4 asserts the partition in FOUR directions because a one-sided assertion passes against a wholesale family reclassification; AC #6 PRESERVES the `B-84` W-5 `== 2` assertion verbatim so the leg cannot claim a closure it did not deliver; AC #7 enumerates every landed witness touched, with the store-error staircase-charge control explicitly STAYING with unchanged assertions.
supersedes: implementation-plan-harness-runtime-v2-60-cleared-2026-08-08.md
---

# Clearance — `Implementation_Plan_Harness_Runtime_v2_61.md v2.61`

v2.61 is the `B-115` (b′) plan leg: **ONE new unit (U-RT-153), ZERO amended units, ONE new DAG edge (U-RT-152 → U-RT-153), ZERO cross-axis edges, ZERO CXA rows, ZERO contract numbers, ZERO `snapshot_hash` impact, ZERO Memory-plan delta.**

U-RT-153 carries the split in four implement items — the new memory-family SIBLING type with its three shape constraints; the capture-boundary VALUE discriminator that makes the deterministic refusal distinguishable at all (a closed `MemoryCaptureFailureKind` enum plus an optional `failure_kind` field; the closed two-value `MemoryCaptureStatus` enum is NOT widened, and propagating was tried and falsified — see the correction note above); the THREE executor re-type surfaces routed through ONE shared helper; and the paired classifier-admission / waiver-tuple move, which MUST happen together because §14.6.3's classifier-consistency rule makes a one-sided change silently wrong.

Its nine ACs and the CONJUNCTIVE closure criterion include one requirement worth naming here: the determinism witnesses must be green **before** the src change as well as after. They are ledger-level and must not depend on the split — if they only pass afterwards, they are witnessing the implementation rather than the property the spec's row-6 condition asks about.

Scope discipline recorded in the unit's own Out-of-scope list rather than left implicit: Reading (a); the duplicate-RECORD half; `B-132`'s remainder; the dedicated C-MEM-19 class (forward row `B-134`); `memory_promotion`'s same-shaped append (outside the three ratified surfaces, recorded in the partition witness docstring as a remaining raw-escape path); and the dead half-open latch (`B-118`), inherited unchanged.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
