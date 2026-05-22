# Class 3 Drift — OD spec v1.9 §C-OD-30.1 resume.outcome enum-gap vs CP spec v1.11 §26.5 fail-class set

**Filed:** 2026-05-21 (cluster 10-CP-B close, U-CP-65 span emission landing)
**Status:** OPEN bounded — informational; non-blocking
**Routing target:** OD spec v1.10 future revision-pass (paired with next OD-side amendment)
**Detection mode:** U-CP-65 implementation — `_derive_resume_outcome` mapping at `harness-cp/src/harness_cp/pause_resume_protocol.py`

---

## §1 — Defect surface

### §1.1 The enum-gap

CP spec v1.11 §26.5 declares **3 CP fail-classes** for the PauseResumeProtocol:

| Fail class | Trigger |
|---|---|
| `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION` | snapshot_hash doesn't validate on resume |
| `CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED` | STRICT policy + diff detected |
| `CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED` | OPERATOR_ARBITRATE policy + diff → HITL escalation owed |

OD spec v1.9 §C-OD-30.1 declares the `resume.outcome` span attribute as **3-class enum**:

| `resume.outcome` value | Semantic |
|---|---|
| `resumed` | Clean resume (no diff, or LENIENT-with-diff) |
| `diff_aborted` | STRICT abort on material diff |
| `arbitration_owed` | OPERATOR_ARBITRATE HITL escalation owed |

**The gap:** CP fail-class `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION` has no matching `resume.outcome` enum value. The corruption path cannot be observed via the `resume.outcome` span attribute.

### §1.2 Why this is Class 3 (not Class 1)

Multiple valid interpretations exist; none requires halting Phase 7 execution:

1. **Corruption is pre-resume validation failure** — semantically, the snapshot was rejected before the resume was actually "attempted". The §26.4 span trigger is "Resume invoked"; corruption could be argued to fire the `pause.captured` span (capture-side) but NOT `resume.attempted` (resume-side never proceeds past validation). This reading is the U-CP-65 MVP convention.
2. **Corruption could map to `diff_aborted`** — closest semantic match (corruption IS a form of abort). But this conflates two distinct fail modes at the observability layer.
3. **OD spec could extend to 4-class** — add `snapshot_corrupted` outcome value. Minor spec amendment; aligns with CP fail-class enumeration 1:1.

The MVP convention (#1) preserves spec byte-exact; #3 would require an OD spec revision pass paired with a CP spec revision (small amendment).

## §2 — MVP resolution at U-CP-65 landing

**Caller-side guard convention** documented at `emit_resume_attempted_span` docstring:

> Caller convention: DO NOT invoke on corruption path. Per the §C-OD-30.1 `resume.outcome` enum (resumed / diff_aborted / arbitration_owed), corruption has no matching outcome value — corruption is a pre-resume validation failure surfaced via ResumeResult.fail_class. Workflow driver checks `result.fail_class != CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION` before invoking this helper.

The workflow driver (downstream arc owner) is responsible for the corruption-bypass guard at invocation site. U-CP-65 ships with the helper enforcing 3-class enum compliance; corruption-path span emission is explicitly out-of-scope at this unit.

## §3 — Routing recommendation

**OD spec v1.10 amendment (preferred)** — extend `resume.outcome` enum to 4-class:
`{resumed, diff_aborted, arbitration_owed, snapshot_corrupted}`. Small additive patch at §C-OD-30.1; paired with CP spec NOTE at §26.4 making the 1:1 correspondence with §26.5 fail-classes explicit. Co-publish with the next OD-side revision (likely OD plan v2.16 absorbing U-OD-53/54).

**Workflow driver MVP** — caller-side guard at the workflow driver pause/resume hook site (future arc). Mirrors U-CP-61 validator-escalation-fail-class branch handling.

## §4 — Status

- **OPEN bounded** — non-blocking for any downstream cluster open.
- **Resolution target:** OD spec v1.10 (timing: paired with next OD-side substantive amendment per `[[design-substrate-divergence]]` workspace divergence discipline).
- **Affected files when resolved:** OD spec §C-OD-30.1 enum row + CP spec §26.4 NOTE addition. ZERO landed-code change (the `_derive_resume_outcome` helper at `pause_resume_protocol.py` already 1:1 maps fail-class to outcome; adding a 4th branch is mechanical).

## §5 — Cross-references

- `harness-cp/src/harness_cp/pause_resume_protocol.py` `_derive_resume_outcome` + `emit_resume_attempted_span` (caller-side guard docstring)
- CP spec v1.11 §26.4 (span emission table) + §26.5 (fail-class taxonomy)
- OD spec v1.9 §C-OD-30.1 (resume.outcome attribute row)
- `[[carrier-surface-inspection-catches-namespace-collision]]` — sibling cluster-open detection pattern
- `[[class_1_fork_u_cp_63_pause_reason_collision]]` — path γ resolution at this cluster's open
