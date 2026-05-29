# Spec: Control Plane — v1.26 (delta over v1.25)

---

## Change-note (v1.25 → v1.26)

**Scope of revision.** Surgical amendment at v1.25 NEW §16.5 sub-section absorbing operator-ratified resolution of nested Class 1 fork `.harness/class_1_tension_u_cp_74_entrypayload_field_set_drift.md`. Resolution shape **β.i** ratified at AskUserQuestion 2026-05-29: hold IS HEAD `EntryPayload` verbatim; rewrite §16.5.3 to declare actual 4-field shape `(action_id, idempotency_key, actor, timestamp)`; relocate outcome-bytes semantic from `response_hash` field to `idempotency_key` derivation suffix per §16.5.4. Sub-question ratifications: **Q-β.i-1=(a)** append outcome-hash to existing per-composer disambiguator (preserves §16.5.4 formula chain verbatim; +1 segment per row); **Q-β.i-3=(b)** reframe §16.5.5 chapeau as outcome-bytes scheme consumed by idempotency_key derivation (per-composer outcome-canonical-bytes recipe table at §16.5.5 preserved verbatim).

**Trigger.** First 7b consumption attempt against v1.25 design substrate (PR #37 merge `e6c2f2c` 2026-05-29) surfaced two compounding drifts at §16.5.3 + §16.5.5 vs IS HEAD: (1) **field-set drift** — §16.5.3 declared `EntryPayload` fields as `(action_id, idempotency_key, actor, response_hash)` while IS HEAD at `harness-is/src/harness_is/state_ledger_write.py:62-75` has `(action_id, idempotency_key, actor, timestamp)` with `extra='forbid'`; (2) **`response_hash` semantic drift** — §16.5.5 defined `response_hash` as SHA-256 over composer-specific outcome canonical bytes (post-override step-config etc.) while IS HEAD at `harness-is/src/harness_is/entry_hash.py:73` defines `compute_response_hash(entry) -> Bytes32 = SHA-256(canonicalize(entry))` over the entry's own canonical form per C-IS-06 §6.2. Distinct from Gap C drift v1.25 §16.5.8 already acknowledged (sync/async + `StateLedgerEntry`-vs-`EntryPayload` type at runtime spec §12.3 callable signature). PR #38 filed; operator authorized A) Phase 5 + 6 design phase route + β.i resolution + Q-β.i-1(a) + Q-β.i-3(b) at AskUserQuestion 2026-05-29.

**Decisive structural constraint for β.i.** IS HEAD `EntryPayload` shape is load-bearing for IS-anchored hash-chain invariants at U-IS-08/09/10 + JSONL persistence format at C-IS-07 §7.3 + cross-axis composition at every dependent axis. Changing IS HEAD field-set or `compute_response_hash` semantic ripples to every consumer downstream — same structural constraint that foreclosed (W) at parent fork. β.i is the structural mirror of (S) at parent fork: hold the downstream-axis HEAD verbatim, adapt the CP-side composer surface. ZERO IS-axis cascade. Q5(a) "hash-over-outcome-bytes" ratification preserved at the idempotency_key discriminator surface; the "what HAPPENED" semantic is recorded at the dedup key rather than at the response_hash field.

**v1.25 substantive content preserved verbatim except for the scoped §16.5.3 + §16.5.4 + §16.5.5 + §16.5.8 + §16.5.9 amendments below.** v1.25 §16.5.1 + §16.5.2 + §16.5.6 + §16.5.7 + §16.5.10 + §16.5.11 PRESERVED VERBATIM. §16.5.5 per-composer outcome-canonical-bytes recipe TABLE preserved verbatim per Q-β.i-3(b); only the chapeau prose at §16.5.5 changes. v1.24 + earlier substantive content (NEW §28.10 `ValidatorPostEvaluateHook` Protocol + §5.2 / §8.1 / §8.3 carrier-name harmonization + §1.2 emission-scope cite-correction + v1.7 §13.5.1 CP→OD converter + C-CP-16 §16.2 + C-CP-20 §20.4) preserved verbatim per delta-only-spec-file convention.

**Co-publication this session.** CP plan v2.28 → v2.29 cascade (U-CP-74..79 ACs + signatures re-author against corrected EntryPayload 4-field shape + idempotency-key suffix per Q-β.i-1(a)); CXA v2.16 UNCHANGED (no cross-axis cascade). Closure-back-references owed at nested fork doc + parent fork doc post-merge.

**ZERO breaking change at signed-payload surfaces.** C-CP-16 §16.2 `CPAuditLedgerEntry` 8-field shape preserved verbatim. C-CP-20 §20.4 `CPSignedAuditLedgerEntry` signing contract preserved verbatim. `emit_override_audit_entry` at `per_step_override_evaluator.py:200` preserved verbatim. The §16.5 sibling composers' EntryPayload field-set correction is producer-side; consumer-side IS HEAD shape PRESERVED VERBATIM at `harness-is/src/harness_is/state_ledger_write.py:62-75`.

**ZERO cross-axis cascade.** IS spec UNCHANGED. OD spec UNCHANGED. AS spec UNCHANGED. Runtime spec UNCHANGED (Gap C callable-signature drift at §12.3 remains Class 3 informational per fork doc; deferred to next runtime-spec revision pass). CXA v2.16 UNCHANGED (CP→IS bucket cardinality and 6-PENDING + 2-NOT-APPLICABLE composition unchanged).

---

## §1 — Amended §16.5 sub-sections

The amendments below REPLACE the cited v1.25 sub-section text verbatim. v1.25 sub-sections NOT listed below (§16.5.1 / §16.5.2 / §16.5.6 / §16.5.7 / §16.5.10 / §16.5.11) are PRESERVED VERBATIM at v1.26 by reference.

### §16.5.3 — Canonical EntryPayload composition contract (REPLACES v1.25 §16.5.3)

Each §16.5.2 composer returns `EntryPayload` per C-IS-10 §10.1. `EntryPayload` per IS HEAD shape carries 4 fields `(action_id, idempotency_key, actor, timestamp)` per `harness-is/src/harness_is/state_ledger_write.py:62-75` (`extra='forbid'` rejects any caller that supplies additional fields) — `response_hash` and `prior_event_hash` are IS-computed internally at `append_ledger_entry` per C-IS-06 §6.2 + C-IS-13 §13.5 (Q4 ratification at v1.26: composer supplies EntryPayload's actual 4 fields; IS computes both hash-chain fields internally). The composer-side composition discipline:

**`action_id: str`** — Per-composer-unit canonical kebab-case action identifier (table at v1.25 §16.5.3 PRESERVED VERBATIM):

| Composer | action_id |
|---|---|
| U-CP-14 | `cp.per-step-override-application` |
| U-CP-27 | `cp.workload-binding-class-selection` |
| U-CP-30 | `cp.pause-resume-protocol` |
| U-CP-37 | `cp.hitl-tool-call-rewriting` |
| U-CP-49 | `cp.pause-captured` |
| U-CP-50 | `cp.resume-attempted` |

**`idempotency_key: str`** — SHA-256 hex-64 over the per-composer canonical idempotency-key bytes per §16.5.4. At v1.26: per-composer canonical idempotency-key bytes are the v1.25 per-composer disambiguator (preserved verbatim at §16.5.4) APPENDED with `sha256(outcome_canonical_bytes).hex()` per Q-β.i-1(a) — the outcome-bytes hash carries the "what HAPPENED" semantic at the dedup-key discriminator. Q5(a) ratification preserved at idempotency_key surface.

**`actor: Actor`** — Direct re-use of the composer-input `ActorIdentity` (Q2=direct-reuse pass-through; mirror v1.7 §13.5.1 Q1 `prior_event_hash ≡ prior_entry_hash` semantic-equivalence precedent). Each composer accepts `actor: ActorIdentity` as input and outputs it as `EntryPayload.actor: Actor` field. Type-narrowing if `ActorIdentity ⊆ Actor`; identity preservation otherwise.

**`timestamp: Timestamp`** — Composer-site clock read per Q3(a) ratification at v1.25 §16.5.9 invariant 3: composer fires at canonical post-resolve-pre-return site and reads wall-clock time at emission via `datetime.utcnow()` or equivalent. The `Timestamp` binding at C-IS-05 §5 is `datetime`; monotonic-ordering discipline at C-IS-07 §7.1 acceptance #9 (write-path concern) holds at IS append-site.

`response_hash` and `prior_event_hash` are NOT supplied by the composer. IS computes both internally at `append_ledger_entry`: `response_hash = SHA-256(canonicalize(entry))` per C-IS-06 §6.2 (over the entry's own canonical form, excluding `response_hash` itself); `prior_event_hash` per C-IS-13 §13.5 hash-chain construction. The outcome-bytes semantic at v1.25 §16.5.5 is preserved via idempotency_key derivation per Q-β.i-1(a), NOT via response_hash field (which the IS HEAD does not expose to caller control).

### §16.5.4 — Idempotency-key formulas (REPLACES v1.25 §16.5.4)

Per Q1(b) operator-ratified override-application-specific formula authoring discipline at v1.25: each composer declares an idempotency-key formula scoped to the composer's semantic action surface (NOT reusing C-IS-10 §10.1 step-dispatch formula). Per Q-β.i-1(a) operator-ratified outcome-bytes-relocation discipline at v1.26: each formula APPENDS `|| sha256(outcome_canonical_bytes).hex()` to the v1.25 per-composer disambiguator, preserving the formula chain verbatim and carrying the Q5(a) "hash-over-outcome-bytes" semantic at the dedup-key discriminator. Multiple invocations of the same composer at the same `(workflow_id, step_id)` with the same disambiguator + same outcome MUST produce identical keys (IS-side `IDEMPOTENT_NOOP` on replay); same disambiguator + different outcome → different keys → both records persist (which is correct for state-ledger replay of non-deterministic composers).

| Composer | idempotency_key canonical bytes (v1.26: v1.25 disambiguator `||` outcome-hash suffix) |
|---|---|
| U-CP-14 | `workflow_id \|\| step_id \|\| override_id \|\| policy_id \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-27 | `workflow_id \|\| step_id \|\| engine_class_id \|\| binding_selection_result_canonical_bytes \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-30 | `workflow_id \|\| step_id \|\| pause_resume_protocol_event_kind \|\| event_sequence_id \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-37 | `workflow_id \|\| step_id \|\| tool_call_id \|\| semantic_variant_binding_id \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-49 | `workflow_id \|\| step_id \|\| pause_event_id \|\| snapshot_hash \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-50 | `workflow_id \|\| step_id \|\| resume_event_id \|\| resume_attempt_count \|\| sha256(outcome_canonical_bytes).hex()` |

Canonical-bytes representation: UTF-8 encode each `||`-separated segment; concatenate with single 0x1E (record-separator) byte between segments; SHA-256 hash the result; hex-64 encode. The 0x1E separator forecloses concatenation-ambiguity attacks (canonical-form rule for §16.5 composers established at v1.25 §16.5.4). At v1.26: idempotency-key bytes grow by 65 bytes per row (1 record-separator + 64 hex chars of outcome-hash); the per-composer disambiguator segments preserved verbatim from v1.25; final SHA-256 hash output unchanged at hex-64.

Per-composer disambiguator fields (e.g., `pause_resume_protocol_event_kind`, `tool_call_id`, `snapshot_hash`) MUST be deterministic at composer-call site. Implementation MUST NOT use wall-clock timestamps or random nonces in idempotency-key composition — that would defeat the idempotency semantic at IS hash-chain replay. The outcome-hash suffix is computed at composer-call site over the outcome canonical bytes per §16.5.5 per-composer recipe.

**Per-composer disambiguator notes (v1.25 §16.5.4 PRESERVED VERBATIM):**

- **U-CP-27 `binding_selection_result_canonical_bytes`** — the `WorkloadBindingSelectionResult` (per impl `workload_binding_engine_class_selection.py:71`) canonical JSON bytes; selection rationale + chosen class together form the canonical disambiguator.
- **U-CP-30 `pause_resume_protocol_event_kind`** — `PauseResumeProtocol` class-method invocation discriminator (snapshot capture / resume attempt / classification entry at protocol layer; distinct from engine-layer free functions at U-CP-49/50).
- **U-CP-37 `semantic_variant_binding_id`** — the resolved `HITLSemanticVariantBinding` (per impl `hitl_as_tool_call_rewriting.py:72`) discriminator at `select_variant(...)` outcome consumed by `rewrite_tool_call_to_hitl(...)`.
- **U-CP-49 `snapshot_hash`** — the `PauseSnapshot.snapshot_hash` field per `PauseResumeProtocol` class spec at line 230 (sha256 hex over canonical JSON serialization of `(workflow_id + run_id + step_index + state_summary)`).
- **U-CP-50 `resume_attempt_count`** — discriminates retry attempts at the same `resume_event_id` per `ResumeAttempt` / `ResumeOutcome` model contract (per impl `pause_resume_protocol.py:63,91`).

### §16.5.5 — Outcome-bytes recipes consumed by idempotency_key derivation (REPLACES v1.25 §16.5.5 chapeau; per-composer outcome-canonical-bytes recipe TABLE preserved verbatim)

Per Q5(a) operator-ratified hash-over-outcome-bytes discipline at v1.25 + Q-β.i-3(b) operator-ratified reframe at v1.26: each composer records the OUTCOME canonical bytes (post-action state mutation), NOT the INPUT canonical bytes (pre-action intent). At v1.26 the outcome-canonical-bytes scheme below is consumed by **idempotency_key derivation per §16.5.4** (appended as `|| sha256(outcome_canonical_bytes).hex()` segment) per Q-β.i-1(a), NOT by `response_hash` field (which is IS-internal per C-IS-06 §6.2 — composer does not control it). The "what HAPPENED" semantic is preserved at the idempotency_key discriminator rather than at response_hash; Q5(a) ratification honored.

| Composer | outcome canonical bytes recipe |
|---|---|
| U-CP-14 | post-override step-config canonical JSON bytes (the effective step config after override application) |
| U-CP-27 | `WorkloadBindingSelectionResult` canonical JSON bytes (resolved class binding + rationale) |
| U-CP-30 | protocol-state-transition outcome canonical JSON bytes (the protocol state snapshot after the class-level event) |
| U-CP-37 | `RewrittenToolCall` canonical JSON bytes (the rewritten tool-call payload at impl line 109) |
| U-CP-49 | `PauseSnapshot` canonical JSON bytes (the persisted state at pause capture per impl line 46) |
| U-CP-50 | `ResumeOutcome` canonical JSON bytes (per impl line 91 — `ResumeOutcomeKind` + resumed state) |

Canonical JSON bytes per the JSON-canonicalization scheme established at v1.7 §13.5.1 for `cp_audit_to_od_audit` converter: sorted keys, `(",", ":")` separators, UTF-8 encode, NaN/Infinity rejection per ECMA-404.

Implementation note (NOT spec): composers SHOULD compute the outcome canonical bytes via a shared `_canonicalize_outcome_bytes(payload: BaseModel | Mapping) → bytes` helper at `harness-cp/src/harness_cp/state_ledger_canonicalization.py` to ensure cross-composer canonical-form consistency. Helper home and naming are implementation-discretion per `harness-cp/CLAUDE.md` §5.1. Helper role preserved at v1.26 — the bytes it produces are consumed by idempotency_key derivation per §16.5.4 rather than by response_hash field; the helper signature + behavior are unchanged.

### §16.5.8 — Runtime wiring discipline (Q4 attribution clause REPLACED; surrounding prose preserved verbatim from v1.25)

The Q4 ratification language at v1.25 §16.5.8 is REPLACED at v1.26 as follows:

Per Q4 ratification at v1.26: the §16.5 composer contract authored here matches the IS HEAD callable shape (`EntryPayload` → `WriteResult`) and the IS HEAD `EntryPayload` 4-field shape `(action_id, idempotency_key, actor, timestamp)`; composer supplies EntryPayload's actual 4 fields; IS computes `response_hash` (via `compute_response_hash = SHA-256(canonicalize(entry))` per C-IS-06 §6.2) AND `prior_event_hash` (per C-IS-13 §13.5 hash-chain construction) internally. Runtime spec amendment to align §12.3 prose with IS HEAD callable shape + IS HEAD EntryPayload field set is deferred to next runtime-spec revision pass per `[[spec-prose-plan-body-drift-pattern]]`.

Surrounding §16.5.8 prose (runtime wiring binding home, Gap C deferral acknowledgment) PRESERVED VERBATIM from v1.25.

### §16.5.9 — Invariants (invariant 2 REPLACED; invariants 1, 3, 4, 5, 6, 7 preserved verbatim from v1.25)

Invariant 2 at v1.25 §16.5.9 is REPLACED at v1.26 as follows:

2. **Composer-side composition; IS-side hash-chain fields.** Composers supply `EntryPayload` 4-field shape `(action_id, idempotency_key, actor, timestamp)`; IS computes `response_hash` (via `compute_response_hash = SHA-256(canonicalize(entry))` per C-IS-06 §6.2 — over the entry's own canonical form, excluding `response_hash` itself) AND `prior_event_hash` (SHA-256 over prior canonical entry on IS-anchored chain per C-IS-13 §13.5) internally. The outcome-bytes semantic at §16.5.5 is consumed by idempotency_key derivation per §16.5.4 (appended segment per Q-β.i-1(a)), NOT by response_hash (which IS-internal per C-IS-06 §6.2).

Invariants 1, 3, 4, 5, 6, 7 at v1.25 §16.5.9 PRESERVED VERBATIM.

---

## §2 — Adjacent observations

- **(a)** Gap C drift at runtime spec §12.3 (`Callable[[StateLedgerEntry], EntryHash]` vs IS HEAD `Callable[[EntryPayload], WriteResult]`) remains Class 3 informational per parent fork doc; NOT patched at v1.26 per FM-2 no-extension discipline. Runtime spec prose alignment for §12.3 callable shape + EntryPayload field-set + sync/async deferred to next runtime-spec revision pass. The β.i resolution at v1.26 matches IS HEAD callable shape + IS HEAD EntryPayload field set; closes the EntryPayload-field-set portion of the spec-prose-vs-impl drift at the CP spec but not at the runtime spec.

- **(b)** `[[impl-time-grounding-pass-pre-merge-revision]]` workspace pattern SHARPENED at v1.26 filing: the v1.25 grounding pass caught module/symbol existence (2 architectural reclassifications + 3 function-name mismatches) but did NOT verify type-definition field-sets of externally-consumed types. Pattern update: when design substrate enumerates per-field semantics for an externally-defined type, the grounding MUST verify the type's actual field set against the substrate's claimed field set. This is a strict superset of the v1.25 grounding shape; future spec revisions citing IS HEAD or AS HEAD types should include field-set diff verification.

- **(c)** β.i resolution preserves the parent fork (S) sibling-variant architectural commitment at the structural level: hold the downstream-axis HEAD verbatim, adapt the producer-side composer surface. ZERO IS-axis cascade at v1.26 matches the (S) precedent's ZERO CP-audit-axis cascade at v1.25.

- **(d)** Q-β.i-2 sub-question from nested fork doc (outcome-canonical-bytes scheme at composer site) ratified by absorption at v1.26: the shared `_canonicalize_outcome_bytes(payload) → bytes` helper at U-CP-74 module `state_ledger_canonicalization.py` retains its role unchanged from CP plan v2.28 §2; helper signature + behavior unchanged. Helper home + naming follow implementation-discretion per `harness-cp/CLAUDE.md` §5.1.

- **(e)** CP plan v2.28 → v2.29 cascade owed per change-note: U-CP-74..79 ACs + signatures at plan v2.28 §2 reference v1.25 §16.5.3 field set and §16.5.5 response_hash semantic; plan v2.29 must absorb the β.i correction at AC #2 (idempotency_key now includes outcome-hash suffix) + AC #3 (drop "response_hash over outcome bytes"; outcome-hash semantic at idempotency_key suffix instead) per U-CP-74 row + cascade analogous corrections at U-CP-75..79. Plan-side cascade is `implementation-planner` revision-pass work, NOT spec-writer work per FM-2 + this file's §"Sections preserved verbatim" discipline.

---

## §3 — Status

Surgical amendment at v1.25 NEW §16.5 sub-section absorbing operator-ratified β.i resolution + Q-β.i-1(a) + Q-β.i-3(b) at AskUserQuestion 2026-05-29. Apply pass: this arc (delta-only spec file co-published with PR #38 routing-doc + nested fork doc). v1.25 §16.5.1 / §16.5.2 / §16.5.6 / §16.5.7 / §16.5.10 / §16.5.11 + v1.24 + earlier PRESERVED VERBATIM per delta-only-spec-file convention.

CP plan v2.28 → v2.29 revision-pass (separate arc; `implementation-planner` skill) blocks on this spec being filed. CXA v2.16 UNCHANGED. Closure-back-references at nested fork doc + parent fork doc owed post-merge.

2026-05-29.
