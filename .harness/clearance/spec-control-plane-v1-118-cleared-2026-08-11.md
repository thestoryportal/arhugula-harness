---
artifact: design-substrate/Spec_Control_Plane_v1_118.md
version: v1.118
cleared_at: 2026-08-11T21:30:00-07:00
clearance_type: spec-writer-apply-pass
back_reference:
  - ".harness/forward-register.yaml B-153 row (minted at the B-144 venue-A close, PR #1311; CP v1.117 §0.5 quarantine)"
  - ".harness/clearance/spec-control-plane-v1-117-cleared-2026-08-11.md (the predecessor whose §0.5 routed this question here)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - out-of-family `just codex-review` at this leg's PR (to convergence)
  - merge-gate 3-lens (code-touching PR — manifest + tests cascade same-PR)
supersedes: spec-control-plane-v1-117-cleared-2026-08-11.md
---

# Clearance — Spec_Control_Plane v1.118 (B-153 Attribute-count column ratification)

**What v1.118 changes.** The C-CP-24 §24.1 `Attribute count` column receives its
first explicit definition — the namespace's declared live export claim in DISTINCT
attribute keys (span names are not attributes; intra-row cross-event repeats count
once; the v1.117 §0.3 cross-namespace sum caveat stands; parent-span reads are not
row exports). Under it: the §24.1.A `hitl.*` cell moves from the countless
"per-event attributes across 4 span names" to the enumerated **11 attributes across
4 span names** (C-CP-20 §20.6 distinct declared keys — matching the standing OD
commitment at C-OD-05 §5.1 row 6 and `harness_od/namespace_map.py`'s ingested 11);
the `audit.*` qualifier row audited under the same definition and recorded
CONFORMING (§20.4 declares exactly seven distinct keys). Subtotal §24.1.A 35 → 42;
declared CP-axis sum 68 → 75 (42 + 29 + 4).

**Not a design extension (X-AL-3).** No new attribute, namespace, sampling rule, or
contract number — the 11 is an enumeration of already-declared §20.6 keys and the
figure OD has committed to since v1.2. Same-PR cascade (bundled absorption §11.4):
manifest hitl row 4 → 11 + docstrings; acceptance-#6 test renamed
`test_total_attribute_count_seventy_five` (68 → 75); NEW cross-package
map↔manifest witness at `test_lifecycle_od_cp_wiring.py` closing the
#1311-recorded residual (well-defined only under this ratification); companion
plan delta v2.51 (U-CP-54 re-pin). OD side needs NO delta (already correct).

**Register effect.** B-153 CLOSES at this leg (the last of the three B-144
same-class count cases).
