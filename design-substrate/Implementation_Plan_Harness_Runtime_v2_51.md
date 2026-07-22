# Implementation Plan — Harness Runtime — v2.51

*Delta over v2.50. v2.51 is the Runtime plan leg of the RATIFIED **B-65 post-effect signing-carrier cascade-disposition arc** (`.harness/class_2_fork_b65_post_effect_signing_carrier_cascade_disposition.md`, **RATIFIED 2026-07-21 — the operator selected OPTION A AS RECOMMENDED**: §3 terminal-with-result rider + §3b protected result store — outage-independent envelope, tenant-bound lookup, full-strength composite keys, idempotent retrieval with ack-gated deletion + TTL GC fallback, fail-closed writes), absorbing **Runtime spec v1.103** (the change-note's two Runtime-owned surfaces (A) the NEW §14.8.11 protected post-effect result store + (B) the `result_ref` widening, `Spec_Harness_Runtime_v1.md`, SPEC-APPLIED 2026-07-22). v2.51 authors **ONE NEW atomic unit U-RT-145** (next free ID after U-RT-144, verified by grep across the chain: zero occurrences of `U-RT-145` anywhere). Unit count 144 → **145**. CP-owned contract text (the §25.15 branch-terminality rider + the name-match fence — CP spec v1.103 §1) is CROSS-REFERENCED to the same-arc CP plan v2.40 (U-CP-85 amended) — never restated. All sections except the §0 change note, the §1 new-unit body, and the §2/§3 DAG + coverage deltas below are PRESERVED VERBATIM from v2.50 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.50 → v2.51)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_50.md` (v2.50 — the B-48 Runtime leg; NEW U-RT-140..U-RT-144).

### §0.2 Revision scope

Per the fork's §3b (the same spec leg resolves payload recoverability — the protected result store contract) + §2 (the witnesses binding the apply arc). v2.51 decomposes the Runtime v1.103 surfaces into one new unit: the DEDICATED protected result store, the `result_ref` widening to a full-strength tenant-composite key, and the write-once wiring at the carrier's raise site. Naming discretion per Runtime v1.103 §14.8.11's deferred list is respected throughout: the store module/class names + API shape, the composite-key serialization, the envelope/DEK format and provisioning mechanism, the typed refusal/declaration class names + expiry report-line format, the TTL config carrier's field name + default, and the repair-acknowledgement marker's shape are implementation discretion — the unit below pins BEHAVIOR criteria only.

### §0.3 Sections revised

§0 (this change note); §1 (NEW U-RT-145); §2 (DAG delta); §3 (coverage delta). All v2.50-and-earlier unit bodies (U-RT-01..U-RT-144) PRESERVED VERBATIM.

### §0.4 Scope + witness discipline

The fork §2 witnesses home as follows (every witness PD-8 mutation-probed per Workflow v1.18 PD-8): witnesses (a)/(b)/(c) — the fence, the no-resume terminality, and the fold ref-carriage — are CP-owned, homed at the same-arc CP plan v2.40 U-CP-85; witness (d) — `result_ref` resolution through the protected store under the OWNING tenant + typed cross-tenant refusal — homes HERE at U-RT-145, together with the store's own contract witnesses. Cross-axis co-land pin (recorded, not a DAG edge — one B-65 impl arc): U-RT-145 ⊕ CP plan v2.40 U-CP-85 (the widened ref the CP folds carry opaquely; the full-chain fan-out witness runs once, at the impl arc, exercising both halves through the real path).

---

## §1 New unit

### §1.1 U-RT-145 — protected post-effect result store + `result_ref` widening + write-once wiring (v1.103 surfaces A + B)

**Implements:** Runtime spec v1.103 §14.8.11 (the DEDICATED protected result store — full protection contract) + the v1.103 change-note surface (B) (`PostEffectAuditSigningError.result_ref` widened from `uuid4().hex[:12]` to a full-strength identifier composed with the normalized tenant scope). The CP-side branch-terminality + fold semantics (CP spec v1.103 §1) are homed at CP plan v2.40 U-CP-85 — cross-referenced, never restated.

**Depends on:** [U-RT-136 (prior-landed — the `PostEffectAuditSigningError` carrier + post-effect fence sites this unit widens and wires; Runtime plan v2.49 §1.3 lineage)].

**Files affected (logical):** a new protected-result-store module in `harness-runtime`; `lifecycle/audit_signing_errors.py` (the `result_ref` widening at the carrier); **EVERY carrier raise site** (codex round-9 on the spec PR — the four `PostEffectClass` dispatcher paths that construct `PostEffectAuditSigningError`: `lifecycle/llm_dispatch.py` (provider-response), `lifecycle/runtime_tool_dispatcher.py` (tool-invocation), `lifecycle/sub_agent_dispatch.py` (sub-agent-dispatch), `lifecycle/webhook_delivery_composer.py` (webhook-delivery)) plus the composition-root factories that build those dispatchers (the store dependency + owning tenant scope are INJECTED there — a raise site the injection does not reach is an acceptance FAILURE); the bootstrap/shutdown GC-sweep hook sites; the TTL config carrier (dual env-loader registration per the committed convention if a RuntimeConfig scalar is chosen — carrier shape implementation-discretion per §14.8.11's deferred list).

**Acceptance criteria:**

1. **(Composite key + write-once.)** `result_ref` is a FULL-STRENGTH identifier (full uuid4 or equivalent — the `uuid4().hex[:12]` 48-bit truncation at `audit_signing_errors.py:91` is WIDENED), composed with the normalized tenant scope (the OD v1.34 §21.2.1 row-2 writer-normalized tenant tag — OD-owned, cross-referenced) as the store's composite key. Creation is collision-safe WRITE-ONCE: a write against an existing key is REFUSED TYPED, never overwritten.
2. **(Outage-independent envelope.)** Payloads are encrypted at rest via an envelope path INDEPENDENT of the audit-signing KMS (a provisioning-time-wrapped local DEK or equivalent) — the carrier's primary trigger IS a signing-KMS outage; a store whose envelope depends on that KMS is an acceptance FAILURE.
3. **(Fail-closed write.)** On a store-write failure, the carrier surfaces WITHOUT a resolvable ref and SAYS SO TYPED (an explicit typed unresolvable-ref declaration on the surfaced failure) — never a silently-unresolvable reference.
4. **(Tenant-bound lookup.)** Retrieval requires the OWNING tenant scope; a cross-tenant resolution attempt is REFUSED TYPED.
5. **(Serialization envelope.)** Non-Mapping / arbitrary-object results are stored as an OPAQUE byte-envelope + type tag — never lossy coercion.
6. **(Write-once at EVERY raise site — per-dispatcher injection.)** The store write happens ONCE, at the carrier's raise site — and the protected store + owning tenant scope reach ALL FOUR `PostEffectClass` raise paths (provider, tool, sub-agent, webhook) via explicit per-dispatcher injection or a scoped-context contract from the composition root. Isolated store tests passing while a real dispatcher path still publishes an unresolvable ref is the wired-but-unreachable failure mode and an acceptance FAILURE (codex round-9).
7. **(Bounded retention.)** Retrieval is IDEMPOTENT (read-then-crash can read again); deletion ONLY after an explicit DURABLE repair acknowledgement; unacknowledged entries carry a deployment-configurable TTL with GC sweeps at bootstrap/shutdown AND a periodic-or-opportunistic runtime sweep while the process stays up (codex round-10); TTL expiry surfaces as a TYPED report-log line, never silent loss.
8. **(Dedicated store.)** The store is NOT `EngineOutputStore` (foreclosed per the fork §3b: plaintext JSONL, no tenant-authorized lookup, Mapping-only, plaintext PII exposure under an MTC signing outage).

**Tests (mutation-probed per PD-8):** **Fork §2 witness (d):** `test_result_ref_resolves_preserved_payload_under_owning_tenant` + `test_cross_tenant_read_refused_typed` (mutation probe: dropping the tenant component from the key lets a cross-tenant read resolve and fails). **Store contract witnesses:** `test_write_once_existing_key_refused_typed`, `test_retrieval_idempotent_across_repeated_reads`, `test_deletion_only_after_durable_repair_ack` (mutation probe: deleting on first read destroys the only recoverable copy and fails the re-read), `test_ttl_expiry_gc_sweep_emits_typed_report_line` (mutation probe: silent expiry fails), `test_store_write_failure_carrier_surfaces_typed_unresolvable_ref` (the DISCRIMINATED unresolvable declaration replaces the live key at the carrier field and the CP fold carries it verbatim — witness (d)'s resolution applies only to the resolvable shape, witness (b)'s ref-carriage covers BOTH shapes; mutation probe: swallowing the write failure OR publishing a dead key that reads as live fails), `test_non_mapping_result_round_trips_via_byte_envelope_and_type_tag`, `test_unserializable_result_composes_with_fail_closed_write_typed_serialization_failure` (a generator/open-handle/unsupported value: the versioned serializer's failure composes with the fail-closed write disposition — the carrier surfaces without a resolvable ref, the typed declaration NAMES the serialization failure, the store persists nothing; mutation probe: lossy coercion or a crash on the unsupported value fails — Runtime v1.103 §14.8.11 serialization-failure disposition, codex round-1 on the spec PR), `test_envelope_resolves_during_simulated_signing_kms_outage` (the store's reason-for-being: retrieval succeeds while the signing backend is unavailable; mutation probe: routing the envelope through the signing KMS fails this witness), `test_persisted_bytes_disclose_nothing` (the encrypted-at-rest criterion ENFORCED, codex round-5 on the spec PR: the on-disk bytes contain neither the plaintext payload nor a trivially-decodable encoding of it — a known sentinel value written through the store is absent from the raw persisted bytes and from their base64/utf-8 decodings; mutation probe: plaintext or base64-only storage through an independent local path fails), and `test_crash_between_temp_write_and_commit_leaves_no_destination_entry` (crash-atomic durable publication, codex round-7 on the spec PR: interrupt the publication after the temp write but before the atomic no-replace commit — the destination key does NOT exist, the write-once existence check does not wedge on a partial entry, and a subsequent write against the same key succeeds; mutation probe: direct write-in-place publication — no temp-then-commit — fails this witness), **Per-raise-site wiring witnesses (codex round-9 — one END-TO-END resolution test per `PostEffectClass`):** `test_provider_response_raise_site_publishes_resolvable_ref_e2e`, `test_tool_invocation_raise_site_publishes_resolvable_ref_e2e`, `test_sub_agent_dispatch_raise_site_publishes_resolvable_ref_e2e`, `test_webhook_delivery_raise_site_publishes_resolvable_ref_e2e` — each drives the REAL dispatcher path (fail-closed signing tripped after a completed stub effect), catches the surfaced carrier, and resolves `result_ref` through the store under the owning tenant to the completed effect's payload (mutation probe, per site ALONE: removing that ONE dispatcher's store injection leaves its carrier unresolvable and fails ONLY that site's witness), `test_wrong_key_or_tampered_ciphertext_fails_typed_before_deserialization` (a flipped ciphertext byte or a wrong DEK refuses typed BEFORE any deserialization runs; mutation probe: deserializing tampered ciphertext — or silently returning it — fails).

**Rollback boundary:** revert the store + widening; the carrier reverts to the 48-bit log-correlation ref with no recovery path — the fork §3b recoverability defect reopens; the CP v2.40 U-CP-85 fold carries a ref that resolves to nothing (witness (d) fails).

---

## §2 DAG topology delta (v2.50 → v2.51)

One new unit; acyclic:

```
L0-within-delta: U-RT-145 (← U-RT-136 prior-landed)
```

Cross-axis relationships: NONE new — U-CP-85 (CP plan v2.40) is a CO-LAND/INTEGRATION PIN of the one B-65 impl arc, never a dependency (CP carries the ref as an opaque string through the import-free name-match fence; no package edge either direction).

---

## §3 Coverage matrix delta (v2.50 → v2.51)

| Spec surface (Runtime v1.103) | Units covering |
|---|---|
| §14.8.11 protected post-effect result store (surface A) | U-RT-145 |
| `result_ref` widening — full-strength tenant-composite key (surface B) | U-RT-145 |
| CP §25.15 branch-terminality rider + name-match fence (CP spec v1.103 §1) | CP plan v2.40 U-CP-85 (cross-axis — no Runtime unit) |

Both v1.103 Runtime-owned surfaces covered; the new unit traces both; fork §2 witnesses (a)–(d) all homed ((a)/(b)/(c) at U-CP-85; (d) here). ✓

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_51.md` (delta over v2.50) |
| Authored at | Phase 7 — B-65 post-effect signing-carrier cascade-disposition apply leg (2026-07-22) |
| Authoring authority | Runtime spec v1.103 (change-note + NEW §14.8.11, `Spec_Harness_Runtime_v1.md`, SPEC-APPLIED 2026-07-22) + `.harness/class_2_fork_b65_post_effect_signing_carrier_cascade_disposition.md` (RATIFIED 2026-07-21, OPTION A AS RECOMMENDED) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_50.md` (v2.50 — B-48 Runtime leg) |
| Siblings (same arc) | `Implementation_Plan_Control_Plane_v2_40.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
