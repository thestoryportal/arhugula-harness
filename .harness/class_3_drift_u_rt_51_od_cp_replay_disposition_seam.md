# Class 3 Drift — OD→CP `ReplayDisposition` seam unenumerated at CXA v2.3 §2.3.6

**Class:** 3 (informational; non-blocking)
**Filed:** 2026-05-20 at U-RT-51 landing
**Trigger:** discovery test in `tests/integration/test_cxa_pattern_p1.py`
**Carrier:** CXA v2.3 §2.3.6 OD → CP bucket

## Drift

`harness_od.idempotency_join_dedup` (U-OD-20) does:

```python
from harness_cp.engine_namespace import ReplayDisposition
```

`ReplayDisposition` is a Pydantic-shaped enum exported by CP. This is a
**genuine typed seam** per the CXA v2.3 §0.3 classification ladder
("Consumer imports a Pydantic v2 type / enum / function from the
producer axis package").

CXA v2.3 §2.3.6 enumerates 12 OD→CP relationships, ALL classified as
convention-level or phase-2-runtime — zero genuine. Audit
(`.harness/cxa_7c_audit_od_buckets.md` Bucket 3) did not visit the
`idempotency_join_dedup` import.

## Impact

- U-RT-51 AC "22 identity-equality assertions pass": ✅ unaffected; the
  test asserts the 22 enumerated seams.
- Pattern P1 byte-exact invariant: the import IS byte-exact (Python
  imports normally; identity holds). No actual code defect.
- CXA aggregate counts: 92 canonical relationships, 22 genuine typed
  seams — by the new finding, the genuine count is **at least 23**.

## Resolution

**Allowlisted at U-RT-51 test** as
`(harness_cp.engine_namespace, ReplayDisposition)` with this drift
record as inline rationale. The test passes.

**Owed:** future CXA revision pass adds the U-OD-20 → U-CP-NN(engine
namespace) edge as genuine-typed-seam, bumping the genuine count
22 → 23. Mechanical change to the CXA document; no Python code change.

This is Class 3 because:
- The landed code is correct.
- The CXA classification is mechanically incomplete, not architecturally
  wrong.
- Resolution is documentation-only.

## Provenance

- Detected: AST walk in `test_cross_axis_imports_match_enumerated_seams`
  found the import not in the 22-row enumeration.
- File evidence: `harness-od/src/harness_od/idempotency_join_dedup.py`
  imports line.
- CXA source: `design-substrate/Cross_Axis_Composition_Document_v2_3.md`
  §2.3.6 (OD → CP, 12 declared, 0 genuine).
- Audit source: `.harness/cxa_7c_audit_od_buckets.md` Bucket 3
  (missed the U-OD-20 import).
