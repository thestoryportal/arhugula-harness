---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.64
cleared_at: 2026-06-20T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (NO operator gate — an AMENDMENT closing §14.21.5 invariant 7 + marking the §14.21.7 follow-on B-INTERSTEP-PERRUN-ISOLATION BUILT; additive correctness that REMOVES B-INTERSTEP's single-flight serialization + CLOSES the registered timeout-zombie residual; no committed-invariant sacrifice, opt-out byte-identical; design authority = the B-INTERSTEP fork §3/§5, which prescribed the ContextVar mechanism)
back_reference:
  - .harness/class_1_fork_b_interstep_perrun_isolation.md
  - .harness/class_1_fork_b_interstep_data_flow.md (§3/§5 — the design authority that prescribed the ContextVar mechanism + registered this arc)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-INTERSTEP-PERRUN-ISOLATION spine BUILT entry + the refreshed B-INTERSTEP follow-on mention)
  - .harness/clearance/Spec_Harness_Runtime-v1_59-cleared-2026-06-18.md (B-INTERSTEP — the channel + invariant-7 this amends)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — affirmed the ContextVar + stable-proxy shape (composes with the existing _CURRENT_TOOL_CTX per-task pattern); caught the opt-out byte-identical bug-in-waiting (bind the channel proxy ONLY when opt-in), flagged the always-on cost path as the real risk (full sink-surface enumerated; arc-CA cost tests re-run green) + the child_workflow_runner ContextVar-inheritance blind-spot (verified inherits); confirmed advisor-not-council (no nameable cross-domain tension)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.64`

v1.64 is an additive delta over v1.63 absorbing the **R-FS-1 standalone arc `B-INTERSTEP-PERRUN-ISOLATION`** (the registered B-INTERSTEP follow-on §3/§5). It **closes §14.21.5 invariant 7** — the run-scoped-no-cross-run-leak invariant of the §14.21 C-RT-34 `InterStepOutputChannel`, previously bounded honestly to (a) sequential reuse + (b) concurrent-within-timeout with (c) the `drain_timeout_seconds` TIMEOUT-ZOMBIE as a registered residual — and marks the §14.21.7 follow-on **BUILT**.

**NO operator gate.** B-INTERSTEP allocated its run-scoped channel at bootstrap scope on the frozen `HarnessContext`; in daemon-client mode one ctx serves many concurrent `run_workflow` invocations, so they SHARED the channel. B-INTERSTEP fenced (a)+(b) with a per-loop single-flight LOCK but could not fence (c) — a timed-out, non-cancellable `asyncio.to_thread` worker keeps writing the SHARED holder after the lock releases. This arc replaces the bootstrap-shared holder with a `ContextVar`-bound **per-run** holder behind a stable ctx proxy (the fork-prescribed mechanism), set fresh per run at the `run_workflow` boundary; the set propagates into the `to_thread` worker via `copy_context()`, so (a)+(b) need no lock and (c) is closed (a zombie writes only the holder captured in its OWN context copy). Additive correctness: it REMOVES the serialization + CLOSES the residual, sacrificing no committed invariant; opt-out (channel unbound) is byte-identical. Adopt-and-note under the FULL-SPEC directive; advisor + out-of-family Codex, not council (internal concurrency correctness — no nameable cross-domain tension).

Reviewed during clearance: the empirically-grounded ContextVar propagation across the in-process MCP boundary (caller-set → handler → `to_thread` worker, and handler-set does not leak back to the caller) which drives the api.run-vs-daemon set-site asymmetry; the always-on **cost path** correctness (the per-dispatch cost wrappers now thread the accumulator PROXY, not a `.records` list captured once at bootstrap — the capture that defeated isolation — and `api.run`/`resume` set a fresh accumulator around `[invoke + cost-read]` so the post-run rollup resolves the same accumulator the wrappers appended to); the opt-out byte-identical guard (the channel proxy binds ONLY when `inter_step_data_flow=True`); the other bootstrap-ctx holders' dispositions (`resume_context_holder` set-per-run overwrite, `engine_output_store` run_idempotency_key-keyed, ledger writers ADR-F2 single-writer + run_id-tagged — none need isolation; not a channel-only false-complete); the non-vacuity deliverable (the timeout-zombie test over REAL `asyncio.to_thread` copy_context + its negative control).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- **No §5.2-hash change** (the holders are ephemeral run-scoped carriers, not persisted/hashed state). CP / IS / OD specs UNCHANGED (the CP driver reads the channel via the `getattr` `cp_is_wiring` idiom — no `harness_cp` → `harness_runtime` import; the `cost_record_accumulator` / `inter_step_output_channel` field TYPES are unchanged — the bound values are IS-A-compatible run-scoped proxies).
- See `.harness/clearance/README.md` for marker discipline.
