# Class 1 Tension — U-CP-49 engine-layer pause/resume free-functions firing-site absence

| Field | Value |
|---|---|
| Status | ✅ RATIFIED-AS-READING-D (bounded-defer per X-AL-2; structurally-unfireable-at-MVP) — 2026-05-29 |
| Filed | 2026-05-29 |
| Filed by | Operator + Claude (post-PR-#68 close, design-phase posture) |
| Class | 1 (architectural; LANDED-substrate-pending-upstream-loop-substrate; THIRD instance of this sub-species pattern in 24 hours after PR #67 HITL `rewrite_tool_call` + sibling-ledger `emit_sibling_ledger_entry`) |
| Triggers | Upstream blocker (4) for H_T-RT-35 RETIRE-READY per checkpoint 2026-05-29; LAST OPEN-no-fork-doc blocker (post PR #68 bootstrap-emission filing) |
| Halt scope | None at execution-time (engine-layer surface is at C-CP-22 §22.1; workflow-layer surface at C-CP-26 §26 is LANDED + production-active); back-flow scope for architectural disposition on engine-layer recovery loop |

---

## §1 Finding

Two free-functions at `harness-cp/src/harness_cp/pause_resume_protocol.py` raise `NotImplementedError` at HEAD `592f0ba`:

- `capture_pause_snapshot(workflow_id, pause_reason) -> PauseEvent` at `:106-125`
- `attempt_resume(attempt: ResumeAttempt) -> ResumeOutcome` at `:128-147`

These are the engine-layer surface per CP spec v1.26 §C-CP-22 §22.1. They compose against IS substrate (U-IS-08 canonicalize+hash + U-IS-09 chain construction + U-IS-11 F2 append + U-IS-12 bounded-read) per docstrings + plan body.

Per CP spec v1.11 §26 NEW NOTE (preserved verbatim through v1.27), the engine-layer surface **coexists** with the workflow-layer C-CP-26 `PauseResumeProtocol` class at distinct architectural layers:

- **Engine-layer** (C-CP-22 §22.1): replay-pause for crash recovery + timeout (ResumptionKind CRASH_RECOVERY + TIMEOUT) — engine-internal lifecycle events.
- **Workflow-layer** (C-CP-26 §26.1): explicit-pause for operator-initiated pause + material-diff resume — LANDED at U-CP-63 (PR landing); production-active.

The workflow-layer class is the one wired at `workflow_driver.py:562 + 789 + 932`. The engine-layer free-functions have ZERO production callers — verified via grep:

```
ResumptionKind.CRASH_RECOVERY  → 0 production hits
ResumptionKind.TIMEOUT         → 0 production hits
capture_pause_snapshot (free)  → 0 production hits at harness-runtime/src/ (all hits route to protocol.capture_pause_snapshot member method)
attempt_resume (free)          → 0 production hits at harness-runtime/src/ (all hits route to protocol.attempt_resume member method)
```

The engine-layer recovery loop (crash-restart bootstrap path + timeout-restart path) does NOT exist at MVP. The runtime plan v2.38 STRUCK U-RT-111 AC #10 e2e scope from 3 sites to 1 (pause-resume workflow-layer only), explicitly excluding engine-layer pause-resume from e2e coverage on this finding.

---

## §2 Empirical orientation (HEAD `592f0ba`)

| Surface | Path | State |
|---|---|---|
| Engine-layer `capture_pause_snapshot` (free) | `harness-cp/src/harness_cp/pause_resume_protocol.py:106-125` | LANDED stub (NotImplementedError) |
| Engine-layer `attempt_resume` (free) | `harness-cp/src/harness_cp/pause_resume_protocol.py:128-147` | LANDED stub (NotImplementedError) |
| Engine-layer `classify_resume` (free) | `:150-163` | LANDED concrete impl (pure decision core, deterministic) |
| Workflow-layer `PauseResumeProtocol.capture_pause_snapshot` (method) | `:263+` | LANDED + production-active |
| Workflow-layer `PauseResumeProtocol.attempt_resume` (method) | `pause_resume_protocol.py` | LANDED + production-active |
| U-CP-50 `material_diff_detection.py` | `harness-cp/src/harness_cp/material_diff_detection.py` | LANDED concrete impl (NEW finding 2026-05-29: previously assumed gap; ZERO NotImplementedError) |
| Production callers of engine-layer free-functions | (none) | **ABSENT** |
| Production callers of `ResumptionKind.CRASH_RECOVERY` | (none) | **ABSENT** |
| Production callers of `ResumptionKind.TIMEOUT` | (none) | **ABSENT** |
| Engine-layer replay loop / crash-recovery bootstrap path | (does not exist at MVP) | **NOT BUILT** |
| Workflow-layer class production callers | `workflow_driver.py:562 + 789 + 932` | LANDED + active |
| harness-cp pyproject.toml deps | `harness-core + harness-as` only | harness-is NOT a direct dep |
| U-RT-111 AC #10 v2.38 scope reduction | runtime plan v2.38 | STRUCK engine-layer site; workflow-layer site only |

**Decisive finding**: the engine-layer surface is structurally unfireable at MVP because the upstream engine-layer recovery loop (crash-restart bootstrap path; timeout-restart path) does not exist. U-CP-50 (material-diff detection, previously feared as co-stub) IS LANDED — only U-CP-49 stubs persist.

---

## §3 Readings

### §3.1 Reading A — Implement engine-layer free-functions via runtime-side composition

Author the free-function bodies at harness-cp/src/harness_cp/pause_resume_protocol.py, threading IS-substrate via runtime-side dependency injection (mirror PR #68 Reading B' narrow-dep-injection precedent for engine_selector). harness-cp gains threaded `ledger_writer` + `ledger_reader` params; runtime composes the binding chain at appropriate bootstrap stage.

**Pros:** closes the LANDED-stub state at the substrate layer; engine-layer surface becomes invokable when the upstream recovery loop is later authored.

**Cons:** authors substrate against a NOT-BUILT upstream loop — same pattern as PR #62 v2.39 (catalogued at `[[2.strike-revision-on-refined-second-tier-reason]]`). The substrate would land with ZERO production callers; first call would happen at recovery-loop authoring time (separate future arc). Snapshot serialization format is deferred to impl discretion per §22.1 — locking it now at first impl risks downstream rework when the actual crash-recovery requirements surface. Could violate X-AL-2 second conjunct (substituted H_E surface no longer invoked — but engine-layer is NOT substituted at MVP per Meta-Arch §5.4; this is a phantom-substitution-retirement concern).

### §3.2 Reading B — Author engine-layer recovery loop AS PART OF this arc

Author the engine-layer crash-recovery + timeout-restart bootstrap path. New runtime substrate at `harness-runtime/.../lifecycle/` for: crash detection (e.g., on bootstrap, scan IS state-ledger for INCOMPLETE workflow runs) + replay invocation (route to engine-layer free-functions) + timeout-restart trigger (e.g., on workflow timeout, capture pause snapshot + attempt resume with elapsed-time material-diff).

**Pros:** closes the architectural gap end-to-end; engine-layer surface gains a real firing site; addresses the structural root cause.

**Cons:** MASSIVE scope — multi-arc decomposition; touches CP TopologyPattern semantics (replay path topology?); touches IS state-ledger reader at bootstrap; touches OD audit-ledger emission for replay events; potentially requires ADR-class decision on crash-recovery semantics (best-effort vs guaranteed; what counts as "INCOMPLETE workflow"?); requires e2e test substrate against actual crash scenario. Likely 3-6 PRs minimum across multiple sessions. Far exceeds H_T-RT-35 RETIRE-READY closure scope.

### §3.3 Reading C — Reframe §C-CP-22 §22.1 scope to workflow-layer-only at MVP

Spec amendment that REFRAMES §C-CP-22 §22.1 to declare engine-layer recovery as out-of-MVP-scope; canonical pause-resume surface narrows to C-CP-26 §26 workflow-layer at v1.6 MVP. Engine-layer free-functions removed from the substrate (or marked as DEFERRED-TO-POST-MVP).

**Pros:** aligns spec with implementation reality (workflow-layer is the operative surface; engine-layer is aspirational); removes a known carrier-without-firing-site; cleanest spec hygiene.

**Cons:** requires CP spec amendment + likely ADR-D1 v1.2 reconsideration (engine + replay anchor — D1 declares 5-class EngineClass including CRASH_RECOVERY / TIMEOUT semantics); cascades into ResumptionKind 5-class taxonomy validity (do CRASH_RECOVERY + TIMEOUT remain as enum members without surface?); high cross-axis cascade risk.

### §3.4 Reading D — Bounded-defer per X-AL-2; structurally-unfireable-at-MVP

Acknowledge that engine-layer free-functions are structurally unfireable at MVP because the engine-layer recovery loop does NOT exist. Defer the firing-site arc until the engine-layer recovery loop is authored (Reading B path) OR explicitly reframe spec scope (Reading C path). Maintain U-RT-111 AC #10 e2e reduction at v2.38 (workflow-layer site only) per current runtime plan.

**Pros:** matches v2.37 U-CP-34 STRIKE + v2.38 AC #10 reduction + PR #67 HITL/sibling-ledger bounded-defer precedents (THIRD instance of LANDED-substrate-pending-upstream-loop-substrate sub-species pattern in 24 hours); preserves architectural coherence; avoids premature substrate authoring against not-yet-built upstream; aligns with `Phase_7_Meta_Architecture_v1.md` §6 self-hosting milestone gradient (engine-layer replay is a downstream milestone, not MVP); does not advance H_T-RT-35 toward RETIRE-READY at this arc but closes the fork-doc-level OPEN question.

**Cons:** does not advance H_T-RT-35 toward RETIRE-READY at this arc; LANDED stubs sit as bounded-residual carry-forward; sub-species 7.deployment-time-opt-in-gate does NOT apply (no production opt-in path even possible until upstream loop exists).

### §3.5 Why Reading D applies (mirror PR #67 framing; inverse of PR #68 §3.5)

This is the THIRD instance of the same sub-species in 24 hours:

| Fork | Substrate | Upstream loop | Disposition |
|---|---|---|---|
| PR #67 HITL `rewrite_tool_call` | LANDED (composer + wiring) | LLM inner tool-call interception loop NOT BUILT | Reading D bounded-defer |
| PR #67 sibling-ledger `emit_sibling_ledger_entry` | LANDED (composer + wiring) | Recursive-harness recursion boundary NOT BUILT | Reading C bounded-defer |
| **This fork** U-CP-49 engine-layer free-functions | LANDED (stub bodies + plan AC) | Engine-layer recovery loop NOT BUILT | **Reading D bounded-defer** |

Distinct from PR #68 bootstrap-emission-substrate where the gap was binding-chain ordering (downstream substrate LANDED + firing-site reachable + only the wiring connecting them was broken). Here, the downstream surface IS THE STUB; the upstream loop that would invoke it does NOT exist.

The sub-species pattern is "LANDED-substrate-pending-upstream-loop-substrate" — cardinality 3 in 24 hours is empirical evidence for workflow v1.13 §7.4.7.2 species addition (candidate noted at §"Adjacent observations" below).

---

## §4 Q-set for operator ratification

| Q | Decision space |
|---|---|
| Q1 | Reading: A (impl now via runtime composition; substrate-first) / B (impl recovery loop end-to-end; multi-arc) / C (spec reframe engine-layer out of MVP scope) / D (bounded-defer; recommended) |
| Q2 (if A) | Snapshot serialization: (i) JSON canonical bytes via `_canonicalize_outcome_bytes` helper precedent; (ii) Pydantic model_dump_json with sorted keys; (iii) implementer-discretion per §22.1 |
| Q3 (if B) | Recovery-loop entrypoint: (i) bootstrap stage 7 INGRESS_ACCEPT crash-scan; (ii) NEW dedicated stage; (iii) workflow_driver outer wrapper; (iv) ADR-class scope (file ADR before fork) |
| Q4 (if C) | Spec reframe shape: (i) §22.1 marked DEFERRED-TO-POST-MVP; (ii) §22.1 removed; (iii) ResumptionKind enum prune to workflow-applicable values only; (iv) v1.6 MVP scope carve-out per §14.7.2 step 5 precedent |
| Q5 (any) | Cross-axis cascade: (α) intra-CP-axis only (Reading D); (β) CP + IS + OD cascade (Reading B); (γ) CP spec + ADR-D1 amendment (Reading C); (δ) full ADR-class deliberation (Reading B/C) |
| Q6 (any) | Sub-species cardinality: (i) catalogue `LANDED-substrate-pending-upstream-loop-substrate` as NEW workflow v1.13 §7.4.7.2 species at follow-on workflow-doc revision arc (cardinality 3 in 24 hours threshold met); (ii) carry as candidate awaiting one more empirical instance per `[[u-rt-59-overlooked-sibling-pattern-deferred-pending-cardinality]]` precedent; (iii) NOT catalogued (treat as PR #67 + this fork as 3 ad-hoc instances) |
| Q7 (any) | H_T-RT-35 transit posture: bounded-defer this arc + 3 sibling closures + 1 FORK-DOC-FILED (PR #68) = 5/5 upstream blockers reach FORK-DOC-FILED-or-better state. RETIRE-READY transit gated only on PR #68 ratification + apply. (α) accept this framing; (β) require additional gating |

---

## §5 Cross-axis cascade analysis

| Axis | Touch under each Reading |
|---|---|
| IS | Reading A: cross-axis dep injection (mirror PR #68 B'); requires runtime-side composition. Reading B: MAJOR — state-ledger scan at bootstrap; replay-aware reader. Reading C: NONE. Reading D: NONE. |
| AS | NONE across all readings. |
| CP | Reading A: composer signature widening at §22.1 surface. Reading B: NEW §C-CP-NN crash-recovery contract + ResumptionKind enum extension to ACTIVE state. Reading C: §22.1 amendment + ADR-D1 reconsideration. Reading D: NONE. |
| OD | Reading B: cost-attribution + audit-ledger for replay events. Other readings: NONE. |
| CXA | Reading A: possible new typed edge if runtime composition crosses fresh boundary. Reading B: many new edges. Other readings: NONE. |
| Runtime spec | Reading A: NEW factory at stage N for engine-layer composer binding. Reading B: NEW §14.X crash-recovery lifecycle contract. Reading C: NONE. Reading D: NONE. |

---

## §6 Recommendation

**Pre-substantive recommendation:** **Reading D (bounded-defer)** is the structurally-coherent disposition at MVP scope. The engine-layer recovery loop does NOT exist; authoring substrate (Reading A) against a not-yet-built upstream replays the v2.37 U-CP-34 / PR #62 v2.39 pattern (premature wiring against not-yet-built downstream substrate). Reading B (build the recovery loop) is ADR-class scope multi-arc work that exceeds H_T-RT-35 RETIRE-READY closure scope. Reading C (spec reframe) is a workaround that risks shoehorning an architectural decision about engine-layer pause-resume semantics that v1.27 §22.1 + ADR-D1 v1.2 + ResumptionKind 5-class enum were designed to encode.

Sub-species cardinality 3 in 24 hours strengthens the empirical case: Reading D applies uniformly across all 3 instances of this pattern this session (HITL, sibling-ledger, engine-layer free-functions).

If operator prefers immediate closure path: Reading D + Q6=(i) catalogue sub-species at next workflow-doc revision + Q7=(α) accept 5/5 blocker FORK-DOC-FILED-or-better framing.

If operator prefers building toward H_T-RT-35 RETIRE-READY active production: Reading B (recovery loop authoring) is the architecturally-canonical long-term path, but it is multi-arc + ADR-class. Filing Reading B as the recommended-long-term + Reading D as the recommended-this-arc preserves both forward direction and present-arc coherence (mirror PR #67 sibling-ledger Reading B/C dual framing).

**Filing posture this arc**: file-only per workspace pattern (mirror PR #65 + PR #68). Ratification (likely Reading D) deferred to fresh session; ratification mechanism is mechanical given the empirical clarity (mirror PR #67 ratification pattern).

---

## §7 Session-end H_T-RT-35 transit posture (with this fork filed)

Post-filing of this fork doc:

| # | Blocker | State |
|---|---|---|
| 1 | U-CP-14 disambiguator | ✅ APPLIED (PR #66 merged `6786a59`) |
| 2 | HITL `rewrite_tool_call` | ✅ RATIFIED-AS-READING-D bounded-defer (PR #67 merged `592f0ba`) |
| 3 | Sibling-ledger recursion boundary | ✅ RATIFIED-AS-READING-C bounded-defer (PR #67 merged `592f0ba`) |
| 4 | Bootstrap-emission-substrate | ✅ FORK-DOC-FILED PROPOSING (PR #68 OPEN at `278e0f8`) |
| 5 | U-CP-49 engine-layer free-functions | ✅ FORK-DOC-FILED PROPOSING (THIS PR) |

**5 of 5 upstream blockers reach FORK-DOC-FILED-or-better state.** H_T-RT-35 RETIRE-READY transit is gated only on:
- PR #68 ratification + apply (Reading B' narrow dep injection recommended)
- This fork's ratification (Reading D bounded-defer recommended) — no apply pass needed

Both ratifications are mechanical given empirical clarity. Once ratified, H_T-RT-35 transits PARTIAL → RETIRE-READY.

---

## §8 Adjacent observations

**(a) Sub-species candidate: `LANDED-substrate-pending-upstream-loop-substrate`** — workflow v1.13 §7.4.7.2 species addition candidate. Cardinality 3 in 24 hours (HITL + sibling-ledger at PR #67 + this engine-layer fork). Common-ancestor closure-event-class: LANDED-substrate (composer + wiring + carrier) with ZERO production callers AT MVP because the upstream loop / recursion / recovery substrate is NOT BUILT. Distinct from species 2 (strike-revision-on-refined-second-tier-reason) and species 3 sub-species catalogue (resolved-but-carry-stale-inherited). Routing target: workflow doc revision when cardinality build-up warrants per `[[u-rt-59-overlooked-sibling-pattern-deferred-pending-cardinality]]` precedent.

**(b) U-CP-50 LANDED status correction** — pre-substantive empirical orientation at this fork's filing revealed U-CP-50 (material-diff detection) IS LANDED (`material_diff_detection.py` concrete impl; ZERO NotImplementedError). Prior checkpoint framing implied U-CP-50 was co-stub with U-CP-49 — empirically false. Scope adjusted at filing.

**(c) Workflow-layer C-CP-26 coexistence** — the LANDED workflow-layer class at `pause_resume_protocol.py:214+` (PauseResumeProtocol with member methods `capture_pause_snapshot` + `attempt_resume`) is production-active per `workflow_driver.py:562 + 789 + 932`. This fork addresses ONLY the engine-layer free-function surface; workflow-layer surface is unaffected.

**(d) ResumptionKind enum carry** — under Reading D, ResumptionKind.CRASH_RECOVERY + TIMEOUT enum members carry without production callers. This is a bounded-residual per X-AL-2 carry-forward shape; not a defect at v1.6 MVP scope but documented for future re-litigation.

---

## §9 Status posture

| Element | Status |
|---|---|
| Engine-layer `capture_pause_snapshot` (free) | ❌ STUB (NotImplementedError) |
| Engine-layer `attempt_resume` (free) | ❌ STUB (NotImplementedError) |
| Engine-layer `classify_resume` (free) | ✅ LANDED concrete impl |
| Workflow-layer `PauseResumeProtocol` (class) | ✅ LANDED + production-active |
| U-CP-50 material-diff detection | ✅ LANDED concrete impl (correction to prior framing) |
| Production callers of engine-layer free-functions | ❌ ABSENT |
| Engine-layer recovery loop | ❌ NOT BUILT at MVP |
| H_T-RT-35 RETIRE-READY transit | GATED on PR #68 ratification + this fork's ratification |
| Recommended Q1 | (D) bounded-defer |
| Sub-species cardinality (this session) | 3 of 3 fits `LANDED-substrate-pending-upstream-loop-substrate` |
| Sibling arc | PR #67 HITL + sibling-ledger bounded-defer (mirror precedent); PR #68 bootstrap-emission Reading B' (distinct sub-species — binding-chain ordering, not substrate absence) |

---

## §10 Ratification (2026-05-29)

Operator ratified **Q1 = Reading D (bounded-defer)** per pre-substantive recommendation at §6 + empirical clarity of sub-species cardinality 3 at §3.5. Q2–Q7 N/A under Reading D (no spec change, no recovery-loop authoring, no firing-site, no cross-axis cascade).

### Rationale

The engine-layer recovery loop (crash-restart bootstrap path + timeout-restart path) does NOT exist at MVP. Authoring engine-layer free-function bodies (Reading A) against a not-yet-built upstream replays the v2.37 U-CP-34 / PR #62 v2.39 pattern. Reading B (build recovery loop) is ADR-class scope multi-arc work exceeding H_T-RT-35 RETIRE-READY closure scope. Reading C (spec reframe) is a workaround that risks shoehorning ADR-D1 v1.2 + ResumptionKind 5-class enum semantics.

ZERO production callers verified at filing time + 3-instance sub-species cardinality this session = empirical clarity for Reading D as the canonical disposition.

### Carry disposition

- **Engine-layer free-functions** (`capture_pause_snapshot` + `attempt_resume` NotImplementedError stubs) PRESERVED VERBATIM at HEAD as future-applicable carriers per X-AL-2 bounded-residual carry-forward.
- **Engine-layer `classify_resume`** (LANDED concrete impl, pure decision core) PRESERVED VERBATIM — usable now by any future caller without state-ledger composition.
- **Workflow-layer C-CP-26 `PauseResumeProtocol` class** UNAFFECTED — production-active at `workflow_driver.py:562 + 789 + 932`.
- **U-CP-50 `material_diff_detection.py`** UNAFFECTED — LANDED concrete impl available to workflow-layer.
- **ResumptionKind enum** UNAFFECTED — CRASH_RECOVERY + TIMEOUT members carry without production callers as bounded-residual.
- **Re-litigation trigger**: when the engine-layer recovery loop is authored (separate future arc per Phase_7_Meta_Architecture_v1.md §6 self-hosting milestone gradient), re-open this fork doc and select Reading A / B / C for that arc's context.

### Sub-species cardinality catalogue candidate

THIRD instance of `LANDED-substrate-pending-upstream-loop-substrate` in 24 hours (HITL + sibling-ledger at PR #67 + this engine-layer fork). Workflow v1.13 §7.4.7.2 sub-species addition candidate — cardinality 3-in-24-hours threshold MET per `[[u-rt-59-overlooked-sibling-pattern-deferred-pending-cardinality]]` precedent. Routing target: workflow doc revision at follow-on arc.

### Cross-artifact effects

- ZERO design-substrate edit (no spec / plan / ADR / ADD / PRD / CXA amendment).
- ZERO production code change.
- ZERO clearance marker (per CLAUDE.md §4.5 — bounded-defer dispositions without design-substrate edits do not require clearance markers).
- ZERO MEMORY.md retirement-event filing (no retirement-tier transit at this arc).

### H_T-RT-35 transit posture impact

This ratification closes 1 of 2 remaining ratification arcs gating H_T-RT-35 PARTIAL → RETIRE-READY transit. PR #68 bootstrap-emission-substrate fork remains gated on fresh-session rescope (firing-site sourcing Q-set per PR #68 §8 addendum). RETIRE-READY transit awaits PR #68 ratification.

---

*End of fork doc.*
