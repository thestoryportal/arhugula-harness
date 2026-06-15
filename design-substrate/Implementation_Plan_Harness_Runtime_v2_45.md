# Implementation Plan — Harness Runtime — v2.45

*Delta over v2.44. v2.45 is the runtime-axis leg of **R-FS-1 — E-plan** — the atomic-unit decomposition of the E sub-program's WAL_SEGMENT (E-2) runtime-homed surfaces (both **impl-against-cleared-spec**, NO spec leg, per `.harness/architect_recommendation_e_engine_fork_vs_impl.md`). TWO NEW units: **U-RT-121** (the hand-rolled WAL segment-log `EnginePauseResumeSubstrate`, extending the proven #475 `JournalEnginePauseResumeSubstrate` per I-6 — no vendored Kafka/WAL); **U-RT-122** (the **R-CXA-2 engine-layer activation** — bind U-RT-121 in the `r_cxa_2_producer_loop_factory` replacing the in-memory `DeterministicEnginePauseResumeSubstrate`, giving `RuntimeEngineRecoveryLoop` its first production driver → `cp.pause-captured`/`cp.resume-attempted` (C-CP-49/50) land → the R-CXA-2 CP→IS engine-layer seam goes LIVE — by-execution e2e). One cross-axis edge (RT→CP, downstream): U-RT-122 → U-CP-95 (the WAL_SEGMENT engine-layer recovery-loop firing branch in the CP driver). The CP-side engine materialization (EVENT_SOURCED_REPLAY U-CP-93 + WAL_SEGMENT resumption U-CP-94 + the firing branch U-CP-95) is at **CP plan v2.34**; the E aggregate cross-axis DAG home is CP plan v2.34 §3.5. **R-CXA-2 activation homes at E-2 (WAL_SEGMENT), NOT E-1** (CP plan v2.34 §6 O-CP-4 / companion §5). E-3 RECONCILER_LOOP is OUT (narrow §7.4 fork at E-spec-3, operator-ratified). Co-published with CP plan v2.34 (U-CP-93/94/95). ZERO spec amendment, X-AL-3-clean. v2.44 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.44 → v2.45)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_44.md` (v2.44 — the R-FS-1 B3-plan runtime leg; 6 NEW units U-RT-115..120 for the smart-HITL gate-composer surfaces).

### §0.2 Revision scope (v2.44 → v2.45)

v2.45 decomposes the **runtime-homed** surfaces of the E sub-program's WAL_SEGMENT engine class (E-2) — **impl-against-cleared-spec** per `.harness/architect_recommendation_e_engine_fork_vs_impl.md` (C-CP-07 §7.4 defers "specific WAL implementation" to impl-discretion; I-6 selects hand-rolled; the U-CP-56 precedent materialized save-point as impl, "no spec bump") — into TWO NEW units. **The keystone homing fact:** the engine recovery loop (`RuntimeEngineRecoveryLoop`, `lifecycle/engine_recovery_loop.py:45`), the #475 `JournalEnginePauseResumeSubstrate` (`lifecycle/journal_pause_resume_substrate.py:123`), and the R-CXA-2 producer factory (`bootstrap/factories/r_cxa_2_producer_loop_factory.py`) are **runtime-homed**; the CP package carries the engine driver / `EngineClass` / consumers / C-CP-49/50 composers + the recovery-loop firing branch (CP plan v2.34 U-CP-93/94/95).

| E surface | Plan home | Rationale |
|---|---|---|
| **WAL segment-log durable substrate** — hand-rolled append-only segment writer + per-segment replay + idempotent consumer state + torn-write detection + fsync (extend #475) | **U-RT-121** (runtime; extends `JournalEnginePauseResumeSubstrate`) | C-CP-07 §7.1 row 5 (WAL-owned) + §7.4 ("specific WAL implementation" deferred to impl-discretion); I-6 hand-roll; satisfies the existing `EnginePauseResumeSubstrate` Protocol |
| **R-CXA-2 engine-layer activation** — bind U-RT-121 in the factory (replace `DeterministicEnginePauseResumeSubstrate` at `r_cxa_2_producer_loop_factory.py:208-214`) + the by-execution go-live e2e | **U-RT-122** (runtime; the factory + the durable proof) | C-CP-49/50 (§16.5.2 composers) + R-CXA-2 (CXA §2.3.2); gives `RuntimeEngineRecoveryLoop` its first production driver (line-181 trigger fired) |
| EVENT_SOURCED_REPLAY materialization (U-CP-93) + WAL_SEGMENT resumption, CP/IS-only (U-CP-94) + recovery-loop firing branch (U-CP-95) | **CP plan v2.34** | engine driver / `EngineClass` / consumers / C-CP-49/50 composers are `harness-cp`; the firing branch consumes `ctx.engine_recovery_loop` duck-typed (no CP→RT import). The Path-(i) `test_u_rt_95` durable e2e is **U-RT-122** below (it needs the durable substrate + firing — relocated from U-CP-94 per Codex 2nd-pass catch) |
| E-3 RECONCILER_LOOP semantics + the narrow §7.4 substrate-deferral reconciliation | **OUT of scope** (E-spec-3, operator-ratified — architect rec §6) | reconciler-loop is the one class §7.4 omits from impl-discretion; its "K8s/etcd" substrate ⊥ I-6 → a narrow spec touch + clearance, separate arc |

No spec amendment; no new contract ID. The WAL_SEGMENT durable-execution semantics are cleared (C-CP-07 §7.1 row 5 + C-CP-08 §8.1 `segment_replay`); U-RT-121 fills the §7.4-deferred substrate slot hand-rolled; U-RT-122 fires the already-cleared C-CP-49/50 composers from a real driver (impl, architect rec §5). X-AL-3-clean.

### §0.3 Sections preserved verbatim from v2.44

| Section | Status at v2.45 |
|---|---|
| §0 (v2.44 change-note) | Superseded by this §0 (historical record preserved at v2.44) |
| §1 Spec inventory | Refreshed: +2 E contract rows (C-CP-07/08 WAL_SEGMENT substrate + C-CP-49/50 R-CXA-2); all prior rows (incl. the B3 §3.8/§14.8.9 rows) PRESERVED VERBATIM |
| §2 — U-RT-01..U-RT-120 (all prior units) | **PRESERVED VERBATIM** from v2.44 + lineage (delta-only-plan-chain convention) |
| §3 Dependency graph | Revised: +§3.1b E delta (U-RT-121/122); all prior edges + acyclicity preserved verbatim |
| §4 Coverage matrix | Revised: +§4.1b (2 E rows); all prior rows preserved verbatim |
| §5 / §6 | Unchanged (no new tri-spec or open item at v2.45); all prior preserved verbatim |

### §0.4 Authority chain — no operator gate

v2.45 absorbs the **cleared** E-2 reading (architect rec §0/§6 — E-1/E-2 impl-against-cleared-spec; operator-set `next_action`=E-plan). No operator decision owed at this plan-layer arc; ZERO X-AL-3 risk (the WAL_SEGMENT semantics are C-CP-07/08-cleared; the §7.4-deferred substrate slot is filled hand-rolled per I-6; firing cleared C-CP-49/50 from a real driver is impl). The ONE genuine operator decision in the E sub-program — the E-3 §7.4 substrate-deferral reconciliation — is OUT (its own E-spec-3 leg). The R-CXA-2-owned-by-E-2 finding is recorded at CP plan v2.34 §6 O-CP-4 (a within-impl re-sequencing, not a fork).

### §0.5 Status posture

`Status: Proposed`. Clearance marker filed at `.harness/clearance/Implementation_Plan_Harness_Runtime-v2_45-cleared-2026-06-15.md`. Sibling co-publication: CP plan v2.34 (U-CP-93/94/95). Companion: `.harness/r-fs-1-e-plan-decomposition.md`.

---

## §1 Spec inventory

PRESERVED VERBATIM from v2.43 §1, **plus**:

| Contract | Version | Status at v2.44 |
|---|---|---|
| **C-RT-04 §3.8** (`HITLAutoApprovePolicy` sub-model + the §14.8.2 step-4c in-`max()` floor-override consumption; the two-bool solo-scoped named-cell shape; the C10 AC-1 audit-wiring + AC-2 EXTERNAL_REVERSIBLE-not-representable) | **runtime spec v1.49 (NEW §3.8)** | **Covered at U-RT-116 (NEW)** (consumes U-CP-91 cross-axis) |
| **§14.8.9** (HITL timeout-degradation dispatch-on-mode; vocab-A `{fail-closed, escalate-secondary-channel, fail-open}`; the 2 granted modes routing through step-4i REJECT + §14.8.8 webhook; `fail-open`-refused-at-all-tiers AC-1; dispatch-not-vacuous AC-3) | **runtime spec v1.50 (NEW §14.8.9)** | **Covered at U-RT-119 (NEW)** (consumes U-CP-92 cross-axis) |
| §14.8.2 step-4c (the `gate_level` composition site — G1-blast producer for the `blast_radius_tier` axis) | runtime spec v1.49 (the in-`max()` consumption site §3.8 describes) | **Covered at U-RT-115 (NEW)** |
| §14.8.2 step-4d (the palette `gate_level=<from 4c>` mandate — G2) | runtime spec (Reading B v1.22) | **Covered at U-RT-117 (NEW)** |
| §14.8.2 step-4f (the `on_hitl_timeout` consult for `degradation_mode_applied` — G4a) | runtime spec v1.50 §14.8.9 (the audit-attribute half, preserved verbatim) | **Covered at U-RT-118 (NEW)** |
| §14.8.2 step-4i + NOTE 6-ii (EDIT replace-not-merge `step.step_payload` — G3) | runtime spec (v1.9 + NOTE 6-ii) | **Covered at U-RT-120 (NEW)** |

**Plus** (E — WAL_SEGMENT runtime surfaces, v2.45; all rows above PRESERVED VERBATIM from v2.44 §1):

| Contract | Version | Status at v2.45 |
|---|---|---|
| C-CP-07 §7.1 row 5 + §7.4 ("specific WAL implementation" deferred) + C-CP-08 §8.1 `segment_replay` + §8.2 row 5 (the WAL_SEGMENT durable-execution substrate semantics) | CP spec v1.2 (cleared; §7/§8 preserved verbatim through the delta chain to head) | **Covered at U-RT-121 (NEW)** (the hand-rolled segment-log substrate; consumes the CP-materialized WAL_SEGMENT class U-CP-94 cross-axis) |
| C-CP-49 / C-CP-50 (§16.5.2 engine-layer pause/resume composers) + R-CXA-2 CP→IS engine-layer producer seam (CXA §2.3.2); CP §16.5.9 invariant 5 | CP spec §16.5 (cleared + built) | **Covered at U-RT-122 (NEW)** (factory bind + go-live e2e; consumes U-CP-95 firing branch cross-axis) |

---

## §2 Atomic-unit decomposition

### §2.1 Preserved-verbatim units

U-RT-01..U-RT-112 — PRESERVED VERBATIM from v2.43 + lineage (delta-only-plan-chain convention). The U-RT-113 + U-RT-114 bodies (the v2.43 B1-plan NEW units) follow immediately below, PRESERVED VERBATIM as prior units (their bodies were the v2.43 `§2.2 NEW units (2)` block; at v2.44 they are prior units and are preserved unchanged).

#### U-RT-113 — `RunStatus.PARTIAL` runtime projection (C-RT-09 §9)

**Scope.** Widen the runtime-facing `RunResult.status` `Literal` to admit `'partial'` and flip the `_CP_TO_RT_STATUS` projection entry from the v1.4 defensive `PARTIAL → 'failed'` placeholder to `PARTIAL → 'partial'`, so a `proceed`-cascade graceful-degradation run (CP `RunStatus.PARTIAL`) surfaces at the public API as `RunResult.status == 'partial'`. One coherent change at the CP→runtime status-projection surface.

**Spec linkage.** C-RT-09 §9 (the `status` `Literal` widen + the `'partial'` graceful-degradation invariant + `failure_cause` stays `None` + no `degraded` field). CP spec v1.32 §25.15.1 (the `proceed` cascade → `RunStatus.PARTIAL` run-level outcome this projects). Runtime §14.18.2 (exit-code mapping — already lists `PARTIAL → 1`; no edit, the unit asserts the existing mapping holds for the now-distinct literal).

**Surfaces affected.** The CP-`RunResult` → runtime-`RunResult` projection map (`_CP_TO_RT_STATUS`) and the `RunResult.status` `Literal` type annotation in the runtime API surface; the CLI exit-code mirror (`_CP_STATUS_TO_EXIT_CODE`, asserted already-correct — already maps `"partial"`).

**Signatures introduced or modified** (transcribed from runtime spec v1.48 §9, NOT redesigned):
- `RunResult.status: Literal['completed', 'drained', 'failed', 'paused', 'partial']` (add `'partial'` — minor type-widen).
- `_CP_TO_RT_STATUS[RunStatus.PARTIAL] = 'partial'` (flip from `'failed'`).

**Depends on.** (none) — the CP `RunStatus.PARTIAL` enum member is code-real (pre-existing, reserved at CP §25.2); this unit is the runtime-side projection only.

**Acceptance criterion (functional).** Given a CP `RunResult(status=RunStatus.PARTIAL, …)`, `_build_run_result` projects `RunResult.status == 'partial'`; `failure_cause is None` (a degraded run did not fail — the existing `status=='failed' ⟹ failure_cause is not None` invariant is unchanged); `terminal_state` carries the partial aggregate; no `degraded` field is added. A `'partial'`-projection unit test asserts the mapping + the invariant. The `pyright`-strict `Literal` narrows cleanly (no `KeyError`, no exhaustiveness gap).

**Acceptance criterion (integration).** Under a `PARALLELIZATION` / fan-out workflow with `cascade_policy = proceed` and ≥1 failed branch (CP plan v2.32 U-CP-85 + a strategy), `api.run(...)` returns `RunResult.status == 'partial'` and the CLI exit code is `1` per §14.18.2 (the cross-axis integration, exercised at B1-impl-N).

**Notes.** Mirrors the v1.45 `'paused'` type-widen exactly (the minor-bump precedent). No new `RunStatus` value (PARTIAL is the CP §25.2 reserved value, now activated by `proceed`).

#### U-RT-114 — branch `AgentRole` dispatch-read — model binding (C-RT-15 §14.5.3)

**Scope.** Make the runtime LLM-dispatch composer read `step_context.agent_role` (the branch `AgentRole` carried on the CP-composed child `StepExecutionContext`, CP plan v2.32 U-CP-81) to index the per-role **model binding** (`RoutingManifest.per_role_bindings`), replacing the hardcoded `_MVP_DEFAULT_AGENT_ROLE` discard — so worker/delegation/handoff branches route per-role models. One coherent change at the dispatch seam. **Model binding only** — the per-role prompt is NOT in scope (resolved once at stage 0 with the default role before branch contexts exist; deferred to B4).

**Spec linkage.** C-RT-15 §14.5.3 (primary — the dispatch-read mechanism, the model-binding-only scope, the per-role-prompt→B4 deferral). CP spec v1.32 §25.14 (the role seam — the CP `StepExecutionContext` carries `AgentRole`, the runtime indexes it). C-CP-01 §1.3 (`RoutingManifest.per_role_bindings` — the per-role model binding indexed).

**Surfaces affected.** The runtime LLM-dispatch composer's role-resolution point (where `_MVP_DEFAULT_AGENT_ROLE` is bound today) — read `step_context.agent_role` for the per-role `RoutingManifest.per_role_bindings` lookup.

**Signatures introduced or modified** (transcribed from runtime spec v1.48 §14.5.3 — NO new signature; a read-substitution): the dispatch composer indexes `RoutingManifest.per_role_bindings[step_context.agent_role]` (fall-through to the default model binding on miss / `"default"` role / empty catalog — byte-identical to v1.47 in that case). No `StepExecutionContext` shape change here (the `agent_role` field is added CP-side at U-CP-81).

**Depends on.** [U-CP-81 (cross-axis: CP) — the branch `StepExecutionContext` carrying the `agent_role` field this unit reads]. (Direction: runtime → CP, matching the `harness-runtime` → `harness-cp` package dependency — downstream, no cycle.)

**Acceptance criterion (functional).** Given a `StepExecutionContext` with `agent_role` set to a role present in `RoutingManifest.per_role_bindings`, the composer dispatches against that role's model binding (not `_MVP_DEFAULT_AGENT_ROLE`'s). Given `agent_role` = `"default"` / absent / an empty catalog, dispatch is byte-identical to v1.47 (fall-through to the manifest default — a non-breaking-default test asserts this). The `SINGLE_THREADED_LINEAR` path (no branch child context) reads the existing default-role path verbatim (regression-safe).

**Acceptance criterion (integration).** Under an `ORCHESTRATOR_WORKERS` workflow (CP plan v2.32 U-CP-88) with per-role model bindings, distinct workers dispatch against distinct per-role models — the worker patterns are non-hollow by per-role model specialization. Verified at B1-impl-N (live e2e where a provider step is involved).

**Notes.** Per-role **prompt** specialization is explicitly OUT of scope (the stage-0 single-prompt resolution per C-CP-29 §29.4 predates the branch context) — deferred to R-FS-1 child-arc B4, per runtime spec §14.5.3.

---

### §2.3 NEW units (6) — R-FS-1 B3-plan (smart-HITL)

#### U-RT-115 — `resolve_step_blast_radius` per-step-kind resolver (G1-blast)

**Scope.** Build a `resolve_step_blast_radius(step, ctx) → BlastRadiusTier` per-step-kind resolver at the composer gate-site (design D-cond.1, materialization-site A1 — gate-site resolution, NOT a `StepEffectiveBinding` field, NOT a CP-contract change), so step-4c can compute a **real** `blast_radius_tier` for the `gate_level()` `max()` instead of the `getattr(binding, "blast_radius_tier", None) → None` fall-back. One coherent change: a pure resolver function + its gate-site call. This is the producer for the `blast_radius` axis the §3.8 in-`max()` consumption (U-RT-116) and the G2 palette-thread (U-RT-117) both require.

**Spec linkage.** Runtime spec v1.49 §3.8 (the in-`max()` consumption site that requires a real `blast_radius_tier`). C-CP-19 §19.1 (the `max(per_tool_gate_level, blast_radius_floor, persona_tier_floor, mcp_server_trust_floor)` composition the resolved value feeds — the `BLAST_RADIUS_GATE_LEVEL_FLOOR` table is the consumer). AS spec C-AS-03 §3.1 (`ToolContract.blast_radius_tier` — the TOOL_STEP source, REQUIRED field). C-CP-12 §12.2 (`compute_child_blast_radius_ceiling` / `_blast_radius_of` at `sub_agent_gate_level_descent.py` — the SUB_AGENT_DISPATCH source, reused). Design §3.2 (the per-step-kind resolution table, semantically well-determined by the existing AS/CP contracts).

**Surfaces affected.** A new resolver function (composer-site or a runtime helper consumed at step-4c) reading `step.step_kind` (CP `workflow_driver_types.WorkflowStep`) + the per-kind source; the step-4c gate-input composition point in `RuntimeHITLGateComposer` (`lifecycle/hitl_gate_composer.py`).

**Signatures introduced or modified** (transcribed from design §3.2 per-step-kind table — NO new contract surface; the values are determined by existing AS/CP contracts):
- `resolve_step_blast_radius(step: WorkflowStep, ctx: HarnessContext) → BlastRadiusTier` with the per-kind table: `INFERENCE_STEP → READ_ONLY`; `TOOL_STEP → ToolContract.blast_radius_tier` (looked up by `tool_id` from the step payload via `ctx.mcp_client_host.tool_registry` / `ctx.tool_contracts`); `SUB_AGENT_DISPATCH → compute_child_blast_radius_ceiling` / `_blast_radius_of(sandbox_tier)` (C-CP-12 §12.2, existing); `DECLARATIVE_STEP / HITL_STEP → READ_ONLY`.

**Depends on.** (none) — a foundational resolver reading existing carriers (`WorkflowStep.step_kind`, `ToolContract.blast_radius_tier`, `compute_child_blast_radius_ceiling`); all sources pre-exist at HEAD.

**Acceptance criterion (functional).** `resolve_step_blast_radius` returns `READ_ONLY` for an INFERENCE_STEP (a provider chat-completion has no external side effect); the looked-up `ToolContract.blast_radius_tier` for a TOOL_STEP (a test with a `LOCAL_MUTATION`-tier tool asserts `LOCAL_MUTATION`); the child ceiling for a SUB_AGENT_DISPATCH (reusing C-CP-12 §12.2, monotonic); `READ_ONLY` for DECLARATIVE/HITL steps. A tool the registry cannot resolve raises (NOT a silent READ_ONLY default — fail-safe; a contrasting-baseline test asserts the raise). The resolver is a pure function (no IO beyond the registry read).

**Acceptance criterion (integration).** With U-RT-116, step-4c composes a real `GateLevelInput(blast_radius_tier=<resolved>, …)`; a solo READ_ONLY inference under the default `HITLAutoApprovePolicy` skips the gate (the smart-HITL headline), while a solo LOCAL_MUTATION step still gates (the `BLAST_RADIUS_GATE_LEVEL_FLOOR[LOCAL_MUTATION]=ASK` backstop). Verified by execution at B3-impl-1.

**Notes.** G1-blast is the producer-discovery half of the keystone (`[[r-cxa-seam-wiring-is-producer-discovery]]`): `blast_radius_tier` has NO per-step carrier at HEAD; it is resolved per step-kind, not looked up. The resolver is impl-against-cleared-spec — the spec's deferred-list leaves the `blast_radius_floor(tool)` lookup to implementation and the per-kind semantics are determined by the existing AS/CP contracts (no new contract minted).

#### U-RT-116 — `HITLAutoApprovePolicy` stage-5 ingestion + in-`max()` floor-override consumption (G1-skip; §3.8 / F-B3-1)

**Scope.** Make the `RuntimeHITLGateComposer` (a) read `config.hitl_auto_approve_policy` at bootstrap **stage-5 construction** and hold it as composer instance state (no C-RT-04 `HarnessContext` field per F-B3-1 §3.1 — the composer does not read `ctx.<field>` at dispatch), and (b) at step-4c, **when `binding.persona_tier == SOLO_DEVELOPER`**, lower the matching §19.1 floor cell to `AUTO` per the policy **before** `gate_level()` composes the `max()` (the in-`max()` floor-value reconfiguration, Reading C — NOT a post-`max()` bypass). This is the unit that makes the gate genuinely conditional (the "smart HITL" headline). The lowered floor reaches `gate_level()` via the U-CP-91 `GateLevelInput` carrier-shape.

**Spec linkage.** Runtime spec v1.49 §3.8 (PRIMARY — the `HITLAutoApprovePolicy` sub-model + the §14.8.2 step-4c in-`max()` consumption + the two-bool solo-scoped named-cell semantics + the `max()` arithmetic table + AC-1/AC-2). `.harness/class_1_fork_b3_1_hitl_auto_approve_policy_field.md` (F-B3-1 — the operator-ratified READ_ONLY-auto-ON default + the C-RT-03-only carrier-home + the solo-scoping). C-CP-19 §19.1 (the `max()` composition + the all-ASK `PERSONA_TIER_GATE_LEVEL_FLOOR` the override lowers). CP plan v2.33 U-CP-91 (the `GateLevelInput` floor-override carrier-shape this consumes, cross-axis).

**Surfaces affected.** The composer's stage-5 construction (ingest `config.hitl_auto_approve_policy`); the step-4c gate-input composition (apply the solo-scoped floor-lowering before `gate_level()`); the §20.1 audit-attribute composition for a policy-applied skip (AC-1).

**Signatures introduced or modified** (transcribed from §3.8 — NO new spec field beyond the cleared `HITLAutoApprovePolicy`): the composer ctor/factory ingests `config.hitl_auto_approve_policy: HITLAutoApprovePolicy`; at step-4c, when `persona_tier == SOLO_DEVELOPER` and the policy knob is set, the matching floor cell (`persona_tier_floor[SOLO]` when `solo_persona_floor_auto`; `blast_radius_floor[LOCAL_MUTATION]` when `solo_local_mutation_floor_auto`) is lowered to `AUTO` and threaded into `gate_level()` via the U-CP-91 carrier. EXTERNAL_REVERSIBLE / EXTERNAL_IRREVERSIBLE are NOT representable (no field expresses them — AC-2).

**Depends on.** [U-RT-115 — the real `blast_radius_tier` the LOCAL_MUTATION-cell override and the `max()` evaluate against], [U-CP-91 (cross-axis: CP) — the `GateLevelInput` floor-override carrier-shape the lowered floor threads through]. (Direction: runtime → CP, downstream package direction — no cycle.)

**Acceptance criterion (functional).** At `persona_tier == SOLO_DEVELOPER` with the default `HITLAutoApprovePolicy()` (`solo_persona_floor_auto=True`, `solo_local_mutation_floor_auto=False`): a READ_ONLY step composes `gate_level == AUTO` → `hitl_required == False` → **skip** (the §3.8 arithmetic table row 1); a LOCAL_MUTATION step composes `ASK` → gate (row 2, opt-in OFF); flipping `solo_local_mutation_floor_auto=True` makes LOCAL_MUTATION `AUTO` → skip; EXTERNAL_REVERSIBLE / EXTERNAL_IRREVERSIBLE stay `ASK` → gate (rows 3/4, hard-stop). At `team-binding` / `multi-tenant-compliance` the policy knobs do NOT apply (solo-scoped) — the gate composes the unchanged all-ASK floor (a regression test asserts no skip at non-solo). A `deny`-tier tool or untrusted MCP server raises the gate regardless of the policy (the policy lowers only the two named cells; `per_tool`/`mcp_trust` are never overridden).

**Acceptance criterion (integration — AC-1 C10 audit-wiring guard, carried from §3.8 / F-B3-1 §5).** Each policy-applied floor-lowering (each skip the policy causes) emits a **non-vacuous** §20.1 audit-ledger entry — verified **by execution** (exercise the actual skip path, confirm the populated entry lands; BODY-read not docstring; a green call-site unit test is INSUFFICIENT per `[[built-but-vacuous-reground-ledger-asis]]`). **The skip MUST NOT go live before this is verified wired.** (AC-2 C10 spec-asymmetry: a contrasting-baseline test shows EXTERNAL_REVERSIBLE solo-override is not representable — the §2.4 asymmetry resolved structurally, not silently widened.)

**Notes.** This unit delivers the B3 headline (conditional skip) WITHOUT G2c — the deny-row narrowing (U-RT-117's payoff) is a separate, inert-until-G2c-lands surface (§6 of CP plan v2.33). The override is an in-`max()` floor reconfiguration (Reading C); a post-`max()` bypass (Reading D) is rejected at design §3.3 and structurally not representable by the cleared two-bool field.

#### U-RT-117 — compute `gate_level` once + thread the real value into step-4d palette (G2; D-palette)

**Scope.** Compute the `GateLevelComputation` **once** at step-4c and thread `computed_gate_level` into BOTH the `hitl_required` bool AND `compute_effective_palette` at step-4d — replacing the `_compute_effective_palette_tolerant` hardcoded `gate_level = GateLevel.ASK` (`lifecycle/hitl_gate_composer.py:406`) with the real value from 4c, and removing the redundant double-computation. One coherent structural change at the step-4c→4d palette seam. (`cross_trust_state=NONE` at wrap-time is PRESERVED — spec-correct per §14.8.2 line 3353 / G2b: cross-trust applies only at the §14.15 mid-step re-entry, not knowable pre-dispatch.)

**Spec linkage.** Runtime spec §14.8.2 step-4d (Reading B v1.22 — MANDATES `gate_level=<from 4c>` into `compute_effective_palette`). Runtime spec §14.8.2 step-4c (the `gate_level()` computation whose result is threaded). C-CP-19 §19.4 (the `hitl_required` predicate the same `computed_gate_level` feeds). Design §4 (D-palette — the compute-once structural cleanup).

**Surfaces affected.** `_evaluate_hitl_required_tolerant` (which computes `gate_level` for the bool then discards it) + `_compute_effective_palette_tolerant` (which re-hardcodes ASK) → a single step-4c `GateLevelComputation` threaded to both, in `RuntimeHITLGateComposer`.

**Signatures introduced or modified** (transcribed from §14.8.2 step-4d — NO new signature; a thread-the-real-value substitution): `compute_effective_palette(gate_level=<computed_gate_level from 4c>, cross_trust_state=NONE, validator_escalation_brief=None)` — the `gate_level` arg becomes the real 4c value; `cross_trust_state=NONE` + `validator_escalation_brief=None` preserved (wrap-time spec-correct).

**Depends on.** [U-RT-115 — the real `blast_radius_tier` axis], [U-RT-116 — the step-4c `GateLevelComputation` (with the §3.8 floor-override applied) this threads]. (Both runtime-internal; no cross-axis edge.)

**Acceptance criterion (functional).** Step-4d's `compute_effective_palette` receives the real `computed_gate_level` from step-4c (a test asserts the threaded value equals the 4c result, NOT the ASK sentinel). The `gate_level` is computed exactly once per gate evaluation (a test asserts no double `gate_level()` call). For a `gate_level == DENY` input, `compute_effective_palette` returns the §19.4 deny-row narrowing `{REJECT, RESPOND}`; for `ASK`/`AUTO` it returns the full palette (unchanged wrap-time behavior). **Reachability note:** at HEAD the wrap-time `gate_level ∈ {AUTO, ASK}` only (persona + blast top at ASK; `per_tool` defaults AUTO until the G2c carrier lands), so the deny-row narrowing is **behaviorally inert-but-harmless** in production until G2c (O-CP-3) lands — this unit threads the real value correctly; the DENY path is exercised by a synthetic `per_tool_gate_level=DENY` unit test (not yet reachable through the production composer).

**Acceptance criterion (integration).** With U-RT-116, the threaded `gate_level` is the floor-override-adjusted value (a solo READ_ONLY skip composes `AUTO` → palette is moot since `hitl_required==False`). The compute-once removes the redundant double-computation without changing observable behavior at `ASK`/`AUTO` (regression-safe).

**Notes.** G2 (this unit) + G2c (the `per_tool_gate_level` producer, O-CP-3 registered) were scoped as "ship together" in the design §4.1 because G2's deny-row payoff is inert without G2c. **Justified divergence (B3-plan):** G2c owes an AS-spec reconciliation whose impl-vs-fork class belongs to a future AS-leg gate (B3-spec skipped the AS leg — §6 O-CP-3); rather than block the cleared G2 structural cleanup behind that gate, U-RT-117 lands G2 as cleared impl (the deny-row inert-but-harmless per the §4.1 arithmetic — no harm, since `gate_level` never reaches DENY in production until G2c). The forbidden move (silently impl'ing the G2c AS carrier) is NOT taken — G2c is registered, not built. This unbundling is X-AL-3-clean and surfaced to the operator.

#### U-RT-118 — timeout `degradation_mode_applied` attribute wiring (G4a)

**Scope.** Replace the timeout path's literal `degradation_mode_applied = "default"` (`lifecycle/hitl_gate_composer.py:1071`) with the value from the `harness_cp.hitl_timeout_degradation.on_hitl_timeout` consult, and derive the `audit.policy.*` value at the partial-audit composition. Thin: `on_hitl_timeout(invocation, persona_tier)` IGNORES its `invocation` arg (`hitl_timeout_degradation.py:166` `_ = invocation`) — it is persona_tier-only, and `persona_tier` is on the production binding — so this is pure attribute wiring, no `HITLInvocation` construction needed.

**Spec linkage.** Runtime spec §14.8.2 step-4f (MANDATES the `degradation_mode_applied` value come from the per-persona-tier `harness_cp.hitl_timeout_degradation` consult + the `audit.policy.*` namespace at audit composition). Runtime spec v1.50 §14.8.9 (the G4a audit-attribute half, "preserved verbatim" — this unit lands the attribute; U-RT-119 lands the dispatch). C-CP-21 §21.8 (the per-persona-tier degradation-mode table the consult resolves; the value is the reconciled vocab-A from U-CP-92). Design §6.1 (G4a-thin).

**Surfaces affected.** The composer's `hitl.invocation.timed_out` span attribute set (`degradation_mode_applied`) + the partial-audit `audit.policy.*` composition, in `RuntimeHITLGateComposer`.

**Signatures introduced or modified** (transcribed from §14.8.2 step-4f — NO new signature): `degradation_mode_applied = on_hitl_timeout(_, binding.persona_tier).value` (the resolved `TimeoutDegradationKind`, post-U-CP-92-reconciliation = vocab-A); the `audit.policy.*` attribute derived from the same value.

**Depends on.** (none) — `on_hitl_timeout` is persona_tier-only and `persona_tier` is on the binding; the consult exists at HEAD. (The value's vocabulary correctness depends on U-CP-92, but the attribute-wiring mechanism does not — see Notes; sequenced before U-CP-92 lands the reconciled enum, this unit emits the current enum value; after reconciliation it emits vocab-A automatically. The cleaner sequencing per design §8.3 lands U-CP-92 first within B3-impl-2 — see §3.)

**Acceptance criterion (functional).** The timeout path's `degradation_mode_applied` attribute carries the `on_hitl_timeout(_, binding.persona_tier)` result (a test asserts the attribute equals the table value for the binding's persona tier, NOT the literal `"default"`). The `audit.policy.*` value is derived from the same consult (non-vacuous — a populated value, BODY-read).

**Acceptance criterion (integration).** Under the reconciled vocab-A enum (U-CP-92), a solo timeout emits `degradation_mode_applied == "fail-closed"`; a team timeout emits `"escalate-secondary-channel"`; a multi timeout emits `"fail-closed"` (NOT `abort-workflow` — the U-CP-92 table fix). Verified by execution at B3-impl-2.

**Notes.** G4a is the attribute half of OQ-6; U-RT-119 is the control-flow (dispatch) half. The two compose: G4a sets the attribute; G4b dispatches on the same resolved mode.

#### U-RT-119 — timeout-degradation dispatch-on-mode (§14.8.9; G4b / F-B3-2)

**Scope.** Replace the timeout path's unconditional `raise HITLGateTimeoutError` (`lifecycle/hitl_gate_composer.py:1084`) with **dispatch on the consulted mode** (`mode = on_hitl_timeout(invocation, binding.persona_tier)`, vocab-A), routing each GRANTED mode through a disposition surface that already exists at §14.8.2 step-4i: `fail-closed` → the step-4i REJECT path (raise `HITLGateRejectedError` → `RT-FAIL-HITL-GATE-REJECTED`); `escalate-secondary-channel` → the already-built §14.8.8 durable-async webhook surface (pause/await, NOT failed); `fail-open` → NOT a granted mode (no dispatch path; refused). One coherent control-flow change at the composer timeout path.

**Spec linkage.** Runtime spec v1.50 §14.8.9 (PRIMARY — the dispatch-on-mode contract; the per-mode disposition table; the `fail-open`-refused-at-all-tiers AC-1; the vocabulary-reconciliation AC-2; the dispatch-not-vacuous per-mode-e2e AC-3). `.harness/class_1_fork_b3_2_timeout_degradation_vocabulary_drift.md` (F-B3-2 — operator-ratified reconcile-code→vocab-A; the corrected dispatch-on-mode scope). C-CP-21 §21.8 (the canonical per-persona-tier mode table — solo→fail-closed; team→escalate-secondary-channel/fail-closed; multi→fail-closed+alerting). ADR-D5 §1.6 (foundational — the same table). §14.8.8 (`WebhookDeliveryComposer` C-RT-20 §14.10.1 + C-RT-26 §14.16 + the `pause_requested_flag` / `PauseResumeProtocol` cycle — the escalate-secondary-channel surface). §14.8.2 step-4i (the REJECT path fail-closed routes through). CP plan v2.33 U-CP-92 (the reconciled vocab-A enum this dispatches on, cross-axis).

**Surfaces affected.** The composer's `AskUserQuestionTimeoutError` branch (the unconditional raise → dispatch-on-mode); the routing into the step-4i REJECT path (fail-closed) + the §14.8.8 webhook surface (escalate-secondary-channel), in `RuntimeHITLGateComposer`.

**Signatures introduced or modified** (transcribed from §14.8.9 dispatch table — NO new contract; routes through existing surfaces): after the G4a attribute set, `mode = on_hitl_timeout(invocation, binding.persona_tier)` (vocab-A from U-CP-92); `if mode == fail-closed:` → step-4i REJECT (`HITLGateRejectedError` → `RT-FAIL-HITL-GATE-REJECTED`; residual hard-timeout with no resolvable policy keeps `RT-FAIL-HITL-GATE-TIMEOUT`); `elif mode == escalate-secondary-channel:` → §14.8.8 webhook delivery + pause/await (degrades to fail-closed when `ctx.webhook_delivery_composer`/`ctx.pause_resume_protocol` unbound — the safe fallback per §14.8.9 deferred-list); `fail-open` is unreachable (refused at config/bootstrap per AC-1, never dispatched).

**Depends on.** [U-RT-118 — the G4a attribute (set before dispatch, "preserved verbatim" per §14.8.9)], [U-CP-92 (cross-axis: CP) — the reconciled vocab-A `TimeoutDegradationKind` enum + table this dispatches on; dispatching on the un-reconciled vocab-B would deepen the drift per F-B3-2 §2.4]. (Direction: runtime → CP, downstream — no cycle.)

**Acceptance criterion (functional — AC-3 dispatch-not-vacuous).** Per-mode by execution (NOT a green call-site unit test, per `[[built-but-vacuous-reground-ledger-asis]]`): a `fail-closed` timeout routes through step-4i REJECT (the step fails as rejected — `RT-FAIL-HITL-GATE-REJECTED`, NOT a raw `RT-FAIL-HITL-GATE-TIMEOUT`); an `escalate-secondary-channel` timeout delivers the gate to the §14.8.8 webhook and the workflow pauses (NOT failed); when the webhook/pause surfaces are unbound, `escalate-secondary-channel` degrades to `fail-closed` (safe fallback). The unconditional raise no longer occurs for a resolvable mode.

**Acceptance criterion (integration — AC-1 fail-open refused at ALL tiers, C10 + X-AL-3).** A deployment configuring `fail-open` at ANY tier is refused at config/bootstrap (detect-then-refuse; raises a typed config error), NEVER silently honored at the timeout path. A contrasting-baseline test shows the refusal at multi (the explicit ADR/CP prohibition) AND at solo/team (not-yet-granted — a runtime extension beyond the cleared authorities). Mirrors the F-B3-1 register-don't-extend / multi structural-foreclosure. (The refusal home is U-CP-92's reconciled-enum + bootstrap-validation — see U-CP-92 AC; this unit asserts the dispatch path never reaches a `fail-open` branch.)

**Notes.** The design §6.2 vocab-B `ABORT_WORKFLOW` row DISAPPEARS (no vocab-A equivalent) and `ESCALATE_TO_REVIEW_BOARD`'s heavy "review-board re-invocation" dissolves into the already-built §14.8.8 webhook secondary-channel path — the corrected F-B3-2 scope is SMALLER. This unit + U-CP-92 close OQ-6's producer-gate (the composer timeout path IS the wall-clock-wait orchestrator OQ-6's confirm-defer was gated on, per design §8.3).

#### U-RT-120 — EDIT replace-not-merge (G3; D-edit)

**Scope.** Replace the step-4i `EDIT` branch's `pass` (`lifecycle/hitl_gate_composer.py:1139`) with the replace-not-merge of `step.step_payload` by `gate_result.edited_proposal`, per §14.8.2 step-4i + NOTE 6-ii ("MUST replace-not-merge"; consumers MUST treat `gate_result.edited_proposal` as authoritative replacement). The `WorkflowStep` is frozen Pydantic, so the replacement constructs a replacement step (`step.model_copy(update={"step_payload": <edited>})`). One coherent change at the step-4i EDIT branch.

**Spec linkage.** Runtime spec §14.8.2 step-4i (the edited proposal replaces `step.step_payload`). Runtime spec §14.8.7 NOTE 6-ii (v1.9 implementations MUST replace-not-merge; `gate_result.edited_proposal` is authoritative replacement; richer mutation — field-level patches, type-aware merging — deferred). Design §5 (D-edit — the carrier-drift framing + the D-edit.A elicitation-collapses-to-IMPL / D-edit.B sub-fork discriminator). C-CP-13 `HITLGateResult.edited_proposal: Mapping[str, Any] | None` (`hitl_placement.py:197` — the CP-canonical structured carrier). Runtime `AskUserQuestionResult.edited_proposal: str | None` (`ask_user_question_surface.py` — the runtime ask-surface carrier the composer consumes today).

**Surfaces affected.** The step-4i `EDIT` branch in `RuntimeHITLGateComposer` (the `pass` → replace-not-merge); the `WorkflowStep` replacement construction (`model_copy`).

**Signatures introduced or modified** (transcribed from step-4i + NOTE 6-ii — NO new contract): `step = step.model_copy(update={"step_payload": <edited_proposal>})` at the EDIT branch; the inner dispatcher reads the replaced step. **Carrier-drift discriminator (design §5 / D-edit):** the runtime ask-surface result is `AskUserQuestionResult.edited_proposal: str` but `WorkflowStep.step_payload` is `Mapping[str, Any]` and the CP-canonical `HITLGateResult.edited_proposal` is `Mapping`. **B3-impl-3 resolves which reading by checking whether the §14.8.3 v1.12 structured-elicitation surface (`ctx.elicit(message, schema)`) is wired:** D-edit.A (structured `Mapping → Mapping` replacement = plain IMPL, sub-fork collapses, carrier drift healed) if reachable; else D-edit.B (the `str → Mapping` replacement is genuinely under-specified → file `class_*_fork_hitl_edit_carrier_drift_str_vs_mapping.md` routed to a follow-on workflow-mutation-discipline arc per NOTE 6-ii's own deferral). The core (replace-not-merge) is IMPL either way; the sub-fork is owed ONLY under D-edit.B.

**Depends on.** (none) — the EDIT branch + the `WorkflowStep` carrier + both `edited_proposal` carriers pre-exist at HEAD; the replacement is a local branch change.

**Acceptance criterion (functional).** On an `EDIT` response, the inner dispatcher reads a `step.step_payload` equal to `gate_result.edited_proposal` (replace, NOT merge — a test asserts the prior payload fields are GONE, not union-merged, per NOTE 6-ii). The `WorkflowStep` replacement is a `model_copy` (frozen-safe). The `APPROVE` / `RESPOND` / `REJECT` branches are unchanged (regression-safe).

**Acceptance criterion (integration).** Under D-edit.A (structured-elicitation wired), the `Mapping → Mapping` replacement is verbatim and the runtime↔CP carrier drift is healed (a test asserts the replaced payload is the structured edited proposal). Under D-edit.B, the sub-fork is filed and the `str`-case replacement is honored per the cleared mandate without silently absorbing the drift (`[[halt-route-split-ac-pattern]]`). B3-impl-3 records which reading applies.

**Notes.** G3 is the only B3-impl-3 unit (sequenced after B3-impl-1/2 per design §8.3). The sub-fork (D-edit.B) is the only conditional fork in this delta — and it is conditional on a HEAD-state check the executor makes, NOT a planner decision.

### §2.4 NEW units (2) — R-FS-1 E-plan (WAL_SEGMENT runtime surfaces, E-2)

#### U-RT-121 — Hand-rolled WAL segment-log `EnginePauseResumeSubstrate` (extend #475 Journal)

**Scope.** Hand-roll a durable **WAL segment-log** `EnginePauseResumeSubstrate` for the WAL_SEGMENT engine class (E-2), per I-6 (no vendored Kafka/WAL). Extend the proven #475 `JournalEnginePauseResumeSubstrate` (`harness-runtime/.../lifecycle/journal_pause_resume_substrate.py:123` — a real durable filesystem-journal substrate, append-JSONL / read-latest, satisfying the `EnginePauseResumeSubstrate` Protocol) into a segment-log writer: append-only segment records + per-segment replay + idempotent per-segment consumer state + torn-write / partial-segment detection (checksum or length-prefix per segment — a half-written segment is discarded on replay) + fsync durability ordering (write-ahead: a segment is durable only after fsync). Implements the existing `EnginePauseResumeSubstrate` Protocol (`pause_resume_protocol.py:123-135`: `capture_pause_snapshot` / `attempt_resume`) so it is a drop-in for `RuntimeEngineRecoveryLoop`. PathClass placement: the on-disk segment log maps to `STATE_LEDGER` (an existing closed `PathClass` member — IS-AL-1-clean; no IS extension); IF a substrate genuinely cannot map honestly, the conditional F-E-IS sub-fork surfaces (resolves design OQ-3).

**Spec linkage.** C-CP-07 §7.1 row 5 ("WAL-segment: lifecycle = Harness; append-only segment log with per-segment resume; per-segment harness-owned lease") + §7.4 ("specific WAL implementation at WAL-segment class" deferred to impl-discretion). C-CP-08 §8.1 `segment_replay` + §8.2 row 5 (per-segment ledger entries join F2 on `idempotency_key`). `.harness/r-fs-1-e-engine-classes-design-v1.md` §4.2 (extend #475 via a REAL driver — the line-181-respecting use). `journal_pause_resume_substrate.py:123` (#475, the extension base). `pause_resume_protocol.py:123-135` (the Protocol). `path_class_registry.py:31-37` (the closed 4-class `PathClass` enum; `STATE_LEDGER`). Research grounding: WAL torn-write + fsync hazards (`Pattern_Reference_Catalog_v1.0.md` WAL cluster; cluster-4).

**Surfaces affected.** A new `harness_runtime.lifecycle.*` segment-log `EnginePauseResumeSubstrate` (extending / alongside `JournalEnginePauseResumeSubstrate`). No new contract; implements the existing Protocol.

**Signatures introduced or modified** (impl — implements the existing Protocol, NO new contract): a `WALSegmentEnginePauseResumeSubstrate` (or a segment-log extension of `JournalEnginePauseResumeSubstrate`) with `capture_pause_snapshot(workflow_id, pause_reason) -> PauseEvent` (append a segment) + `attempt_resume(attempt) -> ResumeOutcome` (replay from the last durable segment; per-segment dedup), plus the injected providers mirroring #475 (`state_summary_provider` required; optional `diff_provider` / `revalidation_succeeded` / pause/resume audit-id providers).

**Depends on.** (none) — implements the existing `EnginePauseResumeSubstrate` Protocol (at HEAD); extends the landed #475 substrate. Composes downstream with U-CP-94 (the materialized WAL_SEGMENT class) + U-RT-122 (the factory bind).

**Acceptance criterion (functional).** `capture_pause_snapshot` appends a durable segment; `attempt_resume` replays from the last durably-written segment and classifies the outcome (clean / revalidated / abort), per-segment dedup not double-applying. **Torn-write detection by execution:** a segment half-written then truncated (simulated crash mid-write) is detected (checksum/length-prefix mismatch) and discarded on replay — a contrasting-baseline test shows a corrupt segment does NOT corrupt the replay (fail-closed). **Durable-across-restart by execution:** a fresh substrate instance over the same segment directory resumes a pause captured by a prior instance (the #475 durability property, extended per-segment).

**Acceptance criterion (integration).** Bound into the R-CXA-2 factory by U-RT-122 (cross-axis); fires through `RuntimeEngineRecoveryLoop` (U-CP-95 firing branch) → C-CP-49/50. Verified by execution at E-impl-2.

**Notes.** This is the line-181-respecting use of #475 (`[[r-cxa-seam-wiring-is-producer-discovery]]`): the substrate is bound via a REAL driver that fires it (the WAL_SEGMENT engine), NOT the cosmetic factory-swap anti-pattern (binding #475 with no firing driver — explicitly foreclosed by `r-cl-p2…` + the class-2 fork + design §0). Hand-rolled per I-6 (no vendored Kafka/WAL framework).

#### U-RT-122 — R-CXA-2 engine-layer activation: bind the durable substrate in the factory + go-live e2e

**Scope.** Activate the **R-CXA-2 CP→IS engine-layer seam in production** for WAL_SEGMENT: replace the in-memory `DeterministicEnginePauseResumeSubstrate` bound at `r_cxa_2_producer_loop_factory.py:208-214` (`materialize_r_cxa_2_producer_loop_stage`) with the durable U-RT-121 segment-log substrate, so `ctx.engine_recovery_loop` (the `RuntimeEngineRecoveryLoop` at `engine_recovery_loop.py:45`) fires against a REAL durable store; then prove, by execution, that the full chain — driver WAL_SEGMENT pause-trigger (U-CP-95 firing branch) → `RuntimeEngineRecoveryLoop.capture_pause`/`.attempt_resume` → `emit_pause_captured_state_ledger_entry` (C-CP-49) / `emit_resume_attempted_state_ledger_entry` (C-CP-50) → the F2 state-ledger — lands `cp.pause-captured` / `cp.resume-attempted` entries. This is the **Unit-B RT-half** + the go-live proof; it gives `RuntimeEngineRecoveryLoop` its first production driver and brings R-CXA-2 (a ratified bounded-residual) LIVE. **This go-live e2e IS the Path-(i) `test_u_rt_95` materialization** (relocated here from U-CP-94 — CP plan v2.34 §6 O-CP-4 + Codex pre-merge catch — because it needs the durable U-RT-121 substrate + the U-CP-95 firing branch, which U-CP-94 `(none)` cannot depend on): it authors the currently-**vacuous** `test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path` body (`harness-runtime/tests/integration/…py:368-375`, today only `_ = patched_runtime, tmp_path` — no `execute_workflow` call, no assertions) into the real `execute_workflow` paused→resume cycle, un-skips it (`:347`), corrects the skip-reason, and flips the Path-(i) fork (`.harness/class_1_fork_path_i_durable_async_engine_class_materialization.md`) CLOSED-DEFERRED → CLOSED-BUILT. Un-skipping the vacuous body ALONE would be a false green (`[[test-bypass-as-runtime-truth-pattern]]`).

**Spec linkage.** C-CP-49 / C-CP-50 (= U-CP-49 / U-CP-50, the §16.5.2 composers; `pause_resume_protocol.py:856/:951`). CXA §2.3.2 R-CXA-2 (CP→IS engine-layer producer seam). CP spec §16.5.9 invariant 5 (ZERO `CPAuditLedgerEntry` greenfield — the engine layer emits state-ledger entries with distinct `cp.pause-captured`/`cp.resume-attempted` action_ids vs the workflow-layer `cp.pause-resume-protocol`). `r_cxa_2_producer_loop_factory.py:208-214` (the bind site). `engine_recovery_loop.py:45-104`. `.harness/r-fs-1-e-engine-classes-design-v1.md` §0/§1.2/§6.3. `.harness/r-fs-1-e-plan-decomposition.md` §5 + CP plan v2.34 §6 O-CP-4 (R-CXA-2 owned by E-2). `post-phase-8-forward-register.md` line 181 (the re-open trigger — "a real … WAL-segment … recovery loop lands" — now fired).

**Surfaces affected.** `harness_runtime.bootstrap.factories.r_cxa_2_producer_loop_factory` — the `materialize_r_cxa_2_producer_loop_stage` engine-recovery-loop substrate binding (`:208-214`, `DeterministicEnginePauseResumeSubstrate` → the durable U-RT-121 substrate, for the WAL_SEGMENT deployment). The R-CXA-2 / engine-recovery fork docs + the relevant substitution rows (R-CXA-2 bounded-residual → LIVE). `harness-runtime/tests/integration/test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py` (materialize the vacuous `:368-375` body into a real e2e + un-skip `:347` + skip-reason correction). `.harness/class_1_fork_path_i_durable_async_engine_class_materialization.md` (Path-(i) status flip CLOSED-DEFERRED → CLOSED-BUILT).

**Signatures introduced or modified** (impl — NO new contract): the factory's `engine_recovery_loop = RuntimeEngineRecoveryLoop(wiring=…, substrate=<durable U-RT-121 segment-log substrate>, actor=…)` (replacing the Deterministic substrate) for the WAL_SEGMENT path. No new public type.

**Depends on.** [U-RT-121 (the durable substrate), U-CP-95 (cross-axis: CP — the firing branch)].

**Acceptance criterion (functional / go-live, by execution — NOT grep).** An e2e drives a WAL_SEGMENT workflow through a pause/resume cycle and asserts: `cp.pause-captured` (C-CP-49) + `cp.resume-attempted` (C-CP-50) state-ledger entries LAND with the correct shape against the **durable** segment-log substrate; their `action_id`s are the engine-layer ones (distinct from the workflow-layer `cp.pause-resume-protocol`); ZERO `CPAuditLedgerEntry` greenfield (CP §16.5.9 invariant 5). The recovery loop's `.capture_pause`/`.attempt_resume` now have a **production caller** (no longer test-only — `[[built-but-vacuous-reground-ledger-asis]]`). A restart-simulation (fresh process over the same segment directory) resumes the captured pause (durable-across-restart, F3 floor (i)). **The Path-(i) `test_u_rt_95` is materialized into this real e2e (not merely un-skipped)** — it drives `execute_workflow` to `RunStatus.PAUSED` then resume, asserting the full DURABLE_ASYNC pause-trigger cycle by execution, with a contrasting check that it FAILS if WAL_SEGMENT is not materialized (proving it exercises the real path, not a tautology); only then is the skip removed and the Path-(i) fork flipped.

**Acceptance criterion (integration).** R-CXA-2 CP→IS engine-layer seam is LIVE in production (the bounded-residual disposition flips); the substitution rows + the R-CXA-2 / engine-recovery fork docs are updated (R-CXA-2 LIVE; line-181 trigger fired). Verified by execution at E-impl-2.

**Notes.** This is the load-bearing Unit-B verification (advisor decomposition #2/#3): the durable e2e proves the seam fires against a REAL substrate, not the in-memory Deterministic — foreclosing the "cosmetic Journal swap" anti-pattern (binding a durable substrate with no firing driver). R-CXA-2 activation homes at E-2/WAL_SEGMENT (NOT E-1) per CP plan v2.34 §6 O-CP-4 + companion §5 (the recovery-loop snapshot surface composes naturally with WAL_SEGMENT's append-then-resume pause-trigger, not with EVENT_SOURCED_REPLAY's pure event-replay).

---

## §3 Dependency graph

### §3.1 Dependency-graph delta (v2.43) — PRESERVED VERBATIM

| Operation | Detail |
|---|---|
| NEW node | U-RT-113 (`Depends on: (none)` — runtime projection of a code-real CP enum member) |
| NEW node | U-RT-114 (`Depends on: [U-CP-81 (cross-axis: CP)]`) |
| NEW cross-axis edge | U-RT-114 → U-CP-81 (runtime → CP; downstream package direction) |

### §3.1a Dependency-graph delta (v2.44 — B3-plan; the B3 aggregate cross-axis order is at CP plan v2.33 §3)

| Operation | Detail |
|---|---|
| NEW node | U-RT-115 (`Depends on: (none)` — foundational gate-site blast resolver) |
| NEW node | U-RT-116 (`Depends on: [U-RT-115, U-CP-91 (cross-axis: CP)]`) |
| NEW node | U-RT-117 (`Depends on: [U-RT-115, U-RT-116]`) |
| NEW node | U-RT-118 (`Depends on: (none)` — `on_hitl_timeout` persona_tier-only, exists at HEAD) |
| NEW node | U-RT-119 (`Depends on: [U-RT-118, U-CP-92 (cross-axis: CP)]`) |
| NEW node | U-RT-120 (`Depends on: (none)` — local EDIT-branch change) |
| NEW cross-axis edge | U-RT-116 → U-CP-91 (runtime → CP; downstream package direction) |
| NEW cross-axis edge | U-RT-119 → U-CP-92 (runtime → CP; downstream package direction) |

### §3.1b Dependency-graph delta (v2.45 — E-plan; the E aggregate cross-axis order is at CP plan v2.34 §3.5)

| Operation | Detail |
|---|---|
| NEW node | U-RT-121 (`Depends on: (none)` — implements the existing `EnginePauseResumeSubstrate` Protocol; extends #475) |
| NEW node | U-RT-122 (`Depends on: [U-RT-121, U-CP-95 (cross-axis: CP)]`) |
| NEW cross-axis edge | U-RT-122 → U-CP-95 (runtime → CP; downstream package direction) |

### §3.2 Acyclicity preservation

**v2.43 (B1) — PRESERVED VERBATIM.** U-RT-113 is a leaf (`(none)`). U-RT-114 → U-CP-81 runs **runtime → CP**, matching the `harness-runtime` → `harness-cp` package dependency; no CP unit depends back on U-RT-114 (the CP strategies SET `agent_role` on the context via U-CP-81; the runtime READS it via U-RT-114 — no CP→RT edge, so no cycle). Aggregate B1 acyclicity + topological order recorded at CP plan v2.32 §3 (the arc's aggregate-graph home). Runtime-axis internal DAG PRESERVED VERBATIM plus the two new nodes.

**v2.44 (B3).** The 6 new runtime nodes form an internal DAG: U-RT-115/118/120 are leaves (`(none)`); U-RT-116 → {U-RT-115, U-CP-91}; U-RT-117 → {U-RT-115, U-RT-116}; U-RT-119 → {U-RT-118, U-CP-92}. The two cross-axis edges (U-RT-116 → U-CP-91; U-RT-119 → U-CP-92) both run **runtime → CP**, matching the package dependency (`harness-runtime` → `harness-cp`); no CP unit depends back on any U-RT-* (U-CP-91/92 are foundational leaves at CP plan v2.33 §3) — so no CP↔RT cycle. Every runtime-internal edge points to a strictly-earlier node (115/118/120 foundational; 116→115; 117→115/116; 119→118). No back-edge. Aggregate B3 cross-axis acyclicity + topological order recorded at **CP plan v2.33 §3** (the B3 arc's aggregate-graph home). Runtime-axis prior DAG (U-RT-01..114) PRESERVED VERBATIM; the 6 new nodes attach without contesting it.

**v2.45 (E).** The 2 new runtime nodes: U-RT-121 is a leaf (`(none)` — implements the existing `EnginePauseResumeSubstrate` Protocol); U-RT-122 → {U-RT-121, U-CP-95}. The single cross-axis edge (U-RT-122 → U-CP-95) runs **runtime → CP**, matching the package dependency (`harness-runtime` → `harness-cp`); no CP unit depends back on any U-RT-* (U-CP-95 consumes `ctx.engine_recovery_loop` **duck-typed** — `Any` on the runtime ctx, exactly as the workflow-layer `ctx.pause_resume_protocol` at `workflow_driver.py:1200`; no `harness_cp` → `harness_runtime` import) — so no CP↔RT cycle. U-RT-122 → U-RT-121 points to a strictly-earlier node. No back-edge. Aggregate E cross-axis acyclicity + topological order recorded at **CP plan v2.34 §3.5** (the E arc's aggregate-graph home). Runtime-axis prior DAG (U-RT-01..120) PRESERVED VERBATIM; the 2 new nodes attach without contesting it.

---

## §4 Coverage matrix

### §4.1 Coverage-matrix delta (v2.43) — PRESERVED VERBATIM

| Spec contract | Atomic unit |
|---|---|
| runtime spec v1.48 C-RT-09 §9 (`'partial'` `Literal` widen + `_CP_TO_RT_STATUS[PARTIAL]→'partial'` projection + invariant) | **U-RT-113** (NEW) |
| runtime spec v1.48 C-RT-15 §14.5.3 (branch `AgentRole` dispatch-read — model binding) | **U-RT-114** (NEW) |
| runtime spec v1.48 C-RT-02 §2.2(a) (materialization site — existing stage-5 sufficient, no new binding) | NO unit — §6 Open-item O-RT-1 (no-change disposition) |

### §4.1a Coverage-matrix delta (v2.44 — B3-plan)

| Spec contract / design gap | Atomic unit |
|---|---|
| runtime spec **v1.49 §3.8** (`HITLAutoApprovePolicy` sub-model + step-4c in-`max()` floor-override consumption; AC-1 audit-wiring + AC-2 EXTERNAL_REVERSIBLE-not-representable) | **U-RT-116** (NEW; consumes U-CP-91 cross-axis) |
| runtime spec **v1.50 §14.8.9** (timeout-degradation dispatch-on-mode; AC-1 fail-open-refused + AC-3 dispatch-not-vacuous) | **U-RT-119** (NEW; consumes U-CP-92 cross-axis) |
| §14.8.2 step-4c G1-blast (`resolve_step_blast_radius` per-step-kind producer) | **U-RT-115** (NEW) |
| §14.8.2 step-4d G2 (compute `gate_level` once + thread real value to palette) | **U-RT-117** (NEW) |
| §14.8.2 step-4f G4a (`on_hitl_timeout` → `degradation_mode_applied` attribute + `audit.policy.*`) | **U-RT-118** (NEW) |
| §14.8.2 step-4i + NOTE 6-ii G3 (EDIT replace-not-merge `step.step_payload`) | **U-RT-120** (NEW) |
| design §8.2 G2c (`ToolContract.per_tool_gate_level` producer — deny-row-reaching axis) | NO unit — **CP plan v2.33 §6 O-CP-3** (REGISTERED owed-AS-spec-reconciliation; classification deferred to that gate) |
| design §7 G5 (HandoffContext non-empty summary) | OUT of scope — distinct B3-impl-handoff summarization-producer follow-on arc |

All other C-RT-* rows PRESERVED VERBATIM from v2.43 §4. The CP-package surfaces (U-CP-91 `GateLevelInput` floor-override carrier; U-CP-92 `TimeoutDegradationKind` vocab reconciliation) are covered at **CP plan v2.33 §4**; the AS-package G2c carrier is registered at CP plan v2.33 §6 O-CP-3.

### §4.1b Coverage-matrix delta (v2.45 — E-plan, WAL_SEGMENT runtime surfaces)

| Spec contract / design surface | Atomic unit |
|---|---|
| C-CP-07 §7.1 row 5 + §7.4 (WAL-segment substrate; "specific WAL implementation" deferred) + C-CP-08 §8.1 `segment_replay` + §8.2 row 5 | **U-RT-121** (NEW; hand-rolled segment-log substrate; consumes U-CP-94 cross-axis) |
| C-CP-49/50 (§16.5.2 composers) + R-CXA-2 CP→IS engine-layer seam go-live + CP §16.5.9 invariant 5 + Path-(i) `test_u_rt_95` materialization (relocated from U-CP-94) | **U-RT-122** (NEW; factory bind + go-live e2e **= the `test_u_rt_95` real durable-async e2e + un-skip + Path-(i) fork flip**; consumes U-CP-95 cross-axis) |
| design §6.2 PathClass placement (closed 4-class enum; IS-AL-1) | AC-level conditional in U-RT-121 (recommend `STATE_LEDGER` = existing member; F-E-IS sub-fork only if no honest mapping — resolves OQ-3) |

All other C-RT-* rows PRESERVED VERBATIM from v2.44 §4. The CP-package E surfaces (U-CP-93/94/95) are covered at **CP plan v2.34 §4.3**. EVENT_SOURCED_REPLAY (E-1) is CP-only (U-CP-93) — no runtime unit (R-CXA-2 owned by E-2, CP plan v2.34 §6 O-CP-4).

---

## §5 Cross-cutting integration units

None new at v2.44. (The B3 runtime surfaces are composer-internal to `RuntimeHITLGateComposer`; the two cross-axis edges U-RT-116 → U-CP-91 + U-RT-119 → U-CP-92 are simple consumer→carrier reads, not tri-spec cross-cutting integration units. All prior §5 units PRESERVED VERBATIM from v2.43.)

---

## §6 Open items

**O-RT-1 — runtime §2.2(a) materialization-site confirmation (no-change; NOT a unit).** PRESERVED VERBATIM from v2.43. Runtime spec v1.48 §2.2(a) states the non-linear topology materialization site is the **existing** stage-5 LOOP_INIT composition (`ctx.topology_dispatcher` / `ctx.step_dispatchers` / `ctx.state_ledger_writer` already bound) — **no new stage-5 binding**, and the CP driver is invoked via the existing C-RT-08 `execute_workflow` (no new runtime invocation surface). Per the implementation-planner atomicity discipline (§3.1 — a unit produces a coherent *change*; "no change needed" is not one), this is **not unit-ified**; it is recorded here as a satisfied-by-existing-substrate confirmation. The B1-impl-N executor verifies no new stage-5 binding is introduced when the strategies land (a regression check that the §2 stage-5 post-condition is not widened). Cited at the coverage matrix (§4.1) as a no-unit disposition, NOT an uncovered row.

**O-RT-2 — G2c `ToolContract.per_tool_gate_level` producer (REGISTERED at CP plan v2.33 §6 O-CP-3; runtime cross-ref).** The G2 deny-row palette narrowing (U-RT-117) is behaviorally inert in production until the `per_tool_gate_level` axis reaches DENY, which requires a `ToolContract` carrier the AS spec C-AS-03 §3.1 typed schema does NOT declare (it carries only `minimum_tier` + `blast_radius_tier`). `per_tool_gate_level` is a C-AS-12 §12.1 `gate_level()` formula axis + a C-AS-03 §3-frontmatter authoring token, NOT a typed `ToolContract` field — so materializing it owes an **AS-spec reconciliation** whose impl-vs-fork classification belongs to that gate (B3-spec skipped the AS leg). This is **REGISTERED, not dropped** (FULL-SPEC directive) and **NOT authored as cleared impl** here. The authoritative registration + classification routing is at **CP plan v2.33 §6 O-CP-3**; this runtime cross-ref records that U-RT-117 lands the G2 structural cleanup independently (the deny-row inert-but-harmless until G2c lands — see U-RT-117 Notes for the justified G2/G2c unbundling).

**O-RT-3 — G3 EDIT carrier-drift sub-fork (conditional; D-edit.B only).** U-RT-120 lands the EDIT replace-not-merge core (IMPL either way). A sub-fork (`class_*_fork_hitl_edit_carrier_drift_str_vs_mapping.md`) is owed ONLY if B3-impl-3 finds the §14.8.3 v1.12 structured-elicitation surface NOT wired (D-edit.B; the `str → Mapping` replacement is then genuinely under-specified, routed to a follow-on workflow-mutation-discipline arc per NOTE 6-ii's own deferral). If structured-elicitation IS wired (D-edit.A), the `Mapping → Mapping` replacement is plain IMPL and the sub-fork collapses. This is an executor HEAD-state check, NOT a planner decision.

All prior §6 open items PRESERVED VERBATIM from v2.43.

---

## §7 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.45 (delta over v2.44) |
| Authored at | 2026-06-15 |
| Authoring authority | R-FS-1 E-plan; `.harness/architect_recommendation_e_engine_fork_vs_impl.md` (E-1/E-2 impl-against-cleared-spec); C-CP-07 §7.1/§7.4 + C-CP-08 §8.1/§8.2 (cleared); design `.harness/r-fs-1-e-engine-classes-design-v1.md` §4/§6 |
| Net delta | +2 NEW units (U-RT-121 WAL segment-log substrate `(none)`; U-RT-122 R-CXA-2 activation `[U-RT-121, U-CP-95 cross-axis]`); +1 cross-axis edge (U-RT-122 → U-CP-95, runtime → CP downstream); +§4.1b (2 coverage rows + 1 PathClass AC-disposition); ZERO new §6 open-item (the R-CXA-2-owned-by-E-2 finding is recorded at CP plan v2.34 §6 O-CP-4); ZERO spec amendment, X-AL-3-clean |
| Sibling co-publication | CP plan v2.34 (U-CP-93/94/95 — engine driver materialization + recovery-loop firing branch); clearance markers; workspace `CLAUDE.md` §2.4 + `.harness/claude-artifact-pointers.md` §2.4 plan-head bumps |
| Cross-axis cascade | U-RT-122 → U-CP-95 (runtime → CP, downstream); no CP→RT back-edge (U-CP-95 consumes `ctx.engine_recovery_loop` duck-typed). Aggregate E graph home at CP plan v2.34 §3.5 |
| Homing decision | engine recovery loop + #475 Journal substrate + R-CXA-2 factory = `harness-runtime` (U-RT-121/122); engine driver / `EngineClass` / consumers / C-CP-49/50 composers + the firing branch = `harness-cp` (CP plan v2.34 U-CP-93/94/95) |
| E-impl sequence (companion §6) | E-impl-1 = U-CP-93 (EVENT_SOURCED_REPLAY; CP-only) → E-impl-2 = U-CP-94 + U-RT-121 + U-CP-95 + U-RT-122 (WAL_SEGMENT segment-replay + un-skip `test_u_rt_95` + durable substrate + firing branch + R-CXA-2 durable go-live e2e) → (separate) E-spec-3 → E-impl-3 = RECONCILER_LOOP |
