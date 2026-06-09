---
title: R-CXA-1 / R-CXA-2 Producer-Seam Design Spec
status: design-brief (forks ratified 2026-06-08; implementation planning/back-flow remains separate)
created: 2026-06-08
posture: design-phase (`.harness/**` only — NO design-substrate edits in this arc)
roadmap: R-CXA-1-as-is-seam, R-CXA-2-cp-is-seam (both stay OPEN)
extends: class_1_tension_u_rt_35_cp_is_wiring_gaps.md (CLOSED — firing-site-layer continuation)
forks_filed:
  - class_1_fork_u_cp_78_pause_captured_type_impedance.md
  - class_2_fork_r_cxa_2_producer_loop_ownership.md
---

# R-CXA-1 / R-CXA-2 Producer-Seam Design Spec

*Faithfully specs the missing **producers** (firing sites) that gate `R-CXA-1` (AS→IS secret-fetch audit) and `R-CXA-2` (CP→IS HITL-rewrite + engine-layer pause/resume) so a future implementation arc can close the seams without hollow ledger emission. Authored under design-phase posture per workspace `CLAUDE.md` §4.3 + §11; the filing arc produced this brief + fork docs only. The 2026-06-08 ratification arc resolved the fork decisions but still defers all `design-substrate/**` spec/plan amendments and runtime implementation to a separate implementation/back-flow arc.*

---

## §0. Why this arc exists — the firing-site-layer continuation

The U-RT-35 CP→IS wiring tension (`class_1_tension_u_rt_35_cp_is_wiring_gaps.md`) is **CLOSED**. Its closure (batches 46+47, 2026-05-29) wired the *runtime composer surface*: `RuntimeCpIsWiring` (U-RT-110) + the production-caller invocation paths (U-RT-111) were authored, and `H_T-RT-35` retired via **"Reading α' vacuous-second-conjunct at firing-site layer"** — i.e. the wiring methods exist, but the *upstream producers that would invoke them* do not. That fork doc's own closing note (§"Fork doc CLOSED", line 355) makes the continuation explicit:

> "sub-species 7d closures are conditionally **re-verifiable when future arcs land production callers at any of the 5 firing-site blocker substitution sites**."

`R-CXA-1` and `R-CXA-2` ARE those future arcs. The composer methods are materialized + unit-tested; what is absent is the **production producer** — the call-site that constructs a non-hollow event and invokes the composer. This brief specs those producers.

**Empirically grounded at HEAD `7ae493d` (origin/main, 2026-06-08):**

| Composer (runtime surface) | action_id | Production caller? | Source |
|---|---|---|---|
| `RuntimeAsIsWiring.emit_secret_fetch_audit_entry` | (AS→IS audit) | **NONE** | `as_is_wiring.py:96`; `.harness/r-cxa-1-producer-audit-2026-06-08.md` |
| `RuntimeCpIsWiring.emit_hitl_tool_call_rewriting_state_ledger_entry` | `cp.hitl-tool-call-rewriting` | **NONE** | `cp_is_wiring.py:274` |
| `RuntimeCpIsWiring.emit_pause_captured_state_ledger_entry` | `cp.pause-captured` (engine) | **NONE** | `cp_is_wiring.py:308` |
| `RuntimeCpIsWiring.emit_resume_attempted_state_ledger_entry` | `cp.resume-attempted` (engine) | **NONE** | `cp_is_wiring.py:340` |

For contrast, the **already-wired** CP→IS composers (do NOT confuse with the above): `emit_sibling_ledger_entry` (U-CP-34), `emit_override_state_ledger_entry` (U-CP-74, `workflow_driver.py:859`), `emit_workload_class_selection_state_ledger_entry` (U-CP-75, stage-3b), and the **workflow-layer** `emit_pause_resume_state_ledger_entry` (U-CP-76, `cp.pause-resume-protocol`, `workflow_driver.py:582/808/965`). The workflow-layer pause/resume composer being wired is precisely what the engine-layer pair is **not** — see §5.

> **Producer-discovery discipline** (`[[r-cxa-seam-wiring-is-producer-discovery]]`): "wire a production caller" first requires grepping the seam's REAL producer; the answer is often DEFER-don't-wire (hollow). This brief applies that lens per-seam, classifying each gap before recommending action.

> **Post-MVP loop architecture → sibling brief.** This file is the *compact decision anchor* (why R-CXA-2 must not be hollow-wired; per-seam B1/B2/B3 disposition). The larger **post-MVP producer-loop architecture** — how to actually build the HITL model-driven tool loop (DP-1(a)) and the engine recovery loop (DP-2(a)+DP-3(a)), the staged path to an impl plan, and the sharpened governance/escalation determination — lives at **`r-cxa-2-post-mvp-producer-loop-product-brief.md`** (conditioned on operator post-MVP build authorization; R-CXA-2 stays `STILL-BOUNDED` until then). Read this anchor for the *decisions*; read the sibling for the *architecture*.

---

## §1. The organizing principle — three buckets per gap

Each producer gap is classified into exactly one bucket; the bucket dictates the artifact (per advisor 2026-06-08):

| Bucket | Meaning | Artifact |
|---|---|---|
| **B1 — buildable** | The existing contract is sufficient; the producer is spec'd-but-unbuilt | Spec the producer + acceptance criteria + tests (this brief) |
| **B2 — settled** | A derivation/decision is already ratified | Cite it; do not re-derive |
| **B3 — decision/defect** | Requires a contract / ownership / identity decision, or is an outright defect | **Surface as a fork; do NOT resolve unilaterally** (X-AL-3 / §4.3) |

B3 is load-bearing: silent absorption of a design-phase defect is the workspace's named worst failure mode (`CLAUDE.md` §4.3 + §10.5). Where a producer-seam turns on a contract/ownership/identity choice, this brief **files a fork and recommends a reading** rather than picking one in-spec.

| Producer | Bucket | Disposition |
|---|---|---|
| R-CXA-1 AS→IS scoped secret-fetch | **B1** | Spec the workflow-time scoped producer (§3) |
| R-CXA-1 bootstrap provider-key exclusion | **B2** | Cite ratified Reading-D DON'T-WIRE (§3.5) |
| R-CXA-2 HITL `semantic_variant_binding_id` derivation | **B2** | Cite ratified v2.39 Reading B (§4.3) |
| R-CXA-2 HITL inner-loop firing site | **B3** | Fork (§4.5 → `class_2_fork_r_cxa_2_producer_loop_ownership.md` DP-1) |
| R-CXA-2 engine recovery-loop ownership | **B3** | Fork (§5.4 → DP-2) |
| R-CXA-2 pause/resume disambiguator derivation | **B3** | Fork (§5.5 → DP-3) |
| R-CXA-2 `pause-captured` PauseEvent↔PauseSnapshot impedance | **B3 (defect)** | Class 1 fork (§5.6 → `class_1_fork_u_cp_78_pause_captured_type_impedance.md`) |

---

## §2. R-CXA-1 — AS→IS scoped secret-fetch producer

**Composer (LANDED + tested, zero production caller):** `RuntimeAsIsWiring.emit_secret_fetch_audit_entry(event: SecretFetchEvent, *, prior_entry: StateLedgerEntry | None = None) -> WriteResult` (`harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py:96`). It composes via the AS surface `compose_secret_fetch_audit_entry` (`harness-as/src/harness_as/secret_fetch_audit.py:76`), extracts the IS-routable `EntryPayload` fields, builds the `WriteKey` from `(thread_id, step_id, idempotency_key)`, and delegates the durable write to `LedgerWriter.append`.

### §2.1 Production caller location / call-site family

**The producer call-site family is already SPECIFIED, not invented.** AS spec `C-AS-08 §8.4` ("One ledger entry per successful fetch" + "One ledger entry per failed fetch") and `C-AS-05 §5` ("Sole resolution path — `fetch_secret` is the **only** path through which secrets reach a sandbox") together mandate a per-fetch audit-ledger entry at the `fetch_secret(name, scope, tier)` site. The producer to build is therefore:

> **A workflow-time secret-resolution driver** that calls `fetch_secret(name, scope, tier)` (or the scope-bearing `ProviderSecretResolver.resolve(name, scope, tier)` — `provider_secrets.py:108`/`:185`/`:326`) **within an active workflow step**, and on success/failure invokes the runtime callback `emit_secret_fetch_audit_entry(...)` with a `SecretFetchEvent` carrying the step's `thread_id` + `step_id`.

This is **AS secret-fetch driver path**, NOT scoped-resolver-only: the scoped `ProviderSecretResolver.resolve(...)` returns a `SecretRef` opaque handle and does *not* itself compose the audit event; the audit emission is the runtime callback per the `as_is_wiring.py` docstring ("Downstream tool-call sites invoke this callback at emission time"). The driver = the tool/skill secret-resolution site at dispatch time, which is where `thread_id`/`step_id` are in scope.

**Why this is B1 (extend a live path), NOT the firing-site-absence fork shape of DP-1.** Empirically at HEAD, a step-context `fetch_secret` *site* does **not** yet exist — the **only** production `fetch_secret(...)` caller is CP F5 signing-key resolution (`f5_signing_key_resolution.py:132`, CP→AS, not a workflow-step tool dispatch), and `RuntimeToolDispatcher` does not resolve secrets at dispatch today. The B1 classification turns on the *extension point*, not the current site: the **tool-dispatch path is live** (`RuntimeToolDispatcher.dispatch` exists) and the contract **fully specifies** the hook with no ownership ambiguity — C-AS-05 §5 makes `fetch_secret` the *sole* path secrets reach a sandbox (so a secret-bearing tool *must* resolve via it at dispatch), C-AS-06 §6.2 specifies the allowlist intersection (`secret_allowlist.py:46`), and C-AS-08 §8.4 mandates the per-fetch audit entry. Building the producer is therefore a **spec-mandated extension of an existing path** — a tool declaring `required_secrets` + the dispatcher resolving them with the step's `thread_id`/`step_id` + emitting the audit. **Contrast DP-1**: the model-driven tool-call inner loop is absent *as a primitive* AND who owns it is an open choice (§4.5 / fork DP-1) — that is why HITL forks and secret-fetch does not. (If a future reviewer judges that "secret-resolution-at-dispatch" is itself an undecided ownership choice rather than a determined contract obligation, R-CXA-1 should be reclassified to the DP-1 shape and forked consistently; this brief judges the C-AS-05 sole-path mandate to settle the ownership, so B1 stands.)

### §2.2 Required fields for a non-hollow `SecretFetchEvent`

Per `secret_fetch_audit.py:45-58`, `SecretFetchEvent` is 7-field (frozen, `extra="forbid"`):

| Field | Type | Non-hollow source at a workflow-time fetch |
|---|---|---|
| `secret_name` | `str` | the requested secret name |
| `secret_scope` | `SecretScope` (`secret_fetch.py:37`, single field `name: str`) | the credential-dimension scope at the call site |
| `secret_last_rotated_at` | `str` (ISO-8601 — a *version attribute*, structure-not-content) | the resolver backend's rotation metadata (real value required; a sentinel collapses the secret fingerprint — see §3.5) |
| `actor` | `Actor` (IS schema) | the step's acting identity |
| `timestamp` | `Timestamp` | fetch time |
| `thread_id` | `Identifier` | **the workflow thread** — present only inside a workflow step |
| `step_id` | `Identifier` | **the workflow step** — present only inside a workflow step |

### §2.3 Scope, tier, caller identity, workflow/thread/step identity, rotation metadata

- **Scope**: `SecretScope.name` at the call site (the credential dimension). NB `SecretScope` carries **only** `name` today — there is no tier/caller-identity field on the scope itself.
- **Tier**: `SandboxTier` is resolved at the call site and passed to `fetch_secret(name, scope, tier)` per C-AS-05 §5.1 (the tier is a `fetch`-arg, not a `SecretFetchEvent` field — the event records the *fingerprint*, not the tier). The producer driver must resolve tier per C-AS-10 before fetching.
- **Caller identity**: carried as the event `actor` (the step's acting `Actor`).
- **Workflow/thread/step identity**: `thread_id` + `step_id` from the active step context — **this is why bootstrap fetches cannot produce a non-hollow event** (§3.5).
- **Rotation metadata**: `secret_last_rotated_at` must be a **real** ISO-8601 version attribute from the resolver backend; it feeds `compute_outputs_hash(secret_name, secret_scope, secret_last_rotated_at)` (`secret_fetch_audit.py:94`) → the `response_hash`. A sentinel here makes every fetch of the same name hash-identical regardless of rotation — a hollow fingerprint.

### §2.4 Idempotency semantics

Per `_idempotency_key` (`secret_fetch_audit.py:61`): `sha256("\x00".join(thread_id, step_id, secret_name, secret_scope.name))`. A replay of the same `(thread_id, step_id, secret_name, scope.name)` 4-tuple yields the same key → the IS append returns `IDEMPOTENT_NOOP` (C-IS-07 §7.1 acceptance #4; U-AS-27 AC #5 "duplicate writes no-op"). **Note the key is timestamp-free** — fetch-once-per-(thread,step,name,scope)-forever. This is correct for in-workflow fetches (a step fetches a given secret once); it is *wrong* for bootstrap (one process-lifetime fetch with no thread/step) — see §3.5.

### §2.5 Why `resolve_bootstrap_value(name)` remains excluded unless the contract changes

This is **B2 — already operator-ratified** (`class_1_fork_cxa_1_secret_fetch_audit_bootstrap_ordering.md`, **APPLIED-AS-READING-D / DON'T-WIRE**, 2026-06-01; reaffirmed by `.harness/r-cxa-1-producer-audit-2026-06-08.md`). The bootstrap provider-key construction path calls **name-only** `resolver.resolve_bootstrap_value(ANTHROPIC_KEYRING_NAME)` / `(OPENAI_KEYRING_NAME)` (`lifecycle/providers.py:328`/`:438`; `provider_secrets.py:122`/`:233`/`:344`). It is structurally unable to produce a non-hollow `SecretFetchEvent`:

- **No `thread_id` / `step_id`** — bootstrap fires *before* any workflow exists. `as_is_wiring.py:110-113` already documents that secret-fetch audit entries fire "outside an active workflow context" and leave `procedural_tier_snapshot_ref` `None`-canonical for exactly this reason.
- **No scope / no rotation metadata** — `resolve_bootstrap_value(name)` takes a name only; `secret_scope` + `secret_last_rotated_at` would be sentinels (material — they collapse the fingerprint per §2.3).
- **Timestamp-free idempotency** — a bootstrap fetch has no thread/step, so the 4-tuple key degenerates; fire-once-forever semantics misfit a per-process bootstrap.

Wiring bootstrap → `emit_secret_fetch_audit_entry` is therefore a **hollow seam**. Admitting bootstrap fetches would require amending the `SecretFetchEvent` contract (e.g. Optional `thread_id`/`step_id`, a bootstrap actor class, a non-thread idempotency formula) — a **design-substrate amendment = B3 fork**, explicitly out of scope here per the handoff non-goal ("Do not treat bootstrap provider-key resolution as AS→IS scoped secret-fetch unless the design explicitly amends the event contract"). The faithful disposition is **bootstrap stays excluded; it is not a producer gap**.

### §2.6 Firing-site prose drift (Class 3 informational — carry, do not relocate)

A known spec-prose-vs-plan-body drift exists and is already documented at `as_is_wiring.py:10-21`: the **runtime** spec §12.2 prose describes the producer site as "AS skill-load completion site (skill-discovery emission)"; the **U-AS-27 plan body / C-AS-08 §8.4** implements **per-fetch** secret-fetch audit emission. The wiring *contract* (`StateLedgerEntry` via U-IS-11 append; chain integrity) is identical in both readings. Per `[[spec-prose-plan-body-drift-pattern]]`: land the producer against the **plan body / C-AS-08 §8.4 per-fetch reading**; cite-don't-relocate; the runtime spec §12.2 prose cleanup is a separate Class 3 doc-hygiene arc (non-blocking).

### §2.7 Acceptance criteria for future implementation (R-CXA-1)

1. A production workflow-step path resolves a secret via `fetch_secret(name, scope, tier)` (or scoped `resolve(...)`) **with the step's `thread_id`/`step_id` in scope**.
2. On success it constructs a `SecretFetchEvent` with all 7 fields populated from real call-site context (no sentinels for `secret_scope`/`secret_last_rotated_at`).
3. It invokes `emit_secret_fetch_audit_entry(event)`; the entry appears in `.harness/state.jsonl` with chain integrity intact (verify via C-IS-06 §6).
4. Replay of the same 4-tuple returns `IDEMPOTENT_NOOP` (no duplicate ledger growth).
5. Bootstrap provider-key fetches remain **unwired** (Reading-D preserved).
6. C-AS-05 §5 "sole resolution path" honored — no secret reaches a sandbox by any non-`fetch_secret` path.
7. **The producer site co-emits the `secret.fetch` span alongside the ledger entry** per **C-AS-08 §8.4** ("Span emission alongside ledger entry"); span attributes `secret.name` / `secret.scope` / `secret.backend` / `secret.fail.class` / `secret.cache.tier_overhead_ms` / `secret.policy.access_decision_reason` per **C-AS-15 + ADR-F5 v1.1 §Consequences (c)**; **structure-not-content** (no secret value in span attributes, §5.3 negative-observation invariant).
8. **The failed-fetch path emits a distinct audit record** per **C-AS-08 §8.4** ("one ledger entry per failed fetch") carrying `secret.fail.class` per **C-AS-07**'s 5-class taxonomy. (AC #2 covers only the *success* path.)

> **§8.4 is two-part — coverage-gap fix (review finding B-1/S-1, 2026-06-08).** ACs #1–#6 (prior version) covered only the AS→IS **ledger** half of C-AS-08 §8.4's per-fetch discipline; §8.4 *also* mandates a co-emitted `secret.fetch` **span** (the AS→OD *observability* half) and a *failed-fetch* record carrying `secret.fail.class`. ACs #7–#8 close that gap. **Scoping:** the span fires at the **same producer/fetch site** as the ledger entry ("alongside" per §8.4), so the R-CXA-1 producer emits both — but the span's *attribute schema* lives on the AS-observability surface (C-AS-15 / ADR-F5). Note also that `SecretFetchEvent` (7-field) has **no** `fail.class` field, so the failed-fetch `secret.fail.class` rides the **span** (per AC #7), not the event; if the composer/event model cannot represent a failed-fetch ledger entry, that is an AS-axis contract gap to **surface (not silently drop)**.

### §2.8 Tests required to prove a real producer exists (R-CXA-1)

Beyond the existing composer unit tests (which prove the *composer*, not a *producer*):

- **`test_secret_fetch_producer_fires_at_workflow_step`** — drive a real workflow step through the secret-resolution path; assert one `state.jsonl` entry appears with the step's `thread_id`/`step_id` (NOT a bootstrap/sentinel identity).
- **`test_secret_fetch_event_fields_non_hollow`** — assert `secret_scope.name` + `secret_last_rotated_at` are real (resolver-supplied), not sentinels; assert `response_hash` differs across two secrets with different rotation metadata.
- **`test_secret_fetch_replay_idempotent_noop`** — second fetch of same 4-tuple → `IDEMPOTENT_NOOP`; ledger length unchanged; chain verify passes.
- **`test_bootstrap_fetch_does_not_emit`** — assert the bootstrap provider-key path produces **zero** `SecretFetchEvent` entries (Reading-D guard).
- **`test_secret_fetch_span_co_emitted`** (AC #7 / B-1) — assert a `secret.fetch` span fires **alongside** the ledger entry at the producer site, carrying the C-AS-15/ADR-F5 attribute set; assert **no secret value** appears in any span attribute (structure-not-content).
- **`test_failed_fetch_emits_fail_class`** (AC #8 / S-1) — drive a failing fetch; assert the failed-fetch record fires with `secret.fail.class` per C-AS-07 (on the span per §8.4, since `SecretFetchEvent` has no fail-class field); structure-not-content preserved.

---

## §3. R-CXA-2 — HITL tool-call rewrite producer

**Composer (LANDED + tested, zero production caller):** `emit_hitl_tool_call_rewriting_state_ledger_entry(*, workflow_id, step_id, tool_call_id, semantic_variant_binding_id, rewritten_tool_call: RewrittenToolCall, actor)` → `cp.hitl-tool-call-rewriting` (`hitl_as_tool_call_rewriting.py:249`; runtime wrapper `cp_is_wiring.py:274`).

### §3.1 Where the LLM/tool inner loop exists or must be introduced

**It must be introduced (B3 — fork DP-1).** Empirically at HEAD:

- The pure rewrite algorithm `rewrite_tool_call_to_hitl(...)` exists (`hitl_as_tool_call_rewriting.py:156`) and the runtime registry method `RuntimeHITLPlacementRegistry.rewrite_tool_call(...)` exists with a **real body** (`hitl_placement.py:187` → `:205 return rewrite_tool_call_to_hitl(...)` — it is *not* a NotImplementedError stub).
- But `rewrite_tool_call` has **6 test callers + ZERO production callers** (confirmed at runtime plan v2.39 §0.3 "firing-site-absence" finding + this arc's grep). No production loop iterates **model-emitted tool calls** through the rewrite gate; each workflow "step" is a single dispatch, not an agentic tool-use inner loop.

The producer is the **model-driven tool-call inner loop**: LLM response → for each emitted tool call → build `ProposedAction` (`handoff_context.py`) → evaluate `hitl_required` (U-CP-43 predicate) → `rewrite_tool_call(...)` → (if rewritten) fire the composer + open the gate → dispatch. **Whether this loop is a NEW runtime primitive or an extension of the existing step dispatch is an ownership decision → DP-1.**

### §3.2 How model-emitted tool calls become `ProposedAction`

`rewrite_tool_call_to_hitl(...)` consumes a `proposed_action: ProposedAction` argument (currently `_ = (persona_tier, proposed_action)` — read but not yet load-bearing in the pure algorithm). The producer loop must construct `ProposedAction(action_kind, payload, brief?)` from each model-emitted tool call before invoking the rewrite gate. The exact mapping (tool-call → `ProposedAction`) is part of the inner-loop design surfaced at DP-1.

### §3.3 When `RuntimeHITLPlacementRegistry.rewrite_tool_call(...)` is invoked

Per C-CP-17 §17.2: rewriting fires **before tool dispatch** — "`rewrite` is the last gate before the action surface" (`hitl_as_tool_call_rewriting.py:176-177`). So the inner loop invokes `rewrite_tool_call(...)` after `hitl_required` is computed and immediately before dispatch, per tool call.

### §3.4 Deterministic derivation of `semantic_variant_binding_id` — B2, SETTLED

**Do not re-derive — cite.** Runtime plan **v2.39 §0.3 / §1.2 Reading B** (operator-ratified via AskUserQuestion 2026-05-29, advisor 43rd application; carries forward unchanged through canonical plan v2.42; also recorded at `Project_Workflow_v1_13.md` species-2 entry):

> `semantic_variant_binding_id = rewritten_call.variant.value` — the StrEnum string value of the existing `HITLSemanticVariant` enum returned by `select_variant()` and stored at `RewrittenToolCall.variant` (`hitl_as_tool_call_rewriting.py:131`). **Zero** field-extension on `RewrittenToolCall` / `HITLSemanticVariantBinding` / composer signature; **zero** spec extension. The composer takes `semantic_variant_binding_id: str` opaque; `StrEnum.value` IS a string.

The producer supplies: `tool_call_id` from the source tool-call id (opaque, caller-provided, analogous to `workflow_id`/`step_id`); `semantic_variant_binding_id = rewritten_call.variant.value`; `actor` from step context; `rewritten_tool_call` from the `rewrite_tool_call_to_hitl(...)` return.

*(Minor carry: CP spec §16.5.4 line 71 informal cite reads loosely; v2.39 §1.2 already notes it "could optionally be cite-cleaned" — deferred per FM-2, non-blocking.)*

### §3.5 What counts as a real rewrite decision vs no-op

Per v2.39 Reading B (emission-conditional semantic) + `rewrite_tool_call_to_hitl` control flow:

- **`hitl_required is False`** → original tool call passes through unchanged (`variant=None`, `response_palette=None`); **no rewrite occurred → NO §16.5 emission fires.** This is the no-op.
- **`hitl_required is True`** → variant selected deterministically by `cell_synchrony_class` (`select_variant`); palette = full 4-response or U-CP-48 restricted; **a real rewrite occurred → the composer fires** with `semantic_variant_binding_id = variant.value`.

### §3.6 Idempotency and replay behavior

Per `_hitl_tool_call_rewriting_idempotency_key` (`hitl_as_tool_call_rewriting.py:224`): `sha256(0x1E.join(workflow_id, step_id, tool_call_id, semantic_variant_binding_id, sha256(RewrittenToolCall canonical bytes).hex()))`. Replay of the same rewrite outcome at the same `(workflow_id, step_id, tool_call_id)` → identical key → IS `IDEMPOTENT_NOOP`. `tool_call_id` must be a **stable** id for a given model tool-call so replays dedup (a fresh-uuid-per-attempt would defeat dedup — the inner-loop design must source `tool_call_id` from the model's tool-call id, not mint one).

### §3.7 Acceptance criteria + tests (R-CXA-2 HITL) — gated on DP-1

*(AC #1-#3 gated on DP-1 ratification of the inner-loop firing site.)*

1. A production inner loop iterates model-emitted tool calls and invokes `rewrite_tool_call(...)` per call before dispatch.
2. When `hitl_required`, it fires `emit_hitl_tool_call_rewriting_state_ledger_entry(...)` with `semantic_variant_binding_id = rewritten_call.variant.value`; the `cp.hitl-tool-call-rewriting` entry appears in `state.jsonl` with chain integrity.
3. When `not hitl_required`, **no** entry is emitted (no-op guard).
4. Replay of the same model tool-call (stable `tool_call_id`) → `IDEMPOTENT_NOOP`.

Tests: `test_hitl_rewrite_producer_fires_when_hitl_required` (e2e through the inner loop); `test_hitl_rewrite_producer_noop_when_not_required`; `test_hitl_rewrite_producer_replay_idempotent`; `test_hitl_rewrite_tool_call_id_is_stable_from_model`. (The existing `test_hitl_tool_call_rewriting_state_ledger_emission.py` suite proves the *composer*; these prove a *producer*.)

---

## §4. R-CXA-2 — engine-layer pause/resume producers

**Composers (LANDED + tested, zero production caller):**
- `emit_pause_captured_state_ledger_entry(*, workflow_id, step_id, pause_event_id, pause_snapshot: PauseSnapshot, actor)` → `cp.pause-captured` (`pause_resume_protocol.py:864`; runtime wrapper `cp_is_wiring.py:308`).
- `emit_resume_attempted_state_ledger_entry(*, workflow_id, step_id, resume_event_id, resume_attempt_count, resume_outcome: ResumeOutcome, actor)` → `cp.resume-attempted` (`pause_resume_protocol.py:967`; runtime wrapper `cp_is_wiring.py:340`).

### §4.1 Distinction from the existing workflow-layer `cp.pause-resume-protocol` (the most important fact here)

The harness has **two coexisting pause/resume layers** (CP spec v1.11 §26 NEW NOTE; `pause_resume_protocol_types.py:21-28`):

| Layer | Surface | Type | action_id | Production caller? |
|---|---|---|---|---|
| **Workflow-layer** (C-CP-26) | `PauseResumeProtocol` **class** methods `capture_pause_snapshot` / `attempt_resume` | `PauseSnapshot` / `ResumeResult` | `cp.pause-resume-protocol` (U-CP-76) | **YES** — `workflow_driver.py:582/808/965` |
| **Engine-layer** (C-CP-22) | module **free functions** `capture_pause_snapshot` / `attempt_resume`, gated behind `bind_engine_pause_resume_substrate(...)` | `PauseEvent` / `ResumeOutcome` | `cp.pause-captured` / `cp.resume-attempted` (U-CP-78/79) | **NONE** |

**Do not treat the workflow-driver pause/resume sites as engine-layer producers** (handoff non-goal). Those sites correctly emit the *workflow-layer* `cp.pause-resume-protocol` via `emit_pause_resume_state_ledger_entry` (`workflow_driver.py:582/808/965` → `cp_is_wiring.py:240`). The engine-layer `cp.pause-captured`/`cp.resume-attempted` are a **different architectural primitive at a different layer** with no production producer.

### §4.2 Engine recovery-loop ownership — B3, fork DP-2

The engine-layer free functions (`pause_resume_protocol.py:252`/`:272`) **fail closed** (`EnginePauseResumeSubstrateNotBoundError`) unless an `EnginePauseResumeSubstrate` is bound via `bind_engine_pause_resume_substrate(...)` (`:153`). A provider-free `DeterministicEnginePauseResumeSubstrate` exists (`:171`) but **nothing in production binds it or calls the free functions** (grep at HEAD: only `cp_is_wiring.py` wrappers + tests reference the composers).

The `EngineClass` 5-class (`engine_class.py`) + `ResumptionKind` 5-class (`resumption_kind.py`) taxonomies exist, but production emits only **binary** RESUMPTION on the `SAVE_POINT_CHECKPOINT` engine class (CP-9 retirement note; `workflow_driver.py:725-746`). A full engine recovery loop — one that binds the substrate and drives `capture_pause_snapshot`/`attempt_resume` across crash-recovery / replay / explicit-pause resumption — **does not exist**. Who owns it (a NEW runtime engine-recovery primitive vs. an extension of the workflow driver vs. bounded-residual-defer) is an architecture decision → **DP-2**.

### §4.3 When `capture_pause_snapshot(...)` / `attempt_resume(...)` are invoked as real producers

Gated on DP-2. If DP-2 ratifies a real engine recovery loop, then:
- `capture_pause_snapshot(workflow_id, pause_reason)` fires when the engine captures a recovery pause (crash-recovery / replay-boundary / engine-native pause per `PauseReason`), and the loop then invokes `emit_pause_captured_state_ledger_entry(...)`.
- `attempt_resume(attempt)` fires when the engine attempts recovery resumption, and the loop then invokes `emit_resume_attempted_state_ledger_entry(...)` at **both** success and failure outcomes (the composer docstring + AC require firing on `ABORT_*` outcomes too — failure is a recorded outcome, not a swallowed exception).

### §4.4 Event identity, attempt count, outcome classification — disambiguator derivation is B3, fork DP-3

The composers take disambiguator kwargs **not derivable from the engine-layer types** at HEAD:
- `pause_event_id` — **not** a field on engine-layer `PauseEvent` (`pause_resume_protocol.py:59`).
- `resume_event_id` + `resume_attempt_count` — **not** fields on `ResumeAttempt` (`:76`) or `ResumeOutcome` (`:104`).

This is the open carry from runtime plan v2.39 §0.4(b) ("5 disambiguator surfaces ... `PauseEvent.pause_event_id` + `resume_attempt_count`") and the v2.34 AC #8 risk flag (`class_1_tension_u_rt_35...` line 322: "If absent at HEAD → Class 1 fork per `[[halt-route-split-AC-pattern]]` (do NOT invent fields at runtime axis = X-AL-3)"). **Unlike the HITL `semantic_variant_binding_id`, this was never closed** (HITL closed at v2.39 Reading B; pause/resume remained owed). Where these values come from — recovery-loop-context-supplied (the loop mints a `pause_event_id` and increments a `resume_attempt_count`) vs. type-field extensions vs. CP spec amendment — is **DP-3**. The recommended reading (recovery-loop-context-supplied, mirroring the HITL `tool_call_id` "caller-provided opaque" precedent) is argued in the fork; **this brief does not pick it**.

- **Outcome classification**: `ResumeOutcome.outcome_kind` (`ResumeOutcomeKind`: `RESUME_CLEAN` / `RESUME_AFTER_REVALIDATION` / `ABORT_REVALIDATION_FAILED` / `ABORT_SNAPSHOT_CORRUPTED`) is already a field — usable directly, no derivation gap.

### §4.5 Idempotency and replay behavior

Per `_pause_captured_idempotency_key` (`:833`): `sha256(0x1E.join(workflow_id, step_id, pause_event_id, snapshot_hash, outcome_hash))`. Per `_resume_attempted_idempotency_key` (`:938`): `sha256(0x1E.join(workflow_id, step_id, resume_event_id, resume_attempt_count, outcome_hash))`. Replay dedups iff the producer supplies **stable** `pause_event_id`/`resume_event_id` and the same `resume_attempt_count` — which is exactly why DP-3's derivation must yield stable, replay-safe identities (a fresh uuid per call defeats dedup).

### §4.6 The `pause-captured` type impedance — B3 DEFECT, Class 1 fork

**Surfaced this arc.** `emit_pause_captured_state_ledger_entry` consumes `pause_snapshot: PauseSnapshot` — the **workflow-layer** 8-field type (`pause_resume_protocol_types.py:92`, has `snapshot_hash`, `state_ledger_anchor`). But its own docstring says it "Fires AFTER `capture_pause_snapshot(...)` ... returns the `PauseSnapshot`" referring to the **engine-layer** free function `capture_pause_snapshot(workflow_id, pause_reason) -> PauseEvent` (`:252`) — which returns a 5-field `PauseEvent` (`:59`, has `pause_audit_entry_id`, **no** `snapshot_hash`). **The engine-layer producer cannot feed its output (`PauseEvent`) to the engine-layer composer (which wants `PauseSnapshot`) without a type adaptation that does not exist.** The sibling `emit_resume_attempted_state_ledger_entry` does **not** have this mismatch (it consumes the engine-layer `ResumeOutcome`, which `attempt_resume` actually returns) — the impedance is asymmetric and `pause-captured`-specific.

A composer consuming a type its documented producer does not emit is a **defect, not a choice** → filed as Class 1 fork `class_1_fork_u_cp_78_pause_captured_type_impedance.md`, with three candidate readings (change composer input type to `PauseEvent`; have the engine recovery loop produce a `PauseSnapshot`; or define an adapter). **This brief recommends a reading in the fork but does not resolve it** — ratification drives the fix.

### §4.7 Acceptance criteria + tests (R-CXA-2 engine pause/resume) — gated on DP-2 + DP-3 + Class 1 fork

1. A production engine recovery loop binds the engine substrate and drives `capture_pause_snapshot`/`attempt_resume` at real recovery sites (DP-2).
2. It supplies stable, replay-safe `pause_event_id` / `resume_event_id` / `resume_attempt_count` per DP-3.
3. The `pause-captured` type seam is resolved (Class 1 fork) so the producer can feed real engine output to the composer.
4. `emit_pause_captured_state_ledger_entry` / `emit_resume_attempted_state_ledger_entry` fire; `cp.pause-captured` / `cp.resume-attempted` entries appear with chain integrity; resume-attempted fires on **both** success and `ABORT_*` outcomes.
5. Replay of the same recovery event → `IDEMPOTENT_NOOP`.

Tests: `test_engine_recovery_loop_emits_pause_captured`; `test_engine_recovery_loop_emits_resume_attempted_on_abort`; `test_pause_captured_consumes_real_engine_output` (the type-seam guard); `test_engine_pause_resume_replay_idempotent`. (Existing `test_pause_resume_workflow_layer_state_ledger_emission.py` covers the composers, not a producer loop.)

---

## §5. Decision-rule determination

Per the handoff decision rule:

> - existing contracts sufficient → design brief + impl plan.
> - event schemas / ownership / idempotency / runtime lifecycle must change → design brief + **ADR** + impl plan.
> - PRD only if operator-facing.

**Determination:**

- **No new top-level ADR.** This workspace's ADRs are *foundational* (F1–F5 / D1–D6). The producer decisions here are spec/plan-granularity. The HITL-rewrite-before-dispatch (ADR-D5 §1.3.2 / C-CP-17 §17.2), pause/resume (ADR-D5 §1.11), and EngineClass/ResumptionKind (ADR-D1) primitives are **already design-committed** — what is missing is *runtime-lifecycle wiring + producer-loop ownership*, which is a runtime-spec/plan + fork-doc concern, not a foundational-ADR concern. The workspace's native mechanism for "new H_T primitive / ownership choice surfaced at execution time" is the **Class 1/2 fork doc** (§4.3), which this arc files. (Should ratification of DP-1/DP-2 conclude that the inner loop / engine recovery loop rises to a *foundational* commitment, a fork→ADR escalation is the documented route — but that is a ratification outcome, not a precondition for this brief.)
- **No PRD.** Internal cross-axis runtime architecture; no operator-facing approval/recovery workflow is introduced (the HITL/pause/resume *surfaces* already exist; this arc specs their *producers*).
- **Impl plan/back-flow deferred to post-ratification — now unblocked.** The B3 forks were ratified on 2026-06-08: U-CP-78 Reading A; R-CXA-2 DP-1(c), DP-2(c), and DP-3(a). The next arc may author the concrete implementation/back-flow plan without inventing contracts. R-CXA-1 remains the buildable producer slice; R-CXA-2 remains bounded on future HITL inner-loop / engine recovery-loop authoring, with the U-CP-78 type fix authorized as a future precondition if the engine producer re-opens.

This keeps the arc in clean design-phase posture: **`.harness/**` only**, no `design-substrate/**` edit, no X-AL-3 guard trip, no clearance marker owed (`[[halt-route-split-ac-pattern]]`: partial-land the brief, route the unsettled).

---

## §6. Non-goals compliance (handoff)

| Non-goal | Compliance |
|---|---|
| Do not close R-CXA-1/2 by wiring placeholder calls | ✅ No code wired; both stay OPEN; producers specified-not-built |
| Do not treat workflow-driver pause/resume as engine-layer producers | ✅ §4.1 explicitly separates the two layers; engine-layer pair confirmed unwired |
| Do not treat bootstrap provider-key resolution as AS→IS scoped secret-fetch unless contract amended | ✅ §2.5 preserves ratified Reading-D exclusion; contract amendment routed to fork (not done here) |
| Do not mix runtime impl with design-substrate changes unless arc opens back-flow scope | ✅ `.harness/**` only; zero `design-substrate/**` + zero `harness-*/src/**` edits |

---

## §7. Closeout

- **R-CXA-1** and **R-CXA-2** stay **OPEN** (PROPOSED/PARTIAL, STILL-BOUNDED respectively). Producer gaps are now **SPECIFIED, not implemented**.
- **Forks ratified** (implementation/back-flow still separate):
  - `class_1_fork_u_cp_78_pause_captured_type_impedance.md` — Reading A ratified; implementation still owed before any engine-layer producer can call `cp.pause-captured`.
  - `class_2_fork_r_cxa_2_producer_loop_ownership.md` — DP-1(c) and DP-2(c) bounded-residual defer; DP-3(a) future recovery-loop-context identities.
- **Settled, cited (not re-derived):** HITL `semantic_variant_binding_id = variant.value` (v2.39 Reading B); bootstrap secret-fetch exclusion (Reading-D 2026-06-01).
- **Cross-references (extends, does not duplicate):** `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (CLOSED; firing-site-layer continuation), runtime plan v2.39 §0.3/§0.4, v2.34 AC #8, `r-cxa-1-producer-audit-2026-06-08.md`, `r-cxa-2-producer-audit-2026-06-08.md`.
- **Roadmap/status:** R-CXA-1/R-CXA-2 entry notes updated to point at this brief + ratified forks; dashboard regenerated from source. A terminating `ops: roadmap status refresh` is owed post-merge per §12.2.1.

## §8. See also

- **`r-cxa-2-post-mvp-producer-loop-product-brief.md`** — the post-MVP producer-loop architecture deep-dive (HITL inner loop DP-1(a) + engine recovery loop DP-2(a)/DP-3(a) + U-CP-78 Reading A apply surface + staged impl-plan path + governance/escalation determination).
- `[[r-cxa-seam-wiring-is-producer-discovery]]` · `[[grounding-reveals-claude-closeable-slice-close-honestly]]` · `[[halt-route-split-ac-pattern]]` · `[[spec-prose-plan-body-drift-pattern]]`
- `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (CLOSED parent lineage)
- `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3 (no silent design extension)
