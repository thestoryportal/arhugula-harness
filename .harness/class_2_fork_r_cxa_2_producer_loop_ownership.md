# Class 2 (in-execution operator decision) — R-CXA-2 producer-loop ownership + identity

**Filed at:** R-CXA-2 producer-seam design arc (2026-06-08), HEAD `7ae493d`
**Locus:** the absent production producers for `cp.hitl-tool-call-rewriting`, `cp.pause-captured`, `cp.resume-attempted` (runtime composers LANDED + tested; no firing site)
**Status:** ✅ RATIFIED 2026-06-08 — DP-1(c) bounded-residual defer for HITL model-driven inner loop; DP-2(c) bounded-residual defer for engine recovery loop; DP-3(a) recovery-loop-context-supplied opaque identities when a real recovery loop exists. No code/spec substrate change landed in this ratification arc.
**Routing:** runtime-axis OR CP-axis design-phase per runtime plan v2.39 §0.4 NEW row (which already routed the HITL firing-site-absence "recommend sibling-bundle with U-CP-34 firing-site arc").
**Parent lineage:** `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (CLOSED — firing-site-layer continuation, line 355). Companion design brief: `r-cxa-1-2-producer-seam-spec.md` §3–§4. Sibling defect fork: `class_1_fork_u_cp_78_pause_captured_type_impedance.md`.
**Precedent:** `[[r-cxa-seam-wiring-is-producer-discovery]]` · `[[grounding-reveals-claude-closeable-slice-close-honestly]]` · v2.34 AC #8/#9 risk flags · CP-AL-1 (sub-agent topology ≠ H_T CP primitives).

## 0. Ratification (2026-06-08)

The operator approved the recommendations as an honest MVP-bounded disposition:

- **DP-1 = Reading (c), bounded-residual defer.** The current MVP runtime has no model-driven multi-tool inner loop. Do not satisfy `cp.hitl-tool-call-rewriting` with a hollow single-dispatch caller. Re-open only when an actual model-emitted tool-call loop is in scope.
- **DP-2 = Reading (c), bounded-residual defer.** The current MVP runtime has no multi-`EngineClass` recovery loop. Do not extend `workflow_driver.py` to impersonate the engine layer. Re-open when a real event-sourced replay, reconciler, WAL-segment, or engine-native-pause recovery loop lands.
- **DP-3 = Reading (a), contingent future rule.** When DP-2 re-opens with a real recovery loop, the loop supplies stable opaque `pause_event_id` / `resume_event_id` values and a replay-safe `resume_attempt_count`; no type-field extension is authorized by this ratification.

**Closeout posture:** the fork is ratified, not applied to runtime code. R-CXA-2 remains STILL-BOUNDED on future upstream-loop authoring; the ratification prevents hollow wiring and defines the re-open triggers.

## Why Class 2 (not Class 1)

These are **choose-between-substantive-alternatives** decisions, not defects. The primitives are design-committed (ADR-D5 §1.3.2 HITL rewrite; ADR-D5 §1.11 pause/resume; ADR-D1 EngineClass/ResumptionKind). What is unspecified is **which production loop owns the firing** and **where two disambiguator identities come from**. Each DP has a defensible default; the operator selects.

---

## DP-1 — HITL tool-call rewrite firing site (the model-driven inner loop)

**Gap:** `RuntimeHITLPlacementRegistry.rewrite_tool_call(...)` (`hitl_placement.py:187`, real body) has 6 test callers + ZERO production callers (runtime plan v2.39 §0.3 firing-site-absence finding, reconfirmed this arc). No production loop iterates **model-emitted tool calls** through the rewrite-before-dispatch gate; each workflow step is a single dispatch.

**Decision:** where does the model-driven tool-call inner loop live?

- **(a) NEW runtime inner-loop primitive** — author an agentic tool-use loop (LLM response → per tool call → `ProposedAction` → `hitl_required` (U-CP-43) → `rewrite_tool_call` → gate/emit → dispatch) as a new runtime-axis composer, sibling to `RuntimeToolDispatcher`. **Recommended IF** the harness intends model-driven multi-tool turns at MVP.
- **(b) Extend the existing step dispatch** — fold the rewrite gate into the existing single-dispatch step path where a step already carries a tool call. Smaller; but does not add model-driven *iteration* (only gates the one tool call a step already names).
- **(c) Defer as bounded-residual** — if MVP scope is single-threaded-linear workflows with no model-driven tool-use turns, the HITL-rewrite producer has no legitimate firing site yet; carry as X-AL-2 bounded-residual (the honest "0-wireable" disposition, mirroring R-CXA-4).

**Note (CP-AL-1):** the inner loop is an H_T runtime primitive, NOT the H_E `Agent`-tool sub-agent topology. Do not satisfy DP-1 by pointing at Claude Code sub-agents.

**Recommendation:** **(a)** if model-driven tool-use is in MVP scope; else **(c)** with an explicit bounded-residual note. **(b) is discouraged** — it satisfies the letter (a `rewrite_tool_call` caller exists) without the substance (no real model-driven rewrite decisions occur), risking a hollow seam.

**Settled sub-part (cite, do not re-open):** the `semantic_variant_binding_id` derivation is **already ratified** — `= rewritten_call.variant.value` (runtime plan v2.39 Reading B, operator-ratified 2026-05-29). DP-1 is about the *loop*, not the disambiguator.

---

## DP-2 — engine-layer recovery-loop ownership

**Gap:** the engine-layer free functions `capture_pause_snapshot` / `attempt_resume` (`pause_resume_protocol.py:252`/`:272`) fail closed unless `bind_engine_pause_resume_substrate(...)` binds an `EnginePauseResumeSubstrate` (`:153`). A provider-free `DeterministicEnginePauseResumeSubstrate` exists (`:171`) but **nothing in production binds it or calls the free functions**. The `EngineClass` 5-class + `ResumptionKind` 5-class taxonomies exist; production emits only binary RESUMPTION on `SAVE_POINT_CHECKPOINT` (`workflow_driver.py:725-746`, CP-9 retirement note).

**Decision:** who owns the engine recovery loop that binds the substrate and drives `capture_pause_snapshot`/`attempt_resume` at real crash-recovery / replay / engine-native-pause sites?

- **(a) NEW runtime engine-recovery primitive** — a runtime-axis loop per `EngineClass` (event-sourced-replay / save-point-checkpoint / reconciler / WAL-segment) that exercises the engine free functions and fires `cp.pause-captured` / `cp.resume-attempted`. **Recommended IF** the harness intends real multi-EngineClass recovery at MVP.
- **(b) Extend the workflow driver** — have `workflow_driver.py` additionally drive the engine-layer surface. **Discouraged** — it would blur the deliberate C-CP-22 (engine-layer) vs C-CP-26 (workflow-layer) distinction the spec keeps separate (`pause_resume_protocol_types.py:21-28`); the workflow driver already correctly owns the *workflow-layer* `cp.pause-resume-protocol`.
- **(c) Defer as bounded-residual** — if MVP runs only the checkpoint/binary-resume slice (current state), the engine-layer recovery loop has no production site; carry as X-AL-2 bounded-residual with a documented re-open trigger (a real event-sourced-replay or reconciler engine landing).

**Recommendation:** **(c)** is the honest MVP disposition unless the operator confirms multi-EngineClass recovery is in scope, in which case **(a)**. **Do not (b).** This mirrors the producer-discovery lesson (`[[r-cxa-seam-wiring-is-producer-discovery]]`): the absence of a producer is often correct, not a gap to paper over.

**External precedent to consult at ratification (operator-named in the R-CXA-2 handoff; NOT independently retrieved this session — see deferral note below).** The engine recovery-loop ownership question is structurally "durable wait/resume coordinated by external state change," which three production systems model and which Reading (a) should be designed against:
- **OpenAI Agents SDK HITL** — approval-interruption + durable `RunState` resume (the run serializes its state at the interrupt and resumes from it). Maps to: how the recovery loop persists + rehydrates pause state (cf. `PauseSnapshot.snapshot_hash` integrity).
- **AWS Step Functions callback task token** — durable wait/resume by an external callback delivering a token. Maps to: the `pause_event_id` / `resume_event_id` as the durable correlation token (DP-3 (a)).
- **Temporal signals / updates / wait-conditions** — external state changes + workflow recovery coordination. Maps to: the engine-native-pause + reconciler `EngineClass` recovery semantics and `resume_attempt_count` retry coordination.

These reinforce DP-3 (a) (recovery-loop-context-supplied opaque correlation ids are the standard durable-resume pattern) and DP-2 (a)'s loop shape. **Per `CLAUDE.md` §10.4, specific API/URL citations are NOT asserted here because the vendor docs were not retrieved in this session** — they are flagged for retrieval at the ratification arc.

> **Deferral note (silent-scope-narrowing guard, `CLAUDE.md` §10.5).** The handoff's "Required startup" listed a NotebookLM / harness-research-corpus query for producer-seam / HITL pause-resume / secret-fetch / runtime recovery-loop precedent. That corpus query was **not run this session** (this is a background job; the NotebookLM MCP is interactively-authenticated and may be absent headless, per `[[notebooklm-harness-corpus-url]]`). The producer-seam *design* is fully determined by the workspace's own ratified contracts (two-layer pause/resume, engine-substrate binding discipline, idempotency-key recipes, v2.39 Reading B, Reading-D) + the operator-named external patterns above, so the deferral does not block the brief. **Continuation contract:** a NotebookLM corpus query + vendor-doc retrieval for the three patterns above is owed at the ratification arc to ground Reading (a) implementation, if DP-2 ratifies a real recovery loop.

---

## DP-3 — pause/resume disambiguator derivation (`pause_event_id`, `resume_event_id`, `resume_attempt_count`)

**Gap:** the engine-layer composers require disambiguator kwargs **not derivable from the engine-layer types** at HEAD: `pause_event_id` is not a field on `PauseEvent` (`:59`); `resume_event_id` + `resume_attempt_count` are not fields on `ResumeAttempt` (`:76`) / `ResumeOutcome` (`:104`). Open carry from runtime plan v2.39 §0.4(b); flagged at v2.34 AC #8 ("If absent at HEAD → Class 1 fork; do NOT invent fields at runtime axis = X-AL-3"). **Unlike the HITL `semantic_variant_binding_id` (closed at v2.39 Reading B), this was never resolved.**

**Decision:** where do these identities come from?

- **(a) Recovery-loop-context-supplied (opaque, caller-provided)** — the DP-2 recovery loop mints a stable `pause_event_id` / `resume_event_id` per recovery event and increments a `resume_attempt_count` per retry, passing them as opaque strings/ints (exactly the precedent the HITL `tool_call_id` set: "caller-provided opaque ... analogous to `workflow_id`/`step_id` opacity", v2.39 §1.2). **No type-field extension; no spec amendment.** **Recommended** — it is the structural twin of the ratified HITL Reading B, and the recovery loop is the natural, legitimate owner of these identities (it is not "inventing" them — they are its own loop state).
- **(b) Type-field extensions** — add `pause_event_id` to `PauseEvent`, `resume_event_id`/`resume_attempt_count` to `ResumeAttempt`/`ResumeOutcome` (CP spec v1.26 → v1.27 amendment). Heavier; cascades to the engine types + their tests.
- **(c) CP spec amendment defining a derivation formula** — specify deterministic derivations (e.g. `pause_event_id = sha256(workflow_id, step_id, snapshot_hash)`). Risks coupling identity to mutable state; less flexible than (a).

**Replay-safety requirement (binds all readings):** the chosen derivation MUST yield **stable** ids and a consistent `resume_attempt_count` so the idempotency keys (`pause_resume_protocol.py:833`/`:938`) dedup on replay — a fresh-uuid-per-call defeats `IDEMPOTENT_NOOP`.

**Recommendation:** **(a)** — mirrors the ratified HITL Reading B, zero type/spec extension, recovery-loop is the legitimate identity owner. Bundle DP-3 ratification with DP-2 (they share the recovery-loop owner).

---

## Bundling + sequencing

Runtime plan v2.39 §0.4 already recommended **sibling-bundling** the HITL firing-site arc with the U-CP-34 firing-site arc. Extending that: DP-1/DP-2/DP-3 + the `class_1_fork_u_cp_78` type impedance should be **ratified together** (they are one R-CXA-2 producer arc), then a single staged implementation plan authored post-ratification per the design brief §5. The Class 1 type-impedance fork is a precondition for DP-2/DP-3's pause-captured producer.

## Acceptance (on ratification)
- DP-1/DP-2/DP-3 each ratified to a reading (or to bounded-residual-defer with a documented re-open trigger).
- If any DP ratifies a real producer loop, the design brief §3.7 / §4.7 acceptance criteria + tests apply.
- If any DP ratifies bounded-residual-defer, the honest X-AL-2 carry is recorded (no hollow wiring) per `[[r-cxa-seam-wiring-is-producer-discovery]]`.

## Cross-axis observability
Closure-back-reference owed here at each DP ratification. Composes with `class_1_fork_u_cp_78_pause_captured_type_impedance.md` (precondition for DP-2/DP-3 pause-captured) and the CLOSED `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` lineage.
