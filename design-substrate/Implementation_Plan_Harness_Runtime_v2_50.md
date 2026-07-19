# Implementation Plan — Harness Runtime — v2.50

*Delta over v2.49. v2.50 is the Runtime plan leg of the RATIFIED **B-48 sync sub-agent dispatch offload arc** (`.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md`, **RATIFIED 2026-07-18 — the operator selected OPTION B AS RECOMMENDED with all filing-settled riders**: custom grow-on-demand executor; ONE shared frame budget with occupied + N + S admission; sync-only inner charging; default `sub_agent_dispatch_max_workers = 256`; atomic reservation; fail-fast, never queue; the C1 ⊥ C9 apply-leg dyad `.harness/council-dyad-b48-apply-2026-07-18.md` returned **16/16 CONFIRM, ZERO deviations**), absorbing **Runtime spec v1.102** (the change-note's four Runtime-owned surfaces (A)–(D) + NEW §14.8.10.1–.5, `Spec_Harness_Runtime_v1.md`, SPEC-APPLIED 2026-07-18). The v2.49 head has NO acceptance criteria for the executor (the v1.102 change-note says so itself: "the plan head v2.49 carries no acceptance criteria for the executor") — v2.50 authors **FIVE NEW atomic units U-RT-140..U-RT-144** (next free IDs after U-RT-139, verified by grep across the chain: zero occurrences of `U-RT-14N` anywhere). Unit count 139 → **144**. All sections except the §0 change note, the §1 new-unit bodies, and the §2/§3 DAG + coverage deltas below are PRESERVED VERBATIM from v2.49 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.49 → v2.50)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_49.md` (v2.49 — the B-51/B-52/B-54 Runtime leg; U-RT-134..U-RT-139 + the U-RT-102 amendment).

### §0.2 Revision scope

Per the fork's §5 rider (c) ("a Runtime plan delta for the new executor's acceptance criteria (the plan currently has none)") and rider (e) (the §4 semantic changes — per-child pause/resume carrier isolation + the cancellation/join/effect-fence policy — ride the same Runtime spec + plan deltas explicitly, never implementation-only authority). v2.50 decomposes the Runtime v1.102 surfaces into five new units transcribing the filing's §4 obligations 1–10 as acceptance criteria. CP-owned contract text (the §25.11 fan-out capacity gating, the depth-phrase retirement, the B-39 interim sequencing constraint — CP spec v1.102 §1–§3) is CROSS-REFERENCED to the same-arc CP plan v2.39 (U-CP-82/85/86/88/89 amended + NEW U-CP-101, the capacity-authority Protocol/default-authority declaration U-RT-141 implements) — never restated. IS-owned contract text (C-IS-07 §7.6 writer-owned drain-timestamp sampling — IS spec v1.11) is CROSS-REFERENCED to the same-arc IS plan v2.7 (U-IS-11 amended) — never restated. Naming discretion per Runtime v1.102 §14.8.10.5's deferred list is respected throughout: the executor class name + worker thread-name prefix, the typed capacity error's class name + exact fail-class identifier string (`RT-FAIL-SUB-AGENT-DISPATCH-CAPACITY` is a suggested NON-BINDING name), the cancel-token / effect-fence carrier shapes, the frame-accounting data structure, the drain-report shape, and the construction-time mode/adapter mechanism (ctor flag vs adapter wrapper) are implementation discretion — the units below pin BEHAVIOR criteria and mark any proposed name as a non-binding suggestion. CARRIER HOME (codex round-5): the typed capacity-exhausted error class lives in `harness-core` (both `harness-cp` and `harness-runtime` consume it; the §14.8.10.5 fail-class row maps to the core type; name non-binding) — aligned with CP v1.102 §3's full rule (codex round-13): during a pending-response resume window ALL siblings, gated and ungated, sequence around the resumed target.

### §0.3 Sections revised

§0 (this change note); §1 (NEW U-RT-140..U-RT-144); §2 (DAG delta); §3 (coverage delta). All v2.49-and-earlier unit bodies (U-RT-01..U-RT-139) PRESERVED VERBATIM.

### §0.4 Scope + witness discipline

The filing's §4 obligations home as `Tests:` criteria (every new witness PD-8 mutation-probed per Workflow v1.18 PD-8 — §4 item 10 is a standing criterion over every unit below, not a separate unit): item 1 → U-RT-142; item 2 → U-RT-143; item 3 → U-RT-142; items 4/5 → U-RT-144; item 6 → the CP plan v2.39 amendments (U-CP-85/86/88; Runtime-side halves at U-RT-141/U-RT-144); item 7 → IS plan v2.7 U-IS-11 + CP plan v2.39 U-CP-82 (cross-axis — no Runtime unit); item 8 → U-RT-142; item 8-bis → U-RT-141; item 9 → U-RT-141. Cross-axis co-land pins (recorded, not DAG edges — one B-48 impl arc): U-RT-141 ⊕ CP plan v2.39 U-CP-86/U-CP-88 (the shared-budget admission's CP fan-out half); U-RT-144 ⊕ CP plan v2.39 U-CP-85/U-CP-86 (nested cascade-deadline cancel + sibling pause/resume isolation CP halves); the drain-timestamp fix + xfail removal ⊕ IS plan v2.7 U-IS-11 ⊕ CP plan v2.39 U-CP-82.

---

## §1 New units

### §1.1 U-RT-140 — `sub_agent_dispatch_max_workers` C-RT-03 field + typed capacity error surface (v1.102 surface A)

**Implements:** Runtime spec v1.102 §3 C-RT-03 (`sub_agent_dispatch_max_workers: int = 256` field row — the ONE shared frame budget, sized in FRAME units; a minor OPTIONAL-with-default addition on the C-RT-03 contract-v2 head) + §14.8.10.5 (the typed fail-fast capacity error row).

**Depends on:** [U-RT-103 (RuntimeConfigSource layered loading — the field must ride all three source layers), U-CORE-03 (cross-package: harness-core — the shared capacity error this unit's taxonomy row maps to; Core plan v1.3; codex round-8)].

**Files affected (logical):** the RuntimeConfig schema module; `config/loader.py` (`_ENV_SCALAR_FIELDS`); `config_source.py` (`_RuntimeEnvSettings`); the typed-error surface for the capacity error.

**Acceptance criteria:**

1. `RuntimeConfig` gains `sub_agent_dispatch_max_workers: int = 256` — the shared frame budget under the §14.8.10.1 occupied+N+S accounting (default 256 per the ratified filing §3 sizing: a legitimate all-sync 3-wide × depth-4 hierarchy holds 3+9+27+81 = 120 active branches × 2 frames = 240 ≤ 256, with headroom); VALIDATED ≥ 1 at config load (a value < 1 is a typed config-validation rejection).
2. **(EXPLICIT criterion per the known dropped-env-override defect class, `[[runtimeconfig-scalar-needs-both-env-loaders]]` — the same criterion shape as U-RT-134 acc #2.)** DUAL env-loader registration: the field is env-keyed via BOTH `config/loader.py::_ENV_SCALAR_FIELDS` AND `config_source.py::_RuntimeEnvSettings`. Registration in only one loader is an acceptance FAILURE. *(Env key name is implementation discretion; non-binding suggestion: `HARNESS_SUB_AGENT_DISPATCH_MAX_WORKERS`.)*
3. The typed fail-fast capacity error is defined per the §14.8.10.5 row's BINDING contract terms: raised when dispatch admission against the shared frame budget fails; NEVER queued, no best-effort degradation (C9); the error NAMES the overflowing dispatch STEP and carries the descent chain in the message (C1 — attributable by the driver/topology machinery, not a generic executor error); it surfaces via the existing `StepDispatcher` fail-propagation path (driver `step-failure:` mapping per C-CP-25 §25.3.3.4). *(Class name + fail-class identifier string are implementation discretion; non-binding suggestion: `RT-FAIL-SUB-AGENT-DISPATCH-CAPACITY`.)*
4. Contract-minor byte-compat: the field unset (default 256) changes NO existing config surface; existing callers untouched (the §3 version-evolution clause's optional-field-minor-bump reading, per the v1.102 change-note).

**Tests (mutation-probed per PD-8):** `test_cap_field_env_only_override_honored_through_both_loaders` (mutation probe: removing EITHER loader registration fails), `test_cap_field_validated_ge_one_at_config_load` (0 and negative rejected typed), `test_capacity_error_names_overflowing_step_and_descent_chain`.

**Rollback boundary:** revert the field + error; U-RT-141 loses its cap carrier and typed boundary — the executor cannot land.

---

### §1.2 U-RT-141 — grow-on-demand dispatch executor + shared frame budget + admission + lifecycle (v1.102 §14.8.10.1)

**Implements:** Runtime spec v1.102 §14.8.10.1 (custom grow-on-demand executor; occupied+N+S admission over ONE shared frame budget; atomic per-branch reservation; fail-fast at the cap NEVER queue; lifecycle on its own terms; fan-out resume semantics preserved). The CP-owned fan-out admission semantics (ADMISSION RULE (sharpened rounds 6/15/17): initial branch-dispatching admission gated at ALL FOUR sites (incl. cancel-policy execution); only frame-releasing teardown of already-admitted branches exempt (rounds 6/15/17); admission-rejection = branch failure under §25.15) are DEFINED at CP spec v1.102 §1 and homed at CP plan v2.39 (U-CP-85/86/88) — cross-referenced, never restated.

**Depends on:** [U-RT-140 (the cap field + typed capacity error), U-CORE-03 (cross-package: harness-core — the shared capacity error the adapter raises; Core plan v1.3; codex round-9), U-CP-101 (cross-axis: CP — the capacity-authority Protocol this unit's adapter IMPLEMENTS; codex round-18 — direction Runtime→CP, acyclic)].

**Files affected (logical):** a new executor module in `harness-runtime` (the grow-on-demand executor + frame-budget accounting); its composition-root construction site.

**Acceptance criteria:**

1. CUSTOM executor (stock `ThreadPoolExecutor` has NO unbounded mode): a worker thread is created when no free worker exists; idle workers are reused; threads are named. The two existing pools are NOT used (the 4-worker audit-offload executor; the loop's default `ThreadPoolExecutor`) — per the filing §2 ineligibility grounds.
2. ONE shared frame budget = `config.sub_agent_dispatch_max_workers` covering BOTH executor layers: every active branch reserves ONE upstream CP frame; ONLY sync/offloaded `SUB_AGENT_DISPATCH` branches reserve the additional inner-dispatch frame (async INFERENCE/TOOL inners are UNCHARGED — charging them would reject unrelated async work despite free executor capacity). `occupied` counts ancestors blocked on descendants AND concurrent workflows holding frames — admission is against AVAILABLE capacity, never the local fan-out alone.
3. ATOMIC per-branch reservation: all-frames-or-fail-fast — a branch acquires its full frame set atomically or not at all (no partial-acquisition exhaustion across concurrent fan-outs).
4. Fail-fast at the cap, NEVER queue: at the cap, admission raises the U-RT-140 typed capacity error immediately. No queueing in ANY variant (a queued descendant whose parents hold every worker is the filing §2 recursive-offload deadlock).
5. Lifecycle on its OWN terms: daemon worker threads + bounded per-DISPATCH join on cancellation (the `run_audit_off_loop` per-job-join shape); drain-with-deadline at shutdown that MUST NOT block on workers currently bridged into the event loop. (The B2a `_DaemonThreadAuditExecutor` is NOT a join-on-shutdown precedent.)
6. The CP v1.97 `PeerFanOutResumeState.paused_child_branches` paused-child-branch resume semantics are UNCHANGED: admission gating changes WHETHER a branch starts, never how a paused one resumes (witnessed CP-side at plan v2.39; Runtime-side control here asserts no executor-layer interference).

- RESERVATION-LEASE LIFECYCLE (codex round-7): the executor owns each job's frame lease — held until ACTUAL job termination or fence-drain acknowledgement (a drained-under-fence or abandoned worker keeps its frames until its fence acks; parent return never releases), released EXACTLY-ONCE across success/failure/pause/cancellation/timeout; witness `test_draining_worker_retains_lease_until_fence_ack` (a cap-full budget with one draining worker rejects a new admission until the drain acks, then admits — mutation probe: releasing on parent return passes an over-cap dispatch during drain and fails) + an exactly-once-release assertion across the five outcome paths.
- CAPACITY-AUTHORITY ADAPTER (codex round-1 on the apply PR): U-RT-141 supplies the adapter implementing the CP-declared capacity-authority Protocol (CP plan v2.39's cycle-safe carrier — RAISE-CAPABLE frame-unit atomic reserve/release over the real executor budget: on exhaustion it raises THE shared typed capacity error — HOMED IN `harness-core` per the workspace carrier-home discipline (codex round-5 reconciliation: CP's fan-out and Runtime's dispatch sites both raise/handle the SAME type; both packages import `harness-core`, no mapping seam, no dual ownership) — with the caller-supplied step/descent context; U-RT-140's taxonomy row references the core type) and the composition root injects it into the CP fan-out path; integration witness `test_cp_fanout_admission_through_real_executor_authority` (a real fan-out admission decision flows through the injected adapter against the live budget — mutation probe: an always-true stub authority passes the below-capacity witnesses but fails the saturation witness through this path).

**Tests (mutation-probed per PD-8):** **Filing §4 item 9 — cap saturation + no-queue:** `test_cap_saturation_next_dispatch_fails_immediately_typed_and_enqueues_nothing` (deterministic cap+1: every frame occupied, one more dispatch → the typed error IMMEDIATELY, provably zero queue growth; mutation probe: swap fail-fast for enqueue → the witness must hang/fail) + `test_shutdown_drain_with_deadline_never_blocks_on_loop_bridged_worker`. **Filing §4 item 8-bis — loop-responsiveness (the PRIMARY defect's own proof):** `test_unrelated_workflow_and_loop_timer_advance_during_slow_offloaded_dispatch` (a slow sync child / stubbed slow KMS call runs through the offload while an UNRELATED concurrent workflow and a pending loop timer demonstrably advance; mutation probe: revert to the direct call → this witness must fail). **Admission accounting:** `test_async_inner_branches_uncharged_sync_branches_charged_two_frames` (mutation probe: charging async inners rejects a fan-out the budget admits and fails the control), `test_atomic_reservation_no_partial_acquisition_under_concurrent_fanouts`.

**Rollback boundary:** revert the executor; dispatch falls back to the ratified-but-defective direct call — the §1 loop-blocking defect and the loop-bridge deadlock reopen; U-RT-142/143/144 lose their substrate.

---

### §1.3 U-RT-142 — construction-time dispatch-mode selection + worker-thread facade bridging + deadlock-anchor promotion (v1.102 §14.8.10.2; filing §4 items 1/3/8)

**Implements:** Runtime spec v1.102 §14.8.10.2 (the three-row stage-5 construction table; sync inners SUBMITTED to the executor, async inners keep the direct await path) + the §14.8.10 provenance clause superseding the post-call awaitability discovery.

**Depends on:** [U-RT-141 (the executor sync inners are submitted to), U-RT-60 (prior-landed — the wrap-asymmetry composer surface `_dispatch_inner` this unit revises)].

**Files affected (logical):** `lifecycle/hitl_gate_composer.py` (`_dispatch_inner` + the construction-time mode/adapter); `bootstrap/stage_5_loop_init.py` (the three composer constructions).

**Acceptance criteria:**

1. **(Filing §4 item 1.)** An explicit construction-time mode/adapter replaces the post-call awaitability discovery (`hitl_gate_composer.py:968-986` at HEAD): the composer knows its inner's §14.8.1 wrap-asymmetry row when built at stage 5. The documented Future/custom-awaitable support of the direct await path is PRESERVED (moving every invocation into a worker is foreclosed). *(Mechanism — ctor flag vs adapter wrapper — is implementation discretion.)*
2. All THREE stage-5 composer constructions conform to the §14.8.10.2 table: `hitl_inference` (`stage_5_loop_init.py:500`, async C-RT-15) → direct await, unchanged; `hitl_sub_agent` (`:615`, sync C-RT-17) → SUBMITTED to the U-RT-141 executor; `hitl_tool` (`:698`, async `RetryBreakerToolDispatcher.dispatch`) → direct await, must stay direct.
3. **(Filing §4 item 3.)** The sync driver's loop-bridge (`run_coroutine_threadsafe` shape, `lifecycle/sync_dispatcher_facade.py`) is exercised from a WORKER thread with the parent awaiting off-loop — the full parent→child→grandchild chain works (each descent level a separate executor job under the shared budget).
4. **(Filing §4 item 8.)** The superseded defect record's live anchor `test_u_cp_89_hierarchical_delegation_depth2_live_ollama` (`harness-runtime/tests/integration/test_u_cp_89_hierarchical_delegation_live_e2e.py:176`, xfail strict=False at HEAD) flips XPASS under the offload (the sub-agent INFERENCE child's facade bridge finds the loop free) and is PROMOTED from xfail on flip — the promotion is an acceptance criterion of this unit, not a discretionary cleanup.

**Tests (mutation-probed per PD-8):** **Filing §4 item 1 witness:** `test_all_three_stage5_constructions_select_mode_at_construction` (parametrized over the three composers; sync submitted / async direct; mutation probe: reverting to post-call discovery fails the sync case). **Filing §4 item 3 witness:** `test_parent_child_grandchild_chain_bridges_from_worker_threads_parent_off_loop`. **Item 8:** the promoted (no-longer-xfail) ollama anchor, run per the credential-gated live-e2e discipline.

**Rollback boundary:** revert the mode selection; the sync inner re-enters the loop-blocking direct call and the ollama anchor re-xfails.

---

### §1.4 U-RT-143 — three-part dispatch-time cancellation policy + token cascade + job-wide effect fence + terminal drain disposition (v1.102 §14.8.10.3; filing §4 item 2)

**Implements:** Runtime spec v1.102 §14.8.10.3 (the three mandatory parts; token cascade through recursive descent; honest guarantee + `worker_draining_under_fence` AMBIGUOUS-EFFECTS / PERMANENTLY TERMINAL disposition; the v1.31 `RT-FAIL-STEP-DISPATCH-TIMEOUT` canonical-reading amendment).

**Depends on:** [U-RT-141 (executor jobs the token/fence govern), U-RT-142 (the offloaded venue), U-IS-11 (cross-axis: IS — the §7.6-widened writer-owned timestamp API the offloaded audit appends adopt; codex round-32)].

**Files affected (logical):** the child-driver step-boundary check sites; `lifecycle/sub_agent_dispatch.py` (the four post-child `_compose_and_persist_audit` sites at `:1018`/`:1051`/`:1088`/`:1126`); `lifecycle/sync_dispatcher_facade.py` (the bounded join at `:115` lineage); the cancel-token/fence carriers. *(Carrier shapes are implementation discretion.)* (codex round-28: these appends also adopt the IS §7.6-widened writer-owned timestamp sampling — B-48's concurrency newly exercises this direct path; co-land with the IS U-IS-11 widening).

**Acceptance criteria:**

1. THREE mandatory parts, all present: (a) a cooperative CANCEL TOKEN checked by the child driver at every step boundary; (b) a JOB-WIDE EFFECT FENCE the token trips — once tripped, no further F2/audit writes; in-flight step results discarded at the fence (at-most-once effect discipline); (c) a bounded JOIN to the fence acknowledgement with TWO distinct outcomes (codex round-10 — the join and the drain disposition cannot both hold unqualified): fence ACKED within the grace AND the ack reports NO effect-bearing operation was in flight at trip time (the fence tripped BETWEEN operations) → `StepDispatchTimeoutError` surfaces WITHOUT the drain disposition (effects genuinely unambiguous); fence acked but an effect-bearing operation WAS in flight at trip (codex round-11: it may have completed after the trip, so an ack alone does not prove unambiguity) → the error carries the AMBIGUOUS-EFFECTS / TERMINAL disposition exactly as the unacked case — the ack's in-flight flag is part of the fence-ack contract; grace EXPIRES unacked (worker still inside a blocking call) → the error surfaces carrying `worker_draining_under_fence` (AMBIGUOUS-EFFECTS / TERMINAL per criterion 4); the join never blocks past the grace. Witnesses (codex round-12): `test_ack_clean_trip_surfaces_unqualified_timeout` (fence trips between operations, acks, no drain disposition) + `test_ack_after_inflight_effect_is_ambiguous_terminal` (an effect-bearing call in flight at trip, ack within grace → the drain disposition anyway; mutation probe: keying the disposition on ack-presence alone passes the in-flight case as safe and fails).
2. The fence covers the ENTIRE offloaded job, NOT only child-driver step boundaries: a tripped fence also suppresses the four post-child `_compose_and_persist_audit` persists (SUCCESS/DRAINED + the exception/FAILED/PAUSED paths) — or the writers are wrapped job-wide — else entries land after `StepDispatchTimeoutError` despite the guarantee.
3. Token CASCADE through recursive descent: descendant executor jobs inherit/link the ancestor's cancel token; tripping it fences the whole descent chain (a timed-out child blocked inside a nested `SUB_AGENT_DISPATCH` cannot reach its next token check while the grandchild runs as a separate job).
4. Honest guarantee + TERMINAL disposition: the fence stops operations NOT YET STARTED (it cannot abort a synchronous append or external call the worker is already inside). Grace-expiry with the worker still inside a blocking call surfaces the error with an explicit `worker_draining_under_fence` disposition — never silent abandonment, never a pretended completion — and that disposition is AMBIGUOUS-EFFECTS / PERMANENTLY TERMINAL: NO automatic retry path (no new retry-gate carrier — the step fails permanently; the §14.8.1 `SUB_AGENT_DISPATCH` row carries no retry layer); workflow re-run after drain is an OPERATOR action informed by the drain report. *(Drain-report shape is implementation discretion.)*
5. The v1.31 `RT-FAIL-STEP-DISPATCH-TIMEOUT` row is read UNDER the fence from this unit's landing (abandoned-worker residual liveness bounded to operations already started).

**Tests (mutation-probed per PD-8):** **Filing §4 item 2 witnesses:** `test_parent_child_grandchild_cancellation_chain_fences_whole_descent` (the token cascades; the grandchild's job is fenced by the ancestor trip), `test_no_new_child_effects_after_failure_surfaces_including_post_child_audit_sites` (mutation probe: unfencing any ONE of the four `_compose_and_persist_audit` sites fails the test), `test_drained_under_fence_step_is_terminal_never_automatically_retried` (the disposition present on the surfaced error; no automatic re-dispatch path fires; mutation probe: routing the error through a retryable fail-class re-runs the step and fails).

**Rollback boundary:** revert the policy; cancelled dispatches regain unbounded late effects (post-failure audit writes; unfenced descent chains) — the round-12/13/14/16/19 defect set reopens.

---

### §1.5 U-RT-144 — pause/resume + selective execution-context riders across the executor boundary (v1.102 §14.8.10.4; filing §4 items 4/5/6 Runtime halves)

**Implements:** Runtime spec v1.102 §14.8.10.4 (cross-executor pause carrier; worker-visible pause flags; selective contextvar carry with the two named exceptions; parent→job cancellation channel; per-child/per-run pause + resume isolation WITH the B-39 boundary). The B-39 interim sequencing constraint itself is CP-OWNED contract text (CP spec v1.102 §3, homed at CP plan v2.39) — cross-referenced, never restated.

**Depends on:** [U-RT-142 (the offloaded venue), U-RT-143 (the cancel token the parent→job channel trips)].

**Files affected (logical):** the executor submission path (context carry); `lifecycle/sub_agent_dispatch.py` (`SubAgentChildPausedError` at `:134`, raised at `:1101`); `lifecycle/inter_step_output_channel.py` (`INTER_STEP_CHANNEL_VAR` at `:153` — per-child binding); the `_BRANCH_INFLIGHT_DISPATCHES` registry handle (`harness-cp/src/harness_cp/workflow_driver.py:2092` — the Runtime-consumed cross-thread-safe cancellation handle; the CP-side witness rides plan v2.39 U-CP-85); the pause-flag / resume-context carriers.

**Acceptance criteria:**

1. **(Item 4 — the REAL carrier.)** A child's nested durable-HITL gate pausing surfaces from the sync `RuntimeSubAgentDispatcher` as `SubAgentChildPausedError` carrying the child's pause SNAPSHOT, and the error AND snapshot cross the executor future INTACT into the parent's fan-out pause handling. The witness exercises THAT carrier — a synthetic `HITLPauseRequestedSignal` or worker-set flag is an acceptance FAILURE (a path production never takes can miss snapshot loss).
2. **(Item 4.)** Durable-async pause flags set from the worker thread are visible to the resume path — no thread-local state.
3. **(Item 5 — selective carry.)** The offload carries `contextvars.copy_context()` for trace continuity, EXCEPT the two named loop-affine exceptions: (a) `INTER_STEP_CHANNEL_VAR` — a PER-CHILD channel is bound (the copied parent channel would let one sibling's step output enter another's payload via `most_recent_output()`); (b) `_BRANCH_INFLIGHT_DISPATCHES` — the registry gains a cross-thread-safe cancellation handle (or a fresh per-child registry with parent-side aggregation).
4. **(Item 5 — parent→job channel.)** The fan-out barrier deadline trips the SAME U-RT-143 cancel token (nothing at HEAD carries the `shutdown(wait=False)` abandonment at `workflow_driver.py:6339` into the offloaded job) — a parent-barrier-deadline cancel reaches the child's fence.
5. **(Item 6 Runtime half — isolation carriers.)** Per-child/per-run pause-flag AND resume-context isolation: only the branch that raised the pause signal is recorded paused (no false sibling pause via the shared `ctx.pause_requested_flag`); the shared `ctx.resume_context_holder` unkeyed `consume_and_clear()` hazard is neutralized AT B-48'S SCOPE by the CP v1.102 §3 sequencing (ALL siblings sequenced around a resumed target during a pending-response window — the sequencing witness is the B-48 obligation); the CONCURRENT branch-keyed consume-prevention witness is B-39's scope (branch-unique routing is undesigned there — requiring it here would cross the authority boundary, codex round-22). The per-child isolation CARRIERS still land here (necessary substrate for B-39). **B-39 boundary:** the branch-unique one-shot HITL-response routing through CP's `ResumeContext`/driver is B-39's gated CP design — NOT designed here; until B-39 resolves, the CP v1.102 §3 constraint governs IN FULL — two gated siblings never genuinely concurrent AND all siblings (gated + ungated) sequenced around a resumed target during a pending-response window (codex round-14; witnessed CP-side at plan v2.39). These isolation carriers are necessary-but-not-sufficient for gated-sibling concurrency.

**Tests (mutation-probed per PD-8):** **Item 4:** `test_real_sub_agent_child_paused_error_and_snapshot_cross_executor_future_intact` (mutation probe: dropping the snapshot across the future boundary fails). **Item 5:** `test_parent_child_span_id_continuity_through_offload` (mutation probe: dropping the context copy fails), `test_sibling_children_channel_isolation_no_cross_child_output` (mutation probe: sharing the parent channel fails), `test_nested_cascade_deadline_cancel_through_offloaded_child` (the cross-thread handle path; pairs with CP plan v2.39 U-CP-85 witness (f)), `test_parent_barrier_deadline_cancel_reaches_child_fence`. **Item 6 Runtime half:** `test_only_raising_branch_recorded_paused_no_false_sibling_pause`, `test_concurrent_resume_response_not_consumed_by_wrong_sibling` (pairs with CP plan v2.39 U-CP-86 witness (d)) — REMOVED from B-48's suite (codex round-33: the concurrent branch-keyed case is B-39 scope; B-48 owns ONLY the sequencing witness).

**Rollback boundary:** revert the riders; the offload ships with wholesale context bleed (cross-sibling output, thread-unsafe cancellation, orphaned parent-abandonment) — the round-7/10/12 defect set reopens; U-RT-142 becomes unshippable (the riders gate the offload's correctness).

---

## §2 DAG topology delta (v2.49 → v2.50)

Five new units; acyclic (Kahn-verifiable — each layer depends only on earlier layers + prior-landed units):

```
L0-within-delta: U-RT-140 (← U-RT-103 prior-landed) — plus U-RT-140/U-RT-141 ← U-CORE-03 (Core plan v1.3, codex round-8)
L1-within-delta: U-RT-141 (← U-RT-140; + U-CORE-03 [Core plan v1.3] + U-CP-101 [cross-axis: the Protocol it implements — the ONE Runtime→CP edge, safe direction; codex round-22])
L2-within-delta: U-RT-142 (← U-RT-141; + U-RT-60 prior-landed)
L3-within-delta: U-RT-143 (← U-RT-141, U-RT-142 + U-IS-11 cross-axis — the §7.6-widened writer-owned timestamp API its offloaded audit writes consume; codex round-35)
L4-within-delta: U-RT-144 (← U-RT-142, U-RT-143)
```

Cross-axis relationships (reconciled rounds 20-26 — ONE authoritative graph): the CP fan-out amendments (U-CP-85/86/88) depend ONLY on U-CP-101 (the CP-declared Protocol + default authority); U-RT-141 ← U-CP-101 (the adapter implements the Protocol — the one Runtime→CP edge, cycle-safe) and ← U-CORE-03; U-RT-141 is a CO-LAND/INTEGRATION PIN of the one B-48 impl arc for the CP units, never a CP dependency.

---

## §3 Coverage matrix delta (v2.49 → v2.50)

| Spec surface (Runtime v1.102) | Units covering |
|---|---|
| §3 C-RT-03 `sub_agent_dispatch_max_workers` field row (surface A) + §14.8.10.5 typed capacity error | U-RT-140 |
| §14.8.10.1 executor contract (grow-on-demand; occupied+N+S shared budget; atomic reservation; fail-fast never-queue; lifecycle; resume-semantics preservation) (surface B) | U-RT-141 (admission semantics' CP half at CP plan v2.39 U-CP-85/86/88 — cross-axis) |
| §14.8.10.2 construction-time dispatch-mode selection (surface B) + filing §4 items 3/8 | U-RT-142 |
| §14.8.10.3 cancellation policy + `RT-FAIL-STEP-DISPATCH-TIMEOUT` canonical-reading amendment (surface C) | U-RT-143 |
| §14.8.10.4 pause/resume + execution-context riders (surface D) | U-RT-144 (B-39 interim constraint CP-owned at CP plan v2.39 — cross-axis) |
| Filing §4 item 7 (drain-timestamp fix + strict-xfail removal) | IS plan v2.7 U-IS-11 + CP plan v2.39 U-CP-82 (cross-axis — no Runtime unit) |

All four v1.102 Runtime-owned surfaces covered ≥ 1 unit; every new unit traces ≥ 1 spec surface; filing §4 items 1–10 all homed (item 10 standing over every witness above). ✓

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_50.md` (delta over v2.49) |
| Authored at | Phase 7 — B-48 sync sub-agent dispatch offload apply leg (2026-07-19) |
| Authoring authority | Runtime spec v1.102 (change-note + NEW §14.8.10, `Spec_Harness_Runtime_v1.md`, SPEC-APPLIED 2026-07-18) + `.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md` (RATIFIED 2026-07-18, OPTION B AS RECOMMENDED with all filing-settled riders) + `.harness/council-dyad-b48-apply-2026-07-18.md` (16/16 CONFIRM, zero deviations) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_49.md` (v2.49 — B-51/B-52/B-54 Runtime leg) |
| Siblings (same arc) | `Implementation_Plan_Control_Plane_v2_39.md` + `Implementation_Plan_Information_Substrate_v2_7.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
