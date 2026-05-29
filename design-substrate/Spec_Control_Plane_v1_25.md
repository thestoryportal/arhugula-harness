# Spec: Control Plane — v1.25 (delta over v1.24)

---

## Change-note (v1.24 → v1.25)

**Scope of revision.** Substantive amendment authoring NEW §16.5 sub-section under C-CP-16 absorbing the CP→IS state-ledger emission contract for **6 CP source units** (U-CP-14 sibling-variant addition + 5 greenfield composers at U-CP-27 / U-CP-30 / U-CP-37 / U-CP-49 / U-CP-50). Resolves U-RT-35 Gap B (within-Path-A) per `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` operator-ratified 2026-05-28 Q-set: (W/S)=S sibling-variant; Q1=Q1(b) override-specific idempotency formula; Q2=direct-reuse actor pass-through; Q3=Q3(a) composer-site clock; Q4=Q4(b) composer-supplies-EntryPayload + IS-computes-prior_event_hash; Q5=Q5(a) hash-over-outcome-bytes; Q6=Q6(a) `emit_override_state_ledger_entry` naming.

**Two CP source units reclassified as NOT-APPLICABLE at v1.25 §16.5.X per impl-time grounding pass:**

- **U-CP-12 `per_class_attribute_composition.py`** — module is purely DECLARATIVE (static `PER_CLASS_ATTRIBUTE_SETS` tuple per C-CP-05 §5.2 + helper `required_attributes_for(...)`). NO runtime composer-action moment where state-ledger emission would fire. Consumers (`multi_agent_span_hierarchy.py` + tests) import the typed `SamplingRate` enum only. There is no "compose_per_class_attributes(...)" function as the v1.25-draft §16.5.7 firing-site discipline assumed; the spec's draft assumption did not ground against the canonical module shape. Reclassified at §16.5.10 as declarative-only; runtime spec §12.3 17-edge canonical enumeration carries U-CP-12 as not-applicable-at-CP-side (Class 3 informational drift documented at §16.5.10 — runtime spec §12.3 revision pass deferred).
- **U-CP-52 `hitl_placement.py`** — module exports the canonical §17.4 `hitl_gate(...)` SIGNATURE-ONLY surface that raises `NotImplementedError` (per spec v1.10 §17.4 canonical signature materialization). Production gate-body composition lives at runtime-side `RuntimeHITLGateComposer` per `Spec_Harness_Runtime_v1.md` v1.13 §14.8. CP-side `hitl_placement.py` has NO production-reachable runtime action where state-ledger emission would fire — the architecture explicitly routes gate composition through the runtime-axis. Reclassified at §16.5.10 as runtime-axis-emission-concern; CP-side signature-only; state-ledger emission for HITL gate outcomes is a future runtime-plan revision concern (deferred).

**Trigger.** U-RT-35 PARTIAL-LAND (1 of 17 spec §12.3 CP→IS edges wired at HEAD) Class 1 fork `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` RE-OPENED 2026-05-28 per harness deployment-readiness audit identifying this as the sole remaining deployment-blocker. Path A (full Phase 6 back-flow) authorized at AskUserQuestion. Within Path A, Gap B presents two structural patterns for U-CP-14 shape divergence + greenfield composers: (W) widen `CPAuditLedgerEntry` C-CP-16 §16.2 8-field shape; (S) preserve §16.2 verbatim + author sibling typed variant. Operator ratified (S).

**Decisive structural constraint for (S).** CPAuditLedgerEntry already carries a signing contract at C-CP-20 §20.4 → `CPSignedAuditLedgerEntry` signs over the 8-field shape. CP spec v1.7 §13.5.1 NOTE 3 ("Cryptographic-payload-mismatch foreclosure") canonicalizes hash-bytes-immutability at signed-payload surfaces — workspace has paid this price once at CP→OD seam. Widening §16.2 would change CP-signed bytes, breaking C-CP-20 §20.4 signing contract or defeating the widening. (S) preserves §16.2 + §20.4 verbatim → C-CP-20 signing contract unchanged → CP→OD converter at v1.7 §13.5.1 unchanged → CP-AL-2 typed taxonomy boundary respected per `harness-cp/CLAUDE.md` §4.2.

**Workspace `CLAUDE.md` §4.4 X-AL-3 compliance.** H_T design extension at Phase 7 execution-time → Class 1 fork required → filed at `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` → operator-ratified at AskUserQuestion 2026-05-28 → apply pass at this v1.25 amendment. The 2 not-applicable reclassifications at §16.5.10 are impl-time-grounded carve-outs against the canonical §12.3 17-edge enumeration; they do NOT constitute silent design extension because the architectural decision (declarative-only vs runtime-composer routing) is canonical at C-CP-05 §5.2 + C-RT-18 §14.8 verbatim.

**v1.24 substantive content preserved verbatim.** All v1.24 content (NEW §28.10 `ValidatorPostEvaluateHook` Protocol absorbing U-OD-40 cost-attribution per Reading B) preserved unchanged. All v1.23 + earlier substantive content (§5.2 / §8.1 / §8.3 carrier-name harmonization + §1.2 emission-scope cite-correction + v1.7 §13.5.1 CP→OD converter + C-CP-16 §16.2 + C-CP-20 §20.4) preserved verbatim. The §16 body at v1.10 preserved verbatim — additive at NEW §16.5 sub-section; ZERO change to §16.1 through §16.4.

**Co-publication this session.** CP plan v2.27 → v2.28 revision-pass (6 NEW composer atomic units U-CP-74..79; ~6-12 tests per unit — separate authoring arc blocking on this spec); CXA v2.15 → v2.16 §0.4 forward-tracking marker for §2.3.2 CP→IS bucket (6 pending events per refresh; separate arc).

**ZERO breaking change at signed-payload surfaces.** C-CP-16 §16.2 `CPAuditLedgerEntry` 8-field shape preserved verbatim. C-CP-20 §20.4 `CPSignedAuditLedgerEntry` signing contract preserved verbatim. `emit_override_audit_entry` at `per_step_override_evaluator.py:200` (existing) preserved verbatim — the NEW sibling `emit_override_state_ledger_entry` is additive; U-CP-14 emits BOTH records per override-application post-revision.

**ZERO cross-axis cascade beyond CXA tracking-marker.** OD spec UNCHANGED. AS spec UNCHANGED. IS spec UNCHANGED at the canonical `StateLedgerEntry` / `EntryPayload` / `WriteResult` shapes per C-IS-10 §10.1 + C-IS-13 §13.5. Runtime spec UNCHANGED in this revision (Gap C callable-signature drift at §12.3 remains Class 3 informational per fork doc; deferred to next runtime-spec revision pass).

---

## §1 — NEW §16.5 — CP→IS state-ledger emission contract

### §16.5.1 — Scope and authority

C-CP-16 §16.2 declares the CP per-response audit-ledger entry shape `CPAuditLedgerEntry` (8 fields, response-conditional optional hash fields per the 4-row table) — the CP-internal audit record signed at C-CP-20 §20.4 and converted to OD-shape audit entries at v1.7 §13.5.1. The §16.5 contract authored here is a SIBLING role: CP→IS state-ledger emission for hash-chain participation at C-IS-10 §10.1 / C-IS-13 §13.5.

The two ledgers are structurally and semantically distinct per the spec:

- **C-CP-16 §16.2 CPAuditLedgerEntry** — CP per-response audit record, CP-internal chain (`prior_event_hash` chains the CP-audit sequence), CP-signed at C-CP-20 §20.4, response-conditional optional hash fields per 4-row table.
- **C-IS-10 §10.1 StateLedgerEntry / EntryPayload** — IS-anchored hash-chain state record (`prior_event_hash` chains the IS-anchored canonical sequence per C-IS-13 §13.5), IS-computed hash-chain fields, fixed 6-field shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)`.

They share field NAMES at `prior_event_hash` but not field SEMANTICS (CP-audit chain vs IS-anchored canonical chain). Widening §16.2 to satisfy IS-anchored hash-chain participation would collapse this distinction silently; the sibling-variant contract authored here preserves it via typed CP-side composers producing the IS-canonical shape directly at the CP→IS seam.

### §16.5.2 — Composer surface enumeration

Six CP-side composer functions emit `EntryPayload` per C-IS-10 §10.1 for IS-anchored hash-chain participation. Runtime callable wiring at `Spec_Harness_Runtime_v1.md` §12.3 binds each composer's output to `ctx.ledger_writer.append_ledger_entry(payload)` returning `WriteResult` per IS HEAD contract:

| CP source unit | Composer function | Module + firing-site grounding |
|---|---|---|
| U-CP-14 | `emit_override_state_ledger_entry` (sibling to existing `emit_override_audit_entry`) | `per_step_override_evaluator.py` — existing `emit_override_audit_entry(...)` at line 200 invoked from `resolve_step_binding(...)` at line 179 |
| U-CP-27 | `emit_workload_class_selection_state_ledger_entry` | `workload_binding_engine_class_selection.py` — fire after `select_engine_class(...)` at line 142 resolves the binding |
| U-CP-30 | `emit_pause_resume_state_ledger_entry` | `pause_resume_protocol.py` — fire from `PauseResumeProtocol` class methods (workflow-layer per CP spec v1.11 §26 NEW NOTE coexistence; distinct from engine-layer free functions at U-CP-49/50) |
| U-CP-37 | `emit_hitl_tool_call_rewriting_state_ledger_entry` | `hitl_as_tool_call_rewriting.py` — fire after `rewrite_tool_call_to_hitl(...)` at line 149 produces the rewritten payload |
| U-CP-49 | `emit_pause_captured_state_ledger_entry` | `pause_resume_protocol.py` — fire after engine-layer free function `capture_pause_snapshot(...)` at line 106 returns the snapshot |
| U-CP-50 | `emit_resume_attempted_state_ledger_entry` | `pause_resume_protocol.py` — fire after engine-layer free function `attempt_resume(...)` at line 128 resolves the resume outcome |

Combined with the LANDED U-CP-34 `emit_sibling_ledger_entry` at runtime spec §12.3 row 1, the §16.5 contract covers 7 of 17 §12.3 source-edges at this revision. The remaining edge-cardinality differential vs §12.3 (17 declared) is documented at §16.5.10 — U-CP-12 + U-CP-52 are NOT-APPLICABLE at CP-side (declarative-only / runtime-composed respectively); runtime spec §12.3 prose revision to align canonical-enumeration with materialized surfaces is deferred to next runtime-spec revision pass per Gap C discipline.

### §16.5.3 — Canonical EntryPayload composition contract

Each §16.5.2 composer returns `EntryPayload` per C-IS-10 §10.1 with the following field-composition discipline. `EntryPayload` per IS HEAD shape carries 4 fields `(action_id, idempotency_key, actor, response_hash)` — `timestamp` and `prior_event_hash` are IS-computed internally at `append_ledger_entry` per C-IS-13 §13.5 (Q4 ratification: composer supplies EntryPayload; IS computes the hash-chain fields). The composer-side composition discipline:

**`action_id: str`** — Per-composer-unit canonical kebab-case action identifier:

| Composer | action_id |
|---|---|
| U-CP-14 | `cp.per-step-override-application` |
| U-CP-27 | `cp.workload-binding-class-selection` |
| U-CP-30 | `cp.pause-resume-protocol` |
| U-CP-37 | `cp.hitl-tool-call-rewriting` |
| U-CP-49 | `cp.pause-captured` |
| U-CP-50 | `cp.resume-attempted` |

**`idempotency_key: str`** — SHA-256 hex-64 over the per-composer canonical idempotency-key bytes per §16.5.4 (Q1=Q1(b) override-specific formula for U-CP-14; analogous per-surface formulas for the 5 greenfield composers).

**`actor: Actor`** — Direct re-use of the composer-input `ActorIdentity` (Q2=direct-reuse pass-through; mirror v1.7 §13.5.1 Q1 `prior_event_hash ≡ prior_entry_hash` semantic-equivalence precedent). Each composer accepts `actor: ActorIdentity` as input and outputs it as `EntryPayload.actor: Actor` field. Type-narrowing if `ActorIdentity ⊆ Actor`; identity preservation otherwise.

**`response_hash: str`** — SHA-256 hex-64 over the composer-specific OUTCOME canonical bytes per §16.5.5 (Q5=Q5(a) hash-over-outcome-bytes). Each composer records what HAPPENED (post-action canonical state bytes), not what was INTENDED (input bytes). Composer-specific canonical-bytes recipes per §16.5.5.

`timestamp` and `prior_event_hash` are NOT supplied by the composer. IS computes both internally at `append_ledger_entry` per C-IS-13 §13.5 (timestamp: clock-read at append-site; prior_event_hash: SHA-256 over prior canonical entry on the IS-anchored chain).

### §16.5.4 — Idempotency-key formulas (Q1(b) ratification)

Per Q1(b) operator-ratified override-application-specific formula authoring discipline: each composer declares an idempotency-key formula scoped to the composer's semantic action surface (NOT reusing C-IS-10 §10.1 step-dispatch formula). Multiple invocations of the same composer at the same `(workflow_id, step_id)` MUST produce distinct keys; collision risk under step-dispatch-formula reuse is real.

| Composer | idempotency_key canonical bytes |
|---|---|
| U-CP-14 | `workflow_id \|\| step_id \|\| override_id \|\| policy_id` |
| U-CP-27 | `workflow_id \|\| step_id \|\| engine_class_id \|\| binding_selection_result_canonical_bytes` |
| U-CP-30 | `workflow_id \|\| step_id \|\| pause_resume_protocol_event_kind \|\| event_sequence_id` |
| U-CP-37 | `workflow_id \|\| step_id \|\| tool_call_id \|\| semantic_variant_binding_id` |
| U-CP-49 | `workflow_id \|\| step_id \|\| pause_event_id \|\| snapshot_hash` |
| U-CP-50 | `workflow_id \|\| step_id \|\| resume_event_id \|\| resume_attempt_count` |

Canonical-bytes representation: UTF-8 encode each `||`-separated segment; concatenate with single 0x1E (record-separator) byte between segments; SHA-256 hash the result; hex-64 encode. The 0x1E separator forecloses concatenation-ambiguity attacks (canonical-form rule for §16.5 composers established at this spec amendment).

Per-composer disambiguator fields (e.g., `pause_resume_protocol_event_kind`, `tool_call_id`, `snapshot_hash`) MUST be deterministic at composer-call site. Implementation MUST NOT use wall-clock timestamps or random nonces in idempotency-key composition — that would defeat the idempotency semantic at IS hash-chain replay.

**Per-composer disambiguator notes:**

- **U-CP-27 `binding_selection_result_canonical_bytes`** — the `WorkloadBindingSelectionResult` (per impl `workload_binding_engine_class_selection.py:71`) canonical JSON bytes; selection rationale + chosen class together form the canonical disambiguator.
- **U-CP-30 `pause_resume_protocol_event_kind`** — `PauseResumeProtocol` class-method invocation discriminator (snapshot capture / resume attempt / classification entry at protocol layer; distinct from engine-layer free functions at U-CP-49/50).
- **U-CP-37 `semantic_variant_binding_id`** — the resolved `HITLSemanticVariantBinding` (per impl `hitl_as_tool_call_rewriting.py:72`) discriminator at `select_variant(...)` outcome consumed by `rewrite_tool_call_to_hitl(...)`.
- **U-CP-49 `snapshot_hash`** — the `PauseSnapshot.snapshot_hash` field per `PauseResumeProtocol` class spec at line 230 (sha256 hex over canonical JSON serialization of `(workflow_id + run_id + step_index + state_summary)`).
- **U-CP-50 `resume_attempt_count`** — discriminates retry attempts at the same `resume_event_id` per `ResumeAttempt` / `ResumeOutcome` model contract (per impl `pause_resume_protocol.py:63,91`).

### §16.5.5 — Response-hash recipes (Q5(a) ratification: outcome bytes)

Per Q5(a) operator-ratified hash-over-outcome-bytes discipline: each composer records the OUTCOME canonical bytes (post-action state mutation), NOT the INPUT canonical bytes (pre-action intent). This produces a state-ledger record of what happened, suitable for IS hash-chain participation at audit replay.

| Composer | response_hash canonical bytes (outcome) |
|---|---|
| U-CP-14 | post-override step-config canonical JSON bytes (the effective step config after override application) |
| U-CP-27 | `WorkloadBindingSelectionResult` canonical JSON bytes (resolved class binding + rationale) |
| U-CP-30 | protocol-state-transition outcome canonical JSON bytes (the protocol state snapshot after the class-level event) |
| U-CP-37 | `RewrittenToolCall` canonical JSON bytes (the rewritten tool-call payload at impl line 109) |
| U-CP-49 | `PauseSnapshot` canonical JSON bytes (the persisted state at pause capture per impl line 46) |
| U-CP-50 | `ResumeOutcome` canonical JSON bytes (per impl line 91 — `ResumeOutcomeKind` + resumed state) |

Canonical JSON bytes per the JSON-canonicalization scheme established at v1.7 §13.5.1 for `cp_audit_to_od_audit` converter: sorted keys, `(",", ":")` separators, UTF-8 encode, NaN/Infinity rejection per ECMA-404.

Implementation note (NOT spec): composers SHOULD compute the canonical bytes via a shared `_canonicalize_outcome_bytes(payload: BaseModel | Mapping) → bytes` helper at `harness-cp/src/harness_cp/state_ledger_canonicalization.py` to ensure cross-composer canonical-form consistency. Helper home and naming are implementation-discretion per `harness-cp/CLAUDE.md` §5.1.

### §16.5.6 — U-CP-14 dual-emission discipline

U-CP-14 `per_step_override_evaluator` is the sole composer with a pre-existing CP-audit role (`emit_override_audit_entry` returning `CPAuditLedgerEntry` per C-CP-14 + C-CP-16 §16.2, declared at `per_step_override_evaluator.py:200` and invoked from `resolve_step_binding(...)` at line 179). At v1.25, U-CP-14 emits BOTH records per override-application:

1. **Existing `emit_override_audit_entry`** — returns `CPAuditLedgerEntry` per C-CP-16 §16.2 8-field shape, preserved VERBATIM. Feeds C-CP-20 §20.4 signing contract + v1.7 §13.5.1 CP→OD converter. CP-internal audit chain participation unchanged.
2. **NEW `emit_override_state_ledger_entry`** — returns `EntryPayload` per §16.5.3 composition discipline. Feeds runtime spec §12.3 CP→IS edge wiring. IS-anchored hash-chain participation NEW at v1.25.

The two emission sites are ORTHOGONAL: distinct return types, distinct downstream consumers, distinct chain semantics. NO de-duplication owed; the records serve distinct roles. Composer-site discipline: invoke BOTH at every override-application site within the existing `emit_override_audit_entry` firing scope at `resolve_step_binding:179`. NEW emission site does NOT mutate or replace the existing CP-audit emission; additive only.

Cost of dual emission: 2 writes per override-application instead of 1. Acceptable per workspace discipline — the records serve distinct canonical roles per the two-typed-ledger architecture at §16.5.1. Acceptable performance budget: each write is bounded I/O (SQLite append + hash compute) at write-only sites with no read-back during dispatch.

### §16.5.7 — Greenfield composer firing-site discipline (5 composers)

The 5 greenfield composers (U-CP-27 / U-CP-30 / U-CP-37 / U-CP-49 / U-CP-50) have NO pre-existing CP-audit role. They MUST NOT emit `CPAuditLedgerEntry`; they emit ONLY `EntryPayload` per §16.5.3 at the canonical firing site within each composer's owning module.

Firing-site discipline per composer (grounded against impl HEAD at `harness-cp/src/harness_cp/`):

- **U-CP-27** `workload_binding_engine_class_selection.py` — fire AFTER `select_engine_class(...)` at line 142 resolves the binding (returns `WorkloadBindingSelectionResult` per line 71); BEFORE returning the result to caller.
- **U-CP-30** `pause_resume_protocol.py` (workflow-layer class) — fire from `PauseResumeProtocol` class methods at line 214+ (workflow-layer per CP spec v1.11 §26 NEW NOTE coexistence). The protocol-layer firing site is distinct from the engine-layer free functions (`capture_pause_snapshot` / `attempt_resume` / `classify_resume`) and emits at workflow-layer protocol transitions per the canonical 2-layer split.
- **U-CP-37** `hitl_as_tool_call_rewriting.py` — fire AFTER `rewrite_tool_call_to_hitl(...)` at line 149 produces the `RewrittenToolCall` (per line 109); BEFORE returning the rewritten call.
- **U-CP-49** `pause_resume_protocol.py` (engine-layer free function) — fire AFTER `capture_pause_snapshot(...)` at line 106 returns the `PauseSnapshot` per line 46; BEFORE returning the snapshot. Engine-layer per CP spec v1.11 §26 NEW NOTE; distinct from U-CP-30 workflow-layer firing site.
- **U-CP-50** `pause_resume_protocol.py` (engine-layer free function) — fire AFTER `attempt_resume(...)` at line 128 resolves the `ResumeOutcome` per line 91 (success OR failure); BEFORE returning the outcome. Engine-layer; distinct from U-CP-30 workflow-layer firing site.

Each composer accepts `ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]` as a kw-only parameter at the composer function signature (mirror U-CP-34 `sibling_ledger_entry_composition` pattern at runtime spec §12.3 row 1 LANDED at U-RT-35 AC #1). Composer module exports the composer function for runtime wiring at runtime-plan binding stage.

ZERO change to existing module logic at the resolve-the-action portion. The composer's pre-v1.25 contract (compute the action; return the result) is unchanged; the §16.5 amendment adds state-ledger emission as a side-effect at the canonical post-resolve-pre-return firing site.

### §16.5.8 — Runtime wiring discipline (spec §12.3 binding)

Each §16.5.2 composer's `ledger_writer` kw-only parameter is bound at runtime composition time per `Spec_Harness_Runtime_v1.md` §12.3 to `ctx.ledger_writer.append_ledger_entry` (the IS-axis HEAD callable). Binding home: composer-specific factory function in `harness-runtime/src/harness_runtime/lifecycle/` per per-composer materialize-stage helper.

Runtime wiring IS NOT in scope at this CP spec amendment. The CP spec authors the producer-side composer contract; the consumer-side binding contract lives at runtime spec §12.3. The runtime plan v2.28+ revision authors the binding stages per the wiring discipline declared here.

Gap C drift at runtime spec §12.3 (`Callable[[StateLedgerEntry], EntryHash]` vs IS HEAD `Callable[[EntryPayload], WriteResult]`) remains Class 3 informational per `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` §"Gap class C". Per Q4 ratification, the §16.5 composer contract authored here matches the IS HEAD callable shape (`EntryPayload` → `WriteResult`); runtime spec amendment to align §12.3 prose is deferred to next runtime-spec revision pass per `[[spec-prose-plan-body-drift-pattern]]`.

### §16.5.9 — Invariants

1. **Sibling role (S) — no widening of C-CP-16 §16.2.** `CPAuditLedgerEntry` 8-field shape preserved verbatim. C-CP-20 §20.4 signing contract preserved verbatim. v1.7 §13.5.1 CP→OD converter unchanged. §16.5 composers produce `EntryPayload`, not widened `CPAuditLedgerEntry`.
2. **Composer-side composition; IS-side hash-chain fields.** Composers supply `EntryPayload` 4-field shape; IS computes `timestamp` (clock-read at append) and `prior_event_hash` (SHA-256 over prior canonical entry on IS-anchored chain per C-IS-13 §13.5) internally.
3. **Composer-site clock posture for action timing.** Q3(a) — composer fires at canonical post-resolve-pre-return site; the IS-side append timestamp records the persistence-site clock. If a composer needs to record action-site clock distinct from append-site clock, that's an out-of-scope future revision (none of the 6 §16.5.2 composers require this distinction at v1.25).
4. **Idempotent on replay.** Idempotency-key formulas per §16.5.4 are deterministic at composer-call site. IS append at duplicate idempotency_key MUST return `WriteResult.IDEMPOTENT_NOOP` per IS HEAD contract; composers MUST NOT condition on this return value (the composer's contract terminates at `append_ledger_entry` invocation).
5. **ZERO CP-audit emission at 5 greenfield composers.** The 5 greenfield composers MUST NOT emit `CPAuditLedgerEntry`; their canonical role is IS state-ledger emission only. Future revision authoring CP-audit role at any of the 5 is a separate spec amendment arc.
6. **U-CP-14 dual emission is order-independent.** U-CP-14 firing site invokes BOTH `emit_override_audit_entry` AND `emit_override_state_ledger_entry`. Order of invocation is implementation-discretion — both emissions complete before override-application returns; neither depends on the other's return value.
7. **ZERO cross-axis cascade at OD-axis.** OD spec, OD plan, OD test surfaces UNCHANGED. CP-audit role + CP→OD converter at v1.7 §13.5.1 unchanged. State-ledger emission is intra-IS-axis; no OD-axis observability seam owed.

### §16.5.10 — Not-applicable-at-CP-side surfaces (impl-time-grounded reclassification)

Two CP source units listed at runtime spec §12.3 canonical 17-edge enumeration are reclassified at v1.25 as NOT-APPLICABLE for CP-side state-ledger emission per impl-time grounding pass:

**U-CP-12 `per_class_attribute_composition.py` — DECLARATIVE-ONLY.** Module exports static `PER_CLASS_ATTRIBUTE_SETS` tuple per C-CP-05 §5.2 (8 entries, one per `WorkflowEventClass`) + helper `required_attributes_for(...)` query. There is NO runtime composer-action moment where state-ledger emission would fire — the canonical per-class attribute set is determined at module-import time per the §5.2 declaration; no resolve-the-action step exists at runtime. Consumers (`multi_agent_span_hierarchy.py` + tests) read the `SamplingRate` enum + table; no consumer site produces a "per-class attribute composition event" worth state-ledger emission. State-ledger participation at this surface is structurally absent; ZERO composer authored.

**U-CP-52 `hitl_placement.py` — RUNTIME-AXIS-COMPOSED.** Module exports canonical §17.4 `hitl_gate(...)` signature surface at line 205; production callers MUST go through runtime-side `RuntimeHITLGateComposer` per `Spec_Harness_Runtime_v1.md` v1.13 §14.8 (the CP-side signature raises `NotImplementedError` for non-bootstrap callers). State-ledger emission for HITL gate outcomes is architecturally a runtime-axis concern — the runtime composer holds the `HITLGateResult` per line 181 + the surrounding workflow context. Future runtime-plan revision authoring `emit_hitl_gate_state_ledger_entry` at the runtime composer site is the canonical path; CP-side `hitl_placement.py` has no production-reachable runtime action where emission would fire.

Per the not-applicable reclassifications: runtime spec §12.3 canonical 17-edge enumeration carries U-CP-12 + U-CP-52 as declared-but-not-CP-materializable; the §12.3 prose revision aligning the canonical-enumeration with materialized surfaces is deferred to next runtime-spec revision pass per Gap C discipline. The effective CP-side materializable edge count at full §16.5.2 landing is 7 (1 U-CP-34 LANDED + 6 NEW v1.25 composers); the 17-vs-7 differential is documented as canonical-vs-materialized at runtime spec §12.3 (not as a spec defect — the §12.3 17-edge enumeration is forward-looking per spec authoring discipline; impl-time grounding at v1.25 surfaces the architectural carve-outs).

### §16.5.11 — Status posture

NEW §16.5 sub-section at v1.25 (6 composer contracts authoring CP→IS state-ledger emission per (S) sibling-variant ratification; 2 not-applicable reclassifications per impl-time grounding). Apply pass: this arc (delta-only spec file co-published with architect recommendation doc `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` + parent fork doc RE-OPEN annotation). v1.24 + earlier PRESERVED VERBATIM per delta-only-spec-file convention.

CP plan v2.27 → v2.28 revision-pass (separate arc; 6 NEW atomic units U-CP-74..79) blocks on this spec being filed. CXA v2.15 → v2.16 §0.4 tracking-marker (separate arc) reflects 6 pending events.

---

## §2 — Adjacent observations

- **(a)** Gap C drift at runtime spec §12.3 (`Callable[[StateLedgerEntry], EntryHash]` vs IS HEAD `Callable[[EntryPayload], WriteResult]`) NOT patched at this arc per FM-3 (informational Class 3 per fork doc). The §16.5 composer contract authored here matches the IS HEAD callable shape; runtime spec prose alignment deferred. Co-deferred: §12.3 17-vs-7 canonical-vs-materialized differential per §16.5.10 reclassifications.

- **(b)** CXA-4 PARTIAL → RETIRE-READY transit gated on §16.5 composer landings + spec §12.3 canonical-vs-materialized differential resolution per `[[close-phase-complete-pre-design-batches-42-44]]` batch-42 §1.2. Separate routing; not blocking on this spec arc.

- **(c)** IS-2 canonical-reading amendment per advisor batch-39 path (β) is a parallel design-phase arc; not blocking on this spec arc. The §16.5 composer contract is INDEPENDENT of the C-IS-02 §"Tier composition contract" line 170 canonical-reading ambiguity (which scopes `procedural`-tier reference enforcement at the state-ledger writer; the §16.5 composers produce EntryPayload at the producer side, orthogonal to the writer-side enforcement gate).

- **(d)** Canonical-bytes helper home `harness-cp/src/harness_cp/state_ledger_canonicalization.py` is implementation-discretion per §16.5.5 implementation note. Helper home + naming follow workspace `harness-cp/CLAUDE.md` §5.1 if a canonical-form rule emerges. NOT patched at this spec arc.

- **(e)** Multi-tenant compliance posture: each §16.5.4 idempotency-key formula scopes the key by `workflow_id` (which carries tenant-id binding per CP spec v1.22 tenant-id binding lift `[[tenant-id-binding-lift-cp-v1-22]]`); cross-tenant idempotency-key collision is structurally foreclosed at the `workflow_id` prefix. NO additional multi-tenant amendment owed at this arc.

- **(f)** `SyncDispatcherFacade` + `SyncValidatorFrameworkFacade` patterns at `harness-cp/src/harness_cp/`: §16.5 composers SHOULD adopt async-first surface (`async def emit_X_state_ledger_entry(...) -> WriteResult`) with sync facade wrapping via existing async-to-sync bridge if sync-driver call sites surface. Decision deferred to implementation-planner per `harness-cp/CLAUDE.md` §5.1.

- **(g)** Pre-revision draft of v1.25 (force-pushed onto PR #37 head before review) carried 8-composer enumeration including U-CP-12 + U-CP-52 with assumed function names (`compose_per_class_attributes` / `decide_hitl_placement`). Impl-time grounding pass against `harness-cp/src/harness_cp/` HEAD surfaced 2 architectural reclassifications (U-CP-12 declarative-only; U-CP-52 runtime-axis-composed) + 3 naming mismatches at U-CP-27 / U-CP-37 / U-CP-49 (now corrected at §16.5.2 + §16.5.7). The pre-revision draft was rebased in-place pre-merge; no closed-and-superseded ledger event owed. Catalogued as `[[impl-time-grounding-pass-pre-merge-revision]]` candidate workspace pattern.

---

## §3 — Status

NEW §16.5 sub-section at v1.25 (6 composer contracts + 2 not-applicable reclassifications). Apply pass: this arc (delta-only spec file co-published with architect recommendation + parent fork doc closure-back-reference annotation). v1.24 + earlier PRESERVED VERBATIM per delta-only-spec-file convention.

CP plan v2.27 → v2.28 revision-pass (separate arc) blocks on this spec being filed. CXA v2.15 → v2.16 §0.4 tracking-marker reflects 6 pending events.

2026-05-28.
