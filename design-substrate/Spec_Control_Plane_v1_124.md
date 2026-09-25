# Spec: Control Plane — v1.124 (delta over v1.123)

*Delta-only file. Two amendment sites: C-CP-25 §25.11 grows the closed `ChildResumeRefusal`
enumeration from six to nine values, and C-CP-26 §26.1/§26.6 gains the Control Plane's one public
snapshot-hash verifier. Every other v1.123 and earlier C-CP-01 … C-CP-29 term remains in force. No
contract number, `RunStatus` value or pause-snapshot hash byte is added or changed.*

**Status: cleared — local isolated source contract only, after independent review (marker `.harness/clearance/spec-control-plane-v1-124-cleared-2026-09-25.md`). Not local-RC or installed acceptance.**

**Filed:** 2026-09-25

**Authority:** ratified B-104 at-most-once durable HITL terms, recorded in
`evaluation/production-readiness-arch/b104-operator-amendment-proposal-1.md`. The Opus design
(`evidence-b104-cp-v124-runtime-v130-design-opus-1/SHA256SUMS`, SHA256
`ba3d7edc98d37a4ac17621a466bec45da5114da712ded40252d9a7df82b4dc8c`) named these clauses and held the
refusal mapping until the source could tell a claim-time refusal from a start-time one. That
precondition is now typed in the isolated S1 source at `057a52c99a559c30da324a0291d9570f0ff4cf36`,
which has an Opus precheck GO and an independent Codex source GO at that commit
(`docs/orchestration/review-evidence/b104-s1-codex-source-review-1/SHA256SUMS`, SHA256
`b21c3f73eacc7f44373af24cb1e7618e2903abe34defca980444d36620dfa112`). That source is not in the local RC
and is not bound to any production path, and nothing here asserts clearance or integration of it.

**Predecessor:** `Spec_Control_Plane_v1_123.md`

**Paired Runtime successor:** Runtime v1.130 is cleared as the paired local source contract (marker `.harness/clearance/spec-harness-runtime-v1-130-cleared-2026-09-25.md`). It specifies the store, F1/F2/F3/F4 terms and
the mapping from typed gateway refusals to these reasons. This delta does not install any gateway,
binding, root claim or worker handoff.

## §0 Change-note (v1.123 → v1.124)

### §0.1 The gap

v1.123 closes `ChildResumeRefusal` at six values, all raised before admission: the verification
checks and the not-installed gateway. It has no value for a refusal that happens while a child is
being claimed or durably started, so a future admission that claims through a live parent would have
to overload an existing spelling or invent one. Separately, the hash a `PauseSnapshot` carries could
be recomputed from a snapshot only through a private function, so a Runtime consumer that must check a
parent's carriers either imported the private name or kept its own list of the hashed fields, which
silently misses the next field CP adds.

### §0.2 C-CP-25 §25.11 (AMENDED) — the closed enumeration is nine values

`ChildResumeRefusal` is a closed string enumeration with exactly nine members, spelled as follows
(machine-read). The six filed at v1.123 keep their spellings and meanings: `missing-ref`,
`unreadable-record`, `snapshot-mismatch`, `depth-mismatch`, `gateway-not-installed`,
`workflow-mismatch`. Three are added: `claim-refused`, `claim-busy`, `start-refused`.

The Control Plane treats every member alike, exactly as at v1.123: it records the refusal under its
branch ordinal, a refusal recorded before the barrier ends terminates the run FAILED under §0.3 and
§0.4, and `ChildResumeRefusedError(reason, detail="",
*, audit_signing_failed=False)` is unchanged. The added members describe where the refusal arose,
in the terms a caller can act on:

- `claim-refused`: the claim step refused the exact child record. The record or its parent evidence
  was not admissible (not the latest or not carried by a live, started parent, a depth, hash or
  identity mismatch, an ineligible record, or an unusable lease), or the claim could not read the
  evidence it needed and refused rather than proceed. No claim is left and no child step ran.
- `claim-busy`: another live holder owns the record's lease. No claim was created and no child step
  ran.
- `start-refused`: the claim succeeded but the durable start was refused or could not be made durable.
  The claim on disk is then claimed-only, started or invalid, the lease is released and no child step
  ran.

Which store condition maps to which member is Runtime's contract (Runtime v1.130). The mapping is
typed by the failing step and the kind of error, never by message text. In the isolated S1 source it
is: a refused or busy claim step gives `claim-refused` or `claim-busy`, and a refused start gives
`start-refused`; a placement fault, a journal-lock timeout, an unwrapped I/O error, an error raised by
the child's own body and any other fault are not refusals and propagate as themselves. That source is
not bound to any production path. This delta does not say a child resume uses it.

`claim-busy` is a refusal like any other here. Within the run the Control Plane never retries it,
never re-dispatches that child as fresh work and never re-captures it as a pause. A later resume of
the unchanged parent pause presents the child to Runtime again, which then verifies and admits or
refuses it anew (Runtime v1.130; Task 5). Adding a member remains a contract change here because the
value is written into a fail class.

### §0.3 C-CP-25 §25.11 / §25.15 (AMENDED) — the fail class over nine values

The terminal outcome and the fail-class wire format are exactly those of v1.123 §0.3:
`<family>-child-resume-refused (<reasons>[; audit-signing-failed])`, with `<family>` either
`parallelization` or `orchestrator-workers`, `<reasons>` the distinct recorded reasons sorted
ascending by string value and joined with `"; "`, and `audit-signing-failed` appended last when any
recorded refusal carried it. The new spellings sort among the old by the same rule, for example
`parallelization-child-resume-refused (claim-busy; depth-mismatch; start-refused)` and
`orchestrator-workers-child-resume-refused (claim-refused; snapshot-mismatch; audit-signing-failed)`.
A run that records only the new reasons renders them the same way.

### §0.4 Order of decisions and the recorded-before-the-barrier limit (PRESERVED)

The `proceed` order of v1.123 §0.4 is unchanged and applies to the new reasons without exception: a
refusal recorded before the barrier ends, including `claim-refused`, `claim-busy` or `start-refused`,
yields FAILED even if the barrier deadline also struck; otherwise the deadline yields PARTIAL;
otherwise a paused child yields FAILED as not resumable. The ledger terminals, `final_state` and
`partial_state` both `None`, and the `cascade-cancel` and `pause` statements of v1.123 are unchanged,
as are their evidence limits. The v1.123 §0.5 limit applies equally: a refusal still in flight when
the deadline cancels its branch, including one still inside a claim or start step, is not recorded,
gives PARTIAL with no reason and no suffix, and the child never ran. The result is not a complete
record of refusals, and the at-most-once statement stays narrow: refusal precedes any step of the
child, and the Control Plane supplies neither recency, a claim, a lease nor a `started` barrier.

### §0.5 C-CP-26 §26.1 / §26.6 (AMENDED) — one public snapshot-hash verifier

The Control Plane's module `harness_cp.pause_resume_protocol` exports two functions (machine-read
names):

- `compute_pause_snapshot_hash(snapshot: PauseSnapshot) -> str` returns the hash the snapshot's own
  content hashes to.
- `verify_pause_snapshot_hash(snapshot: PauseSnapshot) -> bool` returns whether the stored
  `snapshot_hash` equals that recomputed hash.

They state, from a snapshot, exactly what §26.1 capture stamps and §26.6 invariant 2 checks:

- **Coverage.** The hash covers eleven inputs: `workflow_id`, `run_id`, `step_index`,
  `state_summary`, the six resume carriers (`fan_out_resume`, `peer_fan_out_resume`,
  `handoff_resume`, `evaluator_optimizer_resume`, `effect_fence_resume`,
  `orchestrator_effect_fence_resume`) and `hitl_gate_config_hash`. Changing any covered field of an
  otherwise valid snapshot makes `verify_pause_snapshot_hash` return `False`, including a nested
  paused child's snapshot or record reference inside a parent's fan-out carrier.
- **Not covered.** `snapshot_hash` (the value being checked), `created_at`, `pause_reason` and
  `state_ledger_anchor` are outside the hash. Changing any of the last three leaves verification
  `True`. Every `PauseSnapshot` field is classified as covered or not covered; adding a field
  requires classifying it, so a new hashed field is a Control Plane change to this one list.
- **Null omission.** A null `child_record_ref` on a paused-child carrier is omitted from the hashed
  serialization at every nesting depth, exactly as v1.122 §0.4 states, so ephemeral and pre-v1.122
  snapshots keep their earlier hash bytes; a non-null reference is covered. The other existing
  drop-when-default rules for additive fields are likewise unchanged. This delta adds none and
  changes no hash byte: the captured hash and the recomputed hash agree for every snapshot shape, and
  the vectors the tests pin for linear, each carrier, and nested children with and without a
  reference are unchanged.
- **Verify's boundary.** `verify_pause_snapshot_hash` returns `False` for a mismatch and for a
  snapshot whose carriers cannot be serialised (one built without validation). A fault of any other
  kind in the computation is not reported as a mismatch; it propagates. A serialised snapshot with an
  unknown field is refused at parse and never reaches the verifier.
- **Single verifier.** A consumer that must check a snapshot's hash uses `verify_pause_snapshot_hash`
  or `compute_pause_snapshot_hash`. It must not import the private computation or re-list the hashed
  fields. The Runtime claim store is the first such consumer (Runtime v1.130).

### §0.6 Preservation

| Element | Disposition |
|---|---|
| v1.123 six spellings, `ChildResumeRefusedError` and `audit_signing_failed` ownership | Preserved unchanged |
| Fail-class format, sorted reasons, suffix last, family names | Preserved; nine values render alike |
| `proceed` order, ledger terminals, `final_state`/`partial_state` `None`, `cascade-cancel`/`pause` statements | Preserved with their v1.123 evidence limits |
| No-retry and no-recapture within the run; later resume re-presents the child | Preserved and extended to the new reasons |
| v1.122 capture, depth, exact record reference and null-omission hash terms | Preserved unchanged |
| Pause-snapshot hash bytes and covered field set | Unchanged; now readable through one public verifier |
| Runtime mapping, store terms, gateway, binding, Task 5b handoff, root `api.resume` | Outside this delta |

## §1 Source, tests and the evidence limits

Sources read for these terms. The nine-value enumeration and the phase/cause mapping are in the
isolated S1 branch `prod/arch-b104-s1-phase-refusal-sonnet-1` at `057a52c9…` (the enumeration in
`harness-cp/src/harness_cp/workflow_driver_types.py`; the typed gateway refusal in
`harness-runtime/src/harness_runtime/lifecycle/started_body_gateway.py`; the unbound mapping in
`harness-runtime/src/harness_runtime/lifecycle/claimed_child_admission.py`). The public verifier and
the eleven-name list are in the local RC at `8762a4c2…` in
`harness-cp/src/harness_cp/pause_resume_protocol.py`. Tests that pin them: for the enumeration, its
closed set, spellings and fail-class rendering, `harness-cp/tests/test_b104_child_resume_refusal_values.py`
(S1 branch); for the verifier, its byte parity against capture, literal vectors, covered/uncovered
inventory, per-field mutation, nested reference coverage and malformed-data boundary,
`harness-cp/tests/test_pause_snapshot_hash_public.py` (RC); for the mapping, the S1 gateway and
admission tests over a real claim store (S1 branch).

Not established. The nine-value source is not in the local RC and is not bound to any production
path: the production stage still binds the always-refusing admission, so no durable child resume
claims or starts, and neither a worker handoff nor a root claim is present. The S1 source has an Opus
precheck GO and an independent Codex source GO at `057a52c9…`; it remains outside the local RC and
unbound to production. The refusal test file that stalled in some earlier runners completed in
later local runs, but no wider Control Plane suite was run for this draft. `cascade-cancel` and `pause`
behaviour remains source-traced as stated at v1.123. No result here is an installed, live-model or
RC-integration witness. Independent review of this delta and Runtime v1.130 clearance are required
before the nine-value source may enter the local RC.
