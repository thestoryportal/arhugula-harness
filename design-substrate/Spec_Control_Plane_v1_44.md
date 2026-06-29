# Spec: Control Plane — v1.44 (delta over v1.43)

---

## Change-note (v1.43 → v1.44)

**Scope of revision.** One additive carrier type + one additive `PauseSnapshot` field on **C-CP-26 PauseResumeProtocol §26.2**, materializing the cleared **§25.15.1 `pause → PAUSED`** row for the `PARALLELIZATION` (peer fan-out) topology:

- **`PeerFanOutResumeState`** (NEW §26.2 carrier) — the `PARALLELIZATION`-shaped sibling of the v1.42 `FanOutResumeState`. `PARALLELIZATION` is a PEER fan-out: every declared `WorkflowStep` is a branch (`branch_index = steps` ordinal), with NO orchestrator `steps[0]`. So this carrier has NO `orchestrator_output` / `orchestrator_step_id` (2 fields: `branches: tuple[FanOutBranchResumeState, ...]`, `branch_count: int` — the peer analogues of `FanOutResumeState.branches` + `worker_count`). It **REUSES** the v1.42 `FanOutBranchResumeState` per-branch carrier unchanged (already strategy-neutral; its `branch_index` / `step_id` docstrings are refreshed to cover the peer-branch use — `steps[branch_index]` for PARALLELIZATION vs `worker_steps[branch_index]` for ORCHESTRATOR_WORKERS).
- **`PauseSnapshot.peer_fan_out_resume: PeerFanOutResumeState | None = None`** (NEW §26.2 field, additive + defaulted) — present ONLY when the snapshot captures a `PARALLELIZATION` `cascade_policy=pause` halt; **NEVER co-set with `fan_out_resume`** (the strategy that captured the pause populates exactly one). **COVERED by `snapshot_hash`** (only when non-`None`, so every pre-existing snapshot — linear, single-step, OR ORCHESTRATOR_WORKERS fan-out — hashes byte-identically and still validates).

This is the **R-FS-1 standalone arc `B-FANOUT-PAUSE-PARALLELIZATION`** (registered at `.harness/beyond-mvp-capability-boundary-ledger.md`; the **`B-PARALLELIZATION-CASCADE`** prerequisite — the cascade_policy harvest this resume builds on — closed first at PR #678, since PARALLELIZATION had NO cascade machinery before that arc). It closes the interim `parallelization-pause-resume-not-yet-materialized` FAILED (the `pause` branch flips FAILED → genuine resumable PAUSED, mirroring the v1.42 `B-FANOUT-PAUSE` arc for ORCHESTRATOR_WORKERS).

**§25.15.1 `pause → PAUSED` is now MATERIALIZED for `PARALLELIZATION` — impl-to-cleared-spec, NO operator gate.** Exactly the v1.42 reasoning, re-applied: the §25.15.1 row already commits, byte-exact, `pause → PAUSED` "composing with C-CP-26 PauseResumeProtocol + C-RT-35 `api.resume`", and §25.15.2 obligation 7 already commits ledger-based resume reconstruction. The only thing missing was the **carrier shape** — a peer fan-out paused at the branch barrier has no orchestrator output to recover and no single `step_index` representing which branches completed vs. need re-dispatch, and the completed branches' **outputs** do not survive in the ledger (it carries causality + `terminal_status`, NOT the dispatch output mapping). `PeerFanOutResumeState` supplies both.

**Carrier shape — a NEW peer carrier, NOT a loosened `FanOutResumeState` (illegal-states-unrepresentable).** Reusing the orchestrator-bearing `FanOutResumeState` (loosening its required `orchestrator_output` / `orchestrator_step_id` to optional) was rejected: it would make `orchestrator_output=None` *representable* for an ORCHESTRATOR_WORKERS snapshot — an illegal state for that strategy — and force the existing resume-body-mismatch guard to defend a `None` it currently cannot see. A new 2-field peer carrier keeps each strategy's resume state exactly as constrained as its domain (advisor-resolved; reversible in-impl design fork, NOT an operator gate). The second-additive-field route (`peer_fan_out_resume`, not a union over `fan_out_resume`) preserves the v1.42 additive discipline (every existing `PauseSnapshot` composes + validates unmodified).

**Materializes the R-CC-1 design §1.1 re-open trigger (a documented design evolution, NOT a committed-invariant sacrifice → NO operator gate).** Same as v1.42 §3: the completed-branch outputs are the working-state that must survive the pause; R-CC-1 arc-3 design §1.1 explicitly anticipates this extension. Adopt-and-note + clearance under the FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`), NOT an operator gate (`[[feedback-gate-only-on-meaningful-architecture-change]]`).

**Honest no-false-PAUSED preserved.** A PAUSED is returned ONLY when a `pause_resume_protocol` is bound so a snapshot CAN be captured; without the opt-in the peer fan-out fails loud (FAILED + `parallelization-pause-resume-protocol-not-bound`, the detect-then-refuse mirror of `api.resume`'s `ResumeProtocolNotBoundError`). The deadline-strike case (a STUCK fan-out, no branch raised) stays FAILED — no clean pause boundary. The pause semantic per §25.15.1 ("in-flight finish; not-yet-dispatched left re-dispatchable"): in-flight siblings finish (terminal); the not-yet-dispatched ones are LEFT re-dispatchable (NO `cancelled` terminal — the cascade-cancel obligation-4 scan is deliberately NOT run on the `pause` path); a failed branch is recorded `completed` (dispatch-boundary, effect may have landed) → terminal → not re-dispatched (obligation 7 + at-most-once).

**Resumed-terminal PARTIAL (v1.42 §2 carried).** When a resumed peer fan-out reaches a clean terminal, the run-level status reflects whether ANY branch — recovered OR freshly re-dispatched — ultimately FAILED: a terminal branch with no recovered/collected output yields `RunStatus.PARTIAL` (degraded, salvaged), NOT a bare `SUCCESS` that silently drops the failure (mirrors the `proceed`-cascade `any_failed → PARTIAL`).

**Hash-coverage is load-bearing.** The resumed aggregate TRUSTS the recovered completed-branch outputs, so `_compute_snapshot_hash` covers `peer_fan_out_resume` when present; a tampered recovered output fails `attempt_resume`'s recompute → `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`. A material-diff guard fails closed when the resumed body's `branch_count` differs from the captured one OR a recovered branch's `step_id` no longer matches the re-supplied `steps[branch_index]` (a same-count rename/reorder).

**Scope — `PARALLELIZATION` only; the other non-linear strategies remain registered forward arcs.** `EVALUATOR_OPTIMIZER` (`B-FANOUT-PAUSE-EVALUATOR-OPTIMIZER`), `DECENTRALIZED_HANDOFF` (`B-HANDOFF-PAUSE`), and `HIERARCHICAL_DELEGATION` (`B-HIERARCHICAL-PAUSE`) each keep their own `*-pause-resume-not-yet-materialized` FAILED branch.

**v1.43 + prior body PRESERVED VERBATIM.** All v1.43 content — incl. the v1.43 C-CP-02 §2.5.3 L3-effective-budget amendment (`B-LAYER-BUDGET-OVERRIDE`), the v1.42 §26.2 fan-out resume carriers + `PauseSnapshot.fan_out_resume` field, and the entire C-CP-01 … C-CP-29 body incl. §25.x / §26.x — is PRESERVED VERBATIM per the delta-only-spec-file convention; the **only** changes are the additive `PeerFanOutResumeState` carrier + the additive `PauseSnapshot.peer_fan_out_resume` field below, plus the §25.15.1 PARALLELIZATION materialization note and the `FanOutBranchResumeState` strategy-neutral docstring refresh.

---

## §1 — Amended C-CP-26 §26.2 PauseResumeProtocol type carriers (additive)

The §26.2 carrier set gains **one additive type carrier** + the §26.2 `PauseSnapshot` envelope gains **one additive, defaulted field** (preserving all existing §26.2 carriers + fields verbatim, incl. the v1.42 additions):

> **`PeerFanOutResumeState` (NEW at v1.44).** A frozen `extra="forbid"` model — the peer fan-out (`PARALLELIZATION`) resume reconstruction state. Fields: `branches: tuple[FanOutBranchResumeState, ...]` (the terminal branches at pause time — IS the persisted per-branch `terminal_status` obligation 7 reads; a branch ordinal absent is left re-dispatchable); `branch_count: int` (the declared branch count `len(steps)` at pause time — bounds the re-dispatchable set + a material-diff guard at resume). NO `orchestrator_output` / `orchestrator_step_id` (a peer fan-out has no orchestrator `steps[0]`). REUSES the v1.42 `FanOutBranchResumeState` per-branch carrier.

> **`PauseSnapshot.peer_fan_out_resume: PeerFanOutResumeState | None = None` (NEW at v1.44).** Present ONLY when this snapshot captures a `PARALLELIZATION` `cascade_policy=pause` halt; `None` otherwise; NEVER co-set with `fan_out_resume`. **COVERED by `snapshot_hash`** when non-`None` — the key is added to the canonical hash dict ONLY when present, so existing snapshots (linear / single-step / ORCHESTRATOR_WORKERS) are byte-identical and still validate. `api.resume` re-enters the `PARALLELIZATION` strategy with it: terminal branches skipped (outputs recovered), absent ordinals re-dispatched (§25.15.2 obligation 7).

> **`FanOutBranchResumeState` docstring refresh (strategy-neutral; NO field/shape change).** The `branch_index` / `step_id` field docstrings are refreshed to note the carrier serves BOTH strategies: the orchestrator fan-out re-derives identity from `worker_steps[branch_index]`, the peer fan-out from `steps[branch_index]`. No field added, removed, or retyped — the v1.42 model shape + hash are byte-identical.

The existing §26.2 carriers (`WorkflowPauseReason`, `MaterialDiffPolicy`, `FanOutBranchResumeState`, `FanOutResumeState`, `PauseSnapshot`'s prior fields incl. v1.42 `fan_out_resume`, `ResumeResult`, `ResumeContext`) and §26.3–§26.8 are PRESERVED VERBATIM. The new field is additive + defaulted, so every existing `PauseSnapshot` construction / serialized record composes + validates without modification.

---

## §2 — §25.15.1 `pause → PAUSED` materialization note (PARALLELIZATION)

§25.15.1 (PRESERVED VERBATIM) maps `pause → PAUSED` "composing with C-CP-26 PauseResumeProtocol + C-RT-35 `api.resume`". As of this arc that composition is **materialized for `PARALLELIZATION`**: a branch failure under `cascade_policy=pause` (with a bound `pause_resume_protocol`) captures a `PeerFanOutResumeState`-bearing `PauseSnapshot` + returns `RunStatus.PAUSED`; `api.resume` re-enters the strategy, skips the terminal branches (recovering their outputs from the snapshot, obligation 7), and re-dispatches the not-yet-dispatched ones. The interim `parallelization-pause-resume-not-yet-materialized` FAILED is retired for `PARALLELIZATION` (the only honest-FAILED remaining on the `pause` path is the protocol-not-bound detect-then-refuse + the deadline-strike no-clean-boundary case).

**This corrects the v1.42 §2 scope note's PARALLELIZATION forward-arc line** (preserved verbatim through v1.43). v1.42 §2 listed `PARALLELIZATION` among "registered forward arcs" with a `*-pause-resume-not-yet-materialized` FAILED branch; this arc materializes it. The other three non-linear strategies' forward arcs stand.

---

## §3 — Status

One additive §26.2 carrier (`PeerFanOutResumeState`) + one additive `PauseSnapshot.peer_fan_out_resume` field + a strategy-neutral `FanOutBranchResumeState` docstring refresh, absorbing the FULL-SPEC-pre-authorized R-FS-1 standalone arc `B-FANOUT-PAUSE-PARALLELIZATION` — resumable `cascade_policy=pause` peer fan-out for `PARALLELIZATION`. Impl-to-cleared-spec on the §25.15.1 `pause → PAUSED` row + §25.15.2 obligation 7; materializes the R-CC-1 design §1.1 re-open trigger for the peer fan-out case.

**No operator gate.** Additive carrier + opt-in (PAUSED only when the protocol is bound; else honest FAILED); no committed invariant sacrificed (§1.1 is a self-documented MVP re-open, not a forbidding invariant; the carrier-shape fork is a reversible in-impl design choice resolved by advisor); `snapshot_hash` extended (strengthens §26.6 invariant 2, never weakens it); no new ADR / enum / CXA edge / manifest field. Existing snapshots byte-identical.

Apply pass: this delta co-published with the harness-cp impl (`pause_resume_protocol_types.py` `PeerFanOutResumeState` + `PauseSnapshot.peer_fan_out_resume`; `pause_resume_protocol.py` hash + `capture_pause_snapshot(peer_fan_out_resume=)` + `attempt_resume` recompute; `workflow_driver.py` `_execute_parallelization` capture + resume re-entry threaded through `execute_workflow` / `_execute_workflow_body`) + the harness-runtime `durable_pause_resume_protocol.py` forwarding + by-execution tests (`test_workflow_driver_parallelization_pause.py` real-entry-point witness + negative controls + integrity + JSON round-trip; `test_b_fanout_pause_parallelization_resume_e2e.py` full-runtime `api.resume` e2e) + fork/build record at the spine ledger + clearance marker, per workspace `CLAUDE.md` §11.4 bundled-absorption.

v1.43 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. The entire C-CP-01 … C-CP-29 body + §25.x + §26.x (except the additive `PeerFanOutResumeState` carrier + the additive `PauseSnapshot.peer_fan_out_resume` field + the `FanOutBranchResumeState` docstring refresh) PRESERVED VERBATIM. IS spec UNCHANGED (no §5.2 hash-recipe / §16.5.4 key change — `PauseSnapshot` is not a ledger entry). Runtime spec UNCHANGED at the contract level (the snapshot threads opaquely through `api.resume` → `pause_snapshot_input=`). CXA v2.20 UNCHANGED. ADR-F1/F2/F3/D1–D6 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED.

Clearance marker filed at `.harness/clearance/Spec_Control_Plane-v1_44-cleared-2026-06-21.md`.

2026-06-21.
