---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.59
cleared_at: 2026-06-18T19:30:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b_interstep_data_flow.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (line 43 — B-INTERSTEP)
merge_commit: pending (R-FS-1 B-INTERSTEP bundled-absorption PR)
reviewer_chain:
  - advisor (full-transcript) — non-vacuity-is-the-deliverable (build the real consumer, not a hollow channel); flagged the resume-correctness (B-ENGINE-OUTPUT-REPLAY) composition + the all-topologies-vs-genuine-linear scope decision + the dispatcher-purity check
  - out-of-family Codex (pre-merge, on the diff)
  - impl-time grounding pass (worktree off origin/main 9d00f2f)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.59`

v1.59 adds a **NEW contract §14.21 C-RT-34 `InterStepOutputChannel`** — a run-scoped, operator-opt-in **inter-step data-flow channel** (the *"shared run context the dispatcher reads"* that `harness_cp.workflow_driver` §25.11 named). The workflow driver records each completed step's output to it; the C-RT-15 LLM dispatcher injects the immediately-prior step's output into the dispatched provider payload. R-FS-1 standalone `B-*` arc `B-INTERSTEP`, spine ledger line 43 (`design-fork-first per X-AL-3`). Closes the gap where the driver threads only control flow between steps for every topology — most visibly `EVALUATOR_OPTIMIZER` (the evaluator could not see the generate draft; the regenerate could not see the evaluator feedback).

**No operator gate — additive + operator-opt-in.** Gated on a NEW `RuntimeConfig.inter_step_data_flow: bool = False`; default `False` → `ctx.inter_step_output_channel is None` → the driver records nothing + the dispatcher injects nothing → byte-identical to pre-v1.59. The `StepDispatcher.dispatch` signature is UNCHANGED (the channel is read off the dispatcher's construction reference, never a per-call parameter) and §25.3.3.4 step-body-opaque-to-driver is PRESERVED (the driver records the dispatcher's already-produced opaque output Mapping). No committed invariant sacrificed; the mechanism is the one §25.11 named, resolved by landed precedent (the `CostRecordAccumulator` by-ref holder + `cost_record_sink` dispatcher threading + the `cp_is_wiring` `object | None` opt-in) → advisor, not council.

**Genuine consumer (non-vacuity is the deliverable).** The real LLM-dispatcher consumer ships in v1.59: the prior step's output reaches the actual `client.messages.create(messages=...)` call, proven by-execution against the provider boundary — NOT a test stub.

**Genuinely-complete sequential-write scope; remaining surfaces registered.** v1.59 covers `SINGLE_THREADED_LINEAR` + `EVALUATOR_OPTIMIZER` genuinely. Two follow-ons are explicitly registered (§14.21.7 + the spine ledger + the §25.11 driver comment): concurrent-fan-out recording (the 4 remaining non-linear strategies via the #648 buffered-branch drain — ADR-F2; `B-INTERSTEP-NONLINEAR`) + cross-step resume rehydration (composes with `B-ENGINE-OUTPUT-REPLAY` — the F2 `EntryPayload` carries only a `response_hash` digest; EVALUATOR_OPTIMIZER's within-loop data flow is resume-safe).

## Notes

- Scope: ONLY §14.21 (the new contract); all of §9 / §14.x / §14.20 + the existing `RunResult` fields are PRESERVED VERBATIM. No §5.2-hash / IS-spec / OD-spec / CP-spec contract / ADR change; no new fail class (best-effort run-scoped carrier).
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
