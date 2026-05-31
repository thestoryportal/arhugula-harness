# Spec: Control Plane — v1.29 (delta over v1.28)

---

## Change-note (v1.28 → v1.29)

**Scope of revision.** Narrow-scope recipe-completion amendment authoring NEW §16.5.12 — per-composer `procedural_tier_snapshot_ref` sidecar population discipline — and a canonical-reading amendment at §16.5.3 chapeau acknowledging the IS HEAD `EntryPayload` field-set extension from 4 fields to 5 fields per IS spec v1.3 §5.1 (LANDED at PR #89 commit `ec42d22` 2026-05-30). v1.28 §16.5.6.X audit-stub disposition + v1.27 §16.5 substantive content + v1.26 β.i resolution + v1.25 NEW §16.5 sub-section authoring all PRESERVED VERBATIM per delta-only-spec-file convention.

**Trigger.** Council deliberation at session-open 2026-05-31 on H_T-IS-2 producer-site cascade scope (12 enumerated EntryPayload construction sites: 8 CP-axis + 4 runtime-axis). T1 empirical probe at deliberation close — "does the engine-layer kw-only-callable threading pattern at the 3 `pause_resume_protocol.py` sites require a Class 1 spec amendment?" — surfaced two findings:

1. **IS spec v1.3 §5.2 amendment 2** already explicitly pre-authorizes the engine-layer threading pattern: *"Engine-layer composers without `HarnessContext` access at firing time receive the resolver as a `Callable[[], Identifier]` kw-only parameter at the composer function signature, bound at runtime composition time per CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` kw-only-callable-bound-at-runtime-wiring precedent."* The contract surface is settled at IS-axis authority.
2. **CP spec §16.5.3 / §16.5.4 / §16.5.5 / §16.5.6** enumerate per-composer recipes for `action_id` / `idempotency_key` / `response_hash` (β.i-relocated to `idempotency_key` suffix at v1.26) / `actor` / `timestamp` — but NO per-composer recipe exists at CP spec for `procedural_tier_snapshot_ref`. CP spec carries stale-vs-IS-HEAD "4-field" framing through v1.26 → v1.28.

The cascade arc cannot proceed at the producer-site lift without a documented per-composer recipe for the 5th sidecar field. v1.29 authors the recipe + corrects the field-count framing. ZERO new contract; ZERO new field; ZERO new behavior at consumer side (IS HEAD already absorbs the 5th field; field is `Optional` with default `None`; consumers that don't populate it preserve pre-v1.3 behavior at the data layer).

**Decisive structural argument for narrow-scope shape.** Per IS spec v1.3 §5.2: the engine-layer kw-only-callable threading pattern at CP §16.5.7 is *named explicitly* as the canonical bound pattern. Adding `procedural_tier_snapshot_resolver: Callable[[], Identifier]` as a sibling kw-only parameter at the 3 engine-layer composer signatures (`emit_pause_resume_state_ledger_entry` + `emit_pause_captured_state_ledger_entry` + `emit_resume_attempted_state_ledger_entry`) is NOT a contract surface extension at §16.5.7 — it is the documented IS-pre-authorized application of the existing kw-only-callable pattern to a sibling dependency. §16.5.7's "Each composer accepts `ledger_writer: ... ` as a kw-only parameter" is a floor (composer MUST accept this) not a ceiling (composer MUST accept ONLY this); Python signature semantics permit additional kw-only parameters without contradicting the spec text.

For ctx-access composer sites (the other 9 of 12: 5 CP-axis composers at workflow-layer + 4 runtime-axis composers at lifecycle layer), the sidecar population is direct via `HarnessContext` access at composer-construction time per IS spec v1.3 §5.2 resolver contract.

**Council deliberation provenance.** Resolved as **T1 in favor of C1's per-pattern PR shape** (9+3) at the council orchestrator pilot 2026-05-31 — see workspace session notes. C3's coherence concern (ledger ambiguity at half-cascade) mitigated by stacking PR-2 (9 ctx-access sites) and PR-3 (3 engine-layer sites) in the same merge window; this v1.29 amendment is PR-1 of the 3-PR stack.

**v1.28 substantive content PRESERVED VERBATIM except for the scoped amendments below.** v1.28 §16.5.6 + §16.5.6.X + v1.27 §16.5.4 row U-CP-14 + v1.26 β.i §16.5.3 rewrite + v1.25 NEW §16.5 sub-section authoring all preserved verbatim per delta-only-spec-file convention.

**Co-publication this session.** No impl + no test in this PR (recipe-completion doc patch only); PR-2 (9 ctx-access sites at harness-cp + harness-runtime) + PR-3 (3 engine-layer sites + workflow-driver entry-point threading) follow as separate arcs. Workspace `CLAUDE.md` §2.3 CP spec row bump v1.28 → v1.29 + harness-cp/CLAUDE.md §1.2 spec authority row bump + clearance marker at `.harness/clearance/Spec_Control_Plane-v1_29-cleared-2026-05-31.md`.

**ZERO breaking change at signed-payload surfaces.** C-CP-16 §16.2 `CPAuditLedgerEntry` 8-field shape PRESERVED VERBATIM (audit-half ledger is distinct from §16.5 state-ledger half per §16.5.1 two-typed-ledger architecture). C-CP-20 §20.4 `CPSignedAuditLedgerEntry` signing contract PRESERVED VERBATIM. `emit_override_audit_entry` PRESERVED VERBATIM at all surfaces.

**ZERO new field at producer composer surface.** All 6 §16.5.2 composers retain their existing kw-only parameter set; the resolver is threaded as a sibling kw arg only at the 3 engine-layer composers per IS spec v1.3 §5.2 pre-authorization (Python-level signature extension; not a spec-level new field).

**ZERO cross-axis cascade.** IS spec v1.3 PRESERVED VERBATIM (read-only at this arc; this CP amendment consumes IS spec v1.3 §5.1 + §5.2 contracts, does not modify them). OD spec v1.27 PRESERVED VERBATIM. AS spec v1.7 PRESERVED VERBATIM. Runtime spec v1.39 PRESERVED VERBATIM. CXA v2.17 PRESERVED VERBATIM (CP→IS bucket §2.3.2 rows 38-43 absorb the §16.5 composer Pattern-P1 seams; v1.29 producer-side recipe completion does not add a new edge). ADR-F2 v1.2 PRESERVED VERBATIM. ADR-D5 v1.4 PRESERVED VERBATIM. ADD v1.3 + PRD v1.1 PRESERVED VERBATIM. Workflow v1.13 PRESERVED VERBATIM.

---

## §1 — NEW §16.5.12 — Procedural-tier-snapshot sidecar population discipline

### §16.5.12.1 — Field scope and authority

Per IS spec v1.3 §5.1 (LANDED 2026-05-30): `EntryPayload` carries a D-derivative sidecar field `procedural_tier_snapshot_ref: Identifier | None = None`, additive at the D-derivative extension layer authorized by ADR-F2 §Consequences (c). The sidecar carries the content-hash digest identifying which procedural-tier snapshot (active Skills version set + routing manifest SHA per IS spec v1.3 §5.2 2-component scope; prompts component deferred) was in scope at the entry's write-time.

`None` is the canonical value at entries written outside an active workflow context (bootstrap-stage entries; operator-explicit administrative entries). Workflow-context emission sites — the 6 §16.5.2 composers in scope at this amendment — MUST populate the sidecar with a resolved `Identifier` value at every emission, not `None`. Workflow-context with `None` sidecar is a producer-site bug.

### §16.5.12.2 — Per-composer population recipe (uniform)

Each §16.5.2 composer populates the sidecar via the IS spec v1.3 §5.2 resolver contract:

| Composer | Population recipe |
|---|---|
| U-CP-14 (`per_step_override_evaluator.emit_override_state_ledger_entry`) | `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` |
| U-CP-27 (`workload_binding_engine_class_selection.emit_workload_class_selection_state_ledger_entry`) | `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` |
| U-CP-30 (`pause_resume_protocol.PauseResumeProtocol.emit_pause_resume_state_ledger_entry`) | `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` |
| U-CP-37 (`hitl_as_tool_call_rewriting.emit_hitl_tool_call_rewriting_state_ledger_entry`) | `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` |
| U-CP-49 (`pause_resume_protocol.emit_pause_captured_state_ledger_entry`) | `procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()` |
| U-CP-50 (`pause_resume_protocol.emit_resume_attempted_state_ledger_entry`) | `procedural_tier_snapshot_ref = procedural_tier_snapshot_resolver()` |

The recipe diverges by composer-axis access to `HarnessContext`:

- **5 workflow-layer composers (U-CP-14 / U-CP-27 / U-CP-30 / U-CP-37) + 1 engine-layer composer with ctx-access path:** call `resolve_procedural_tier_snapshot(harness_context)` directly with the in-scope `HarnessContext` reference per IS spec v1.3 §5.2 signature. `harness_context` is sourced from the composer's containing call stack (workflow_driver step-dispatch ctx pass-through OR composer-construction-site closure capture).
- **3 engine-layer composers without ctx-access (U-CP-30 workflow-layer is workflow-layer; U-CP-49 + U-CP-50 are engine-layer; U-CP-30 engine-layer entry — see §16.5.7 for the workflow-vs-engine-layer split):** accept `procedural_tier_snapshot_resolver: Callable[[], Identifier]` as a kw-only parameter at the composer function signature per IS spec v1.3 §5.2 amendment 2 pre-authorization (citing CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` precedent). The resolver closure is bound at runtime composition time at the same wiring layer as the `ledger_writer` callable (see §16.5.12.4 below).

### §16.5.12.3 — Composer signature extension at engine-layer composers

The 3 engine-layer composer functions extend their signatures with the sibling kw-only parameter:

```python
async def emit_pause_resume_state_ledger_entry(
    ...,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
    procedural_tier_snapshot_resolver: Callable[[], Identifier],  # NEW at v1.29
) -> WriteResult: ...

async def emit_pause_captured_state_ledger_entry(
    ...,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
    procedural_tier_snapshot_resolver: Callable[[], Identifier],  # NEW at v1.29
) -> WriteResult: ...

async def emit_resume_attempted_state_ledger_entry(
    ...,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
    procedural_tier_snapshot_resolver: Callable[[], Identifier],  # NEW at v1.29
) -> WriteResult: ...
```

Both kw-only callables are REQUIRED at the engine-layer composer signature (no default; caller MUST supply both at every invocation). This preserves the §16.5.7 "Each composer accepts `ledger_writer` as a kw-only parameter" floor and adds the sibling resolver per IS spec v1.3 §5.2 amendment 2 explicit authorization. Python semantics: §16.5.7's enumeration is non-exclusive; additional kw-only parameters are admissible without spec contradiction.

### §16.5.12.4 — Runtime wiring at engine-layer composers

The `procedural_tier_snapshot_resolver` kw-only parameter at the 3 engine-layer composer signatures is bound at runtime composition time per §16.5.8 (Runtime wiring discipline) — the same wiring layer that binds `ledger_writer` to `ctx.ledger_writer.append_ledger_entry`. The binding source per IS spec v1.3 §5.2 amendment 2:

```python
procedural_tier_snapshot_resolver = make_procedural_tier_snapshot_resolver(harness_context)
```

`make_procedural_tier_snapshot_resolver(harness_context: HarnessContext) -> Callable[[], Identifier]` is the U-RT-112 factory at `harness-runtime/src/harness_runtime/lifecycle/procedural_tier_snapshot.py` (LANDED 2026-05-30 per IS spec v1.3 Q-γ=(γ-2) ratification). The factory closure captures `harness_context` and re-computes the snapshot at every invocation per U-RT-112 AC #8 direct-compute discipline; consumer-site memoization is admissible per U-RT-112 AC #8 trailing implementation-discretion clause.

Binding home for the resolver-closure construction: the same per-composer factory function in `harness-runtime/src/harness_runtime/lifecycle/` that already binds `ledger_writer` per §16.5.8. Per-composer materialize-stage helper authors both bindings together; the resolver is sibling to the writer at the composer-construction surface.

### §16.5.12.5 — Failure-mode posture (composer-site)

If `resolve_procedural_tier_snapshot(harness_context)` raises at composer invocation (programming error at composition time per U-RT-112 AC #1 pure-function semantics; transient retry does NOT apply), the composer MUST propagate the exception to its caller. The composer-side contract is HALT-on-resolver-failure:

- A workflow that cannot resolve its procedural-tier snapshot cannot emit a deterministically-replayable state-ledger entry. Emitting `procedural_tier_snapshot_ref=None` at a workflow-context emission site silently degrades the ledger's audit guarantee per §16.5.12.1 (workflow-context with `None` sidecar is a producer-site bug).
- Resolver failure modes are programming errors at composition time: schema drift at `harness_context.skills`; Pydantic model integrity at `routing_manifest.model_dump()`; non-JSON-serializable field at `json.dumps` canonical serialization. Retry does not fix these; they require operator intervention at the composition surface.
- The composer's typed-exception surface is implementer-discretion (a typed `ProceduralTierResolutionError` wrapping the original exception is the recommended shape; CP spec does not commit a specific exception identity at v1.29).

The composer-site HALT posture is symmetric with C-CP-16 §16.2 audit-half emission's POSIX-semantics on JSONL write failure: the producer surfaces the failure to the caller; the caller decides workflow continuation policy.

### §16.5.12.6 — Caching scope (composer-site implementer-discretion)

Per U-RT-112 AC #8 direct-compute discipline + trailing implementation-discretion clause: the resolver re-computes from captured `harness_context` at every invocation (no module-level memoization). At consumer composer sites, two caching shapes are admissible:

1. **Per-emission re-resolve.** Composer calls the resolver at every emission. Default at v1.29; matches AC #8 explicit posture; bounded cost per IS spec v1.3 §5.2 2-component scope (one sha256 over routing_manifest canonical JSON + one sha256 over canonical_join payload).
2. **Per-composer-construction factory closure.** Composer binds `_resolver = make_procedural_tier_snapshot_resolver(ctx)` once at construction; calls `_resolver()` at every emission. The factory closure captures ctx; subsequent calls re-walk `ctx.skills` + `ctx.routing_manifest` per AC #8 (the factory does not cache the result, only the ctx reference). Admissible because IS spec v1.3 §2.4 commits procedural-tier immutability mid-run; the resolver's input space does not change across a workflow's emission stream.

CP spec does not commit one shape over the other at v1.29; per-composer implementation-discretion per the per-composer impl arc.

### §16.5.12.7 — Invariants

1. **Workflow-context emission MUST populate.** Every §16.5.2 composer invocation in workflow-context populates `procedural_tier_snapshot_ref` with a resolved `Identifier`; `None` at workflow-context emission is a producer-site bug per §16.5.12.1.
2. **Outside-workflow-context emission MAY be `None`.** Bootstrap-stage entries + operator-explicit administrative entries emit `procedural_tier_snapshot_ref=None` per IS spec v1.3 §5.1. These are NOT §16.5.2 composer-emitted entries.
3. **Sidecar does NOT widen C-CP-16 §16.2.** `CPAuditLedgerEntry` audit-half shape PRESERVED VERBATIM at 8 fields. The sidecar lives at IS-anchored `EntryPayload` only, not at CP-internal audit ledger.
4. **Sidecar does NOT enter `idempotency_key` derivation per §16.5.4.** Each composer's idempotency-key formula at §16.5.4 PRESERVED VERBATIM; the procedural-tier snapshot is NOT a disambiguator at the dedup key (the snapshot is per-deployment identity, not per-emission identity).
5. **Sidecar enters IS-internal `compute_response_hash` per C-IS-06 §6.2.** Per IS spec v1.3 amendment 1: the F-layer six-field shape at §5 PRESERVED VERBATIM; sidecar is additive at D-derivative extension. IS HEAD `compute_response_hash` canonicalization at `harness-is/src/harness_is/entry_hash.py` INCLUDES the sidecar field per IS spec v1.3 §5.1 acknowledgement.
6. **Composer-site HALT on resolver failure.** §16.5.12.5 commits HALT posture; producer surfaces resolver-raise to caller; caller decides workflow continuation.

---

## §2 — Canonical-reading amendment at §16.5.3 chapeau

v1.26 §16.5.3 (REPLACES v1.25 §16.5.3 per nested fork β.i ratification 2026-05-29) declares: *"`EntryPayload` per IS HEAD shape carries 4 fields `(action_id, idempotency_key, actor, timestamp)` per `harness-is/src/harness_is/state_ledger_write.py:62-75` (`extra='forbid'` rejects any caller that supplies additional fields)."*

This claim was accurate at v1.26 authoring (2026-05-29 commit `ec4a2f7`); it became stale at IS spec v1.3 absorption (PR #89 commit `ec42d22` 2026-05-30) which authored the 5th D-derivative sidecar field `procedural_tier_snapshot_ref: Identifier | None = None` at `state_ledger_write.py:78`.

**Canonical reading at v1.29.** Substitute *"5 fields `(action_id, idempotency_key, actor, timestamp, procedural_tier_snapshot_ref)`"* for *"4 fields `(action_id, idempotency_key, actor, timestamp)`"* at every occurrence in v1.26 §16.5.3 + v1.26 §16.5.9 invariant 2 + v1.27 + v1.28 substantive text. The `extra='forbid'` Pydantic v2 discipline PRESERVED VERBATIM at IS HEAD (the model now declares 5 fields, still forbids extras beyond declared fields).

The §16.5.3 per-field composition discipline at v1.26 enumerates `action_id` + `idempotency_key` + `actor` + `timestamp` recipes verbatim (3 composer-side + 1 IS-internal); the 5th field's per-composer recipe is authored at v1.29 §1 (NEW §16.5.12). v1.26 §16.5.3 body text PRESERVED VERBATIM; downstream readers apply this v1.29 §2 canonical-reading substitution when interpreting v1.26 §16.5.3 / §16.5.9 invariant 2 field-set claims.

v1.26 §16.5.9 invariant 2 amended at the canonical-reading layer: composer-supplied field count 4 → 5; IS-internal computed field set PRESERVED VERBATIM (`response_hash` per C-IS-06 §6.2 + `prior_event_hash` per C-IS-13 §13.5; 2 IS-internal fields, both unchanged at v1.29).

---

## §3 — Adjacent observations (NOT patched per FM-2)

- **(a) Engine-layer caller-site threading discipline at workflow_driver entry-point.** WHICH workflow-driver call site binds the resolver closure to which of the 3 engine-layer composer call sites is implementer-discretion. The U-RT-112 factory + the §16.5.8 runtime wiring layer together fully specify the binding mechanism; the per-impl-arc choice of which workflow-driver method threads the factory output is bounded by the existing pause/resume entry-point pattern at `harness-cp/src/harness_cp/workflow_driver.py` (the same surface that threads `ledger_writer`). NOT patched at CP spec v1.29 per FM-2.

- **(b) Typed-exception surface at composer-site resolver-failure HALT.** Composer-site HALT on resolver-raise is committed at §16.5.12.5 as posture; the specific typed-exception shape (e.g., NEW `ProceduralTierResolutionError` wrapping the original) is implementer-discretion. Recommended at the impl arc per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` 58th-application surfacing. NOT patched at CP spec v1.29 per FM-2.

- **(c) Caching scope canonicalization.** §16.5.12.6 enumerates two admissible caching shapes (per-emission vs. per-composer-construction factory closure) without committing CP-spec preference. Future amendment authoring a single canonical shape is admissible at a follow-on revision pass; CP spec carries the choice as impl-discretion at v1.29.

- **(d) Workflow-context vs. outside-workflow-context discriminator.** §16.5.12.1 commits the field semantic per IS spec v1.3 §5.1: `None` admissible at outside-workflow-context entries (bootstrap + admin); REQUIRED at workflow-context entries (the 6 §16.5.2 composers). The discriminator is structural at the composer surface (these 6 composers always fire in workflow-context); no runtime discriminator is needed.

- **(e) Sub-species 3 candidate at workflow v1.13 §7.4.7.2: `cross-axis-stale-since-sibling-spec-version-bump`.** v1.26 §16.5.3 "4-field" framing went stale at IS spec v1.3 absorption (2026-05-30) without CP spec authoring an acknowledgement amendment; carry persisted across v1.27 + v1.28 + ~24 hours of pre-cascade work. Distinct sub-species from prior catalogued shapes (3.code-resolution / 3.fork-doc-closure / 3.workflow-grammar / 3.empirical-verification-of-external-authority / 3.same-session-immediate-sequel / 3.retirement-event-filing-arc / 3.binding-fix-not-schema-extension / 3.intra-spec-sibling-supersession / 3.carry-suggests-foreclosed-reading / 3.forward-looking-code-comment-becomes-phantom-ledger-cite / 3.checkpoint-listed-as-open-but-already-applied) — the staleness shape here is cross-axis-spec-version-coordination, where one axis spec advances and a downstream-consumer axis spec carries pre-bump framing across multiple subsequent revisions. Cardinality 1; awaits second instance before workflow-doc promotion.

- **(f) Council orchestrator pilot artifact.** v1.29 is the first design-substrate amendment authored downstream of a council deliberation arc rather than a direct architect-recommendation or operator AskUserQuestion arc. The deliberation surfaced T1 (cascade-grouping shape: 1+11 vs. 9+3) and T2 (caching scope) tensions; T1 resolved at empirical probe in C1's favor + co-publication discipline mitigation; T2 documented at §16.5.12.6 as admissible-either-way. NOT patched at CP spec; pattern catalogued at workspace session notes for future council deliberation cadence calibration.

---

## §4 — Status

Narrow-scope recipe-completion amendment authoring NEW §16.5.12 (per-composer `procedural_tier_snapshot_ref` sidecar population discipline) + canonical-reading amendment at §16.5.3 chapeau (4-field → 5-field framing refresh per IS spec v1.3 absorption). Apply pass: this arc (delta-only spec file PR-1 of a 3-PR stack; PR-2 lifts 9 ctx-access producer sites; PR-3 lifts 3 engine-layer producer sites with the §16.5.12.3 signature extension). ZERO impl + ZERO test at v1.29; co-publication scope limited to workspace `CLAUDE.md` row bump + harness-cp/CLAUDE.md row bump + clearance marker.

H_T-IS-2 substitution-retirement transit posture UNCHANGED at PARTIAL (per batch-49 close 2026-05-30); PARTIAL → RETIRED transit GATED on full producer-site cascade completion (PR-2 + PR-3) per X-AL-2 second conjunct.

v1.28 + v1.27 + v1.26 + v1.25 + earlier PRESERVED VERBATIM per delta-only-spec-file convention.
