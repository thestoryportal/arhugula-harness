# Class 2 Build Record — B-INTERSTEP-NONLINEAR (handoff slice): inter-step DATA flow for DECENTRALIZED_HANDOFF

**Filed:** 2026-06-20 · R-FS-1 standalone `B-*` arc **B-INTERSTEP-NONLINEAR**, **handoff slice** (registered follow-on of **B-INTERSTEP**; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md`; runtime spec **§14.21 C-RT-29** §14.21.7 "Concurrent-fan-out recording (registered follow-on `B-INTERSTEP-NONLINEAR`)"). Posture: **impl-to-cleared-spec** — `harness-cp/src` (the handoff driver record site) + `harness-cp` + `harness-runtime` by-execution tests + this build record + ledgers. **NO design-substrate edit** (the §14.21 C-RT-29 contract is cleared; recording for the non-linear topologies is an already-registered §14.21.7 follow-on; the consumer is the existing C-RT-15 dispatcher). Class 2 (in-execution build of a registered follow-on; no operator gate). FULL-SPEC-pre-authorized (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Status:** ✅ RESOLVED + BUILT. **NO operator gate.** Additive + operator-opt-in (default `RuntimeConfig.inter_step_data_flow=False` → `ctx.inter_step_output_channel is None` → the driver records nothing → **byte-identical to pre-arc**); sacrifices **no committed invariant** — the `StepDispatcher.dispatch` signature is UNCHANGED, §25.3.3.4 *step-body-opaque-to-driver* is PRESERVED (the driver records the dispatcher's already-produced opaque output Mapping), and ADR-F2 single-threaded-write holds (the record is INLINE on the driver thread). No nameable cross-domain tension (a runtime/dispatcher data-flow record call mirroring the cleared linear/EO sites) → advisor, **not council** (§10.9 discriminator). Adopt-and-note per `CLAUDE.md` §12.4.1 + `[[feedback-gate-only-on-meaningful-architecture-change]]`.

---

## §1 The slice — DECENTRALIZED_HANDOFF threaded NO inter-step data

B-INTERSTEP (parent, #651/v1.59) shipped inter-step DATA flow for the two **sequential-write** topologies (`SINGLE_THREADED_LINEAR` + `EVALUATOR_OPTIMIZER`) and registered the 4 non-linear strategies as `B-INTERSTEP-NONLINEAR`. At HEAD, `_execute_decentralized_handoff` (`workflow_driver.py:4923`) dispatched each stage-expert but did **NOT** record any stage's output to the channel — so a later stage-expert's dispatch read `most_recent_output() is None` and the handoff carried **control flow only** (ownership-transfer `HandoffContext` records), never the prior stage's *output content*. The `_record_inter_step_output` producer fired only at the linear (`:2535`) and EO (`:3841`) sites.

### §1.1 Why handoff is the cleanest first slice (advisor decision rule)

The advisor's tie-breaker: the right slice is the topology whose **minimal non-vacuous consumer needs no discriminator the spec doesn't give**. The 4 non-linear topologies split:

- **ORCHESTRATOR_WORKERS / PARALLELIZATION / HIERARCHICAL_DELEGATION** — concurrent fan-out. The genuine post-join synthesis consumer wants *all* siblings, but the existing consumer injects only `most_recent_output()` (one arbitrary last-drained sibling). Bridging that is a "consume the fan-out aggregate" signal — a message-shape extension (§14.21.7 bullet 1 impl-discretion) that drags in the all-siblings read. Shipping "synthesis sees one arbitrary worker" would pass a test but be **soft built-but-vacuous** (`[[built-but-vacuous-reground-ledger-asis]]`).
- **DECENTRALIZED_HANDOFF** — single-owner **sequential** (driver lines 4933-4943: "NO fan-out, NO `TaskGroup`"). Records like the linear case (driver thread, no concurrency drain), and `most_recent_output()` is **genuinely the correct read** (stage B sees stage A's output — there is exactly one predecessor). Small, non-vacuous, no message-shape extension, no missing discriminator.

So handoff is the slice; the 3 concurrent topologies are re-scoped under B-INTERSTEP-NONLINEAR (registered).

---

## §2 Resolution — record each completed stage's output INLINE

`_execute_decentralized_handoff`, after a stage completes (`stage_outputs[step_id] = output`, `workflow_driver.py:5137`), calls `_record_inter_step_output(ctx, str(step.step_id), output)` — the SAME helper the linear/EO sites use. The next stage-expert's dispatch reads `most_recent_output()` off the dispatcher's construction reference (the existing C-RT-15 consumer, §14.21.2) and the LLM dispatcher injects it as the `user` "Upstream step output:" message. Single-owner sequential ⟹ recorded **inline on the driver thread**, NOT via the #648 buffered-branch drain (which exists only to serialize *concurrent* sibling writes — structurally absent here). The function docstring is refreshed to disambiguate terminal CONTROL detection (still structural) from inter-step DATA flow (now wired).

### §2.1 Non-vacuity is the deliverable — full-chain witness (no proxy)

Per `[[full-chain-witness-not-half-proofs]]` (producer + consumer in SEPARATE seam-stopping tests = a half-proof), the witness composes the NEW handoff producer + the existing dispatcher consumer **through the real path**:

- **Producer witness** (`harness-cp/tests/test_workflow_driver_decentralized_handoff.py`) — `test_decentralized_handoff_records_inter_step_output_for_next_stage`: a 3-stage handoff records each stage in order; each later stage's dispatch reads its predecessor's output (`seen_upstream == [None, {out:s0}, {out:s1}]`). Plus a **NEGATIVE CONTROL** (`test_decentralized_handoff_opt_out_records_nothing`): opt-out (channel unbound on ctx) → every stage sees `None`, channel empty (byte-identical to pre-arc) — proves the record() wiring is gated on the ctx binding.
- **Full-chain witness** (`harness-runtime/tests/test_lifecycle_llm_dispatch.py`) — `test_decentralized_handoff_inter_step_output_reaches_real_provider_call`: a genuine 2-stage handoff runs through the REAL CP driver (`execute_workflow` → `_execute_decentralized_handoff`) where each stage dispatches through the REAL `RuntimeLLMDispatcher` via the production `SyncDispatcherFacade` async/sync bridge (the `api.py` `asyncio.to_thread` shape). Stage B's ACTUAL provider call (`adapter.client.messages.calls[1]`) carries stage A's distinct output token as the injected "Upstream step output:" message — the model GENUINELY receives the prior stage-expert's output. (An e2e passing UNCHANGED after the producer change cannot witness it; this one fails without the record() call.)

---

## §3 Class-3 informational — §14.21.7 spec imprecision (handoff is sequential, not concurrent)

§14.21.7 (and the parent fork `class_1_fork_b_interstep_data_flow.md` §3) lumps **DECENTRALIZED_HANDOFF** with the 3 genuinely-concurrent topologies under *"concurrent sibling writes … the #648 buffered-branch drain path (ADR-F2)"*. Empirically (driver `workflow_driver.py:4933-4943`), handoff is **single-owner sequential** — it records inline on the driver thread exactly like `SINGLE_THREADED_LINEAR` / `EVALUATOR_OPTIMIZER`, and needs **no** buffered-branch drain. This is a **Class-3 informational** spec imprecision (the spec's INTENT — record completed step outputs to the channel — is honored; only the mechanism-detail "via the buffered-branch drain" is over-broad for handoff). Non-blocking (advisor: "a Class-3 note, not a blocker"); logged here per `CLAUDE.md` §4.3 Class-3 routing. The "buffered-branch drain" mechanism remains correct for the 3 concurrent topologies (B-INTERSTEP-NONLINEAR, registered). A batched spec refresh of §14.21.7 may correct the lumping at the concurrent-topologies arc.

---

## §4 Scope + registered follow-ons (NOT silent-deferred)

| Topology | Disposition |
|---|---|
| `DECENTRALIZED_HANDOFF` | ✅ BUILT (this slice — sequential, inline record) |
| `ORCHESTRATOR_WORKERS` / `PARALLELIZATION` / `HIERARCHICAL_DELEGATION` | **B-INTERSTEP-NONLINEAR** (registered, re-scoped to the 3 concurrent strategies) — concurrent sibling writes need the #648 buffered-branch drain (ADR-F2) + the all-siblings post-join read (the §14.21.7 bullet-1 message-shape discriminator) |
| Cross-step resume rehydration | `B-ENGINE-OUTPUT-REPLAY` (existing follow-on; handoff data flow lives within one driver invocation, so the wired consumer is resume-safe within the run) |

---

## §5 Gates

- pyright 0/0/0 (changed source + both test files).
- `harness-cp` `test_workflow_driver_decentralized_handoff.py` (full) + `test_workflow_driver.py` green; `harness-runtime` `test_lifecycle_llm_dispatch.py` non-e2e green.
- advisor (full-transcript: arc selection + the fork-vs-not crux + the slicing tie-breaker + the spec-imprecision Class-3 call) + out-of-family Codex (pre-merge).

**Cross-refs:** `[[full-chain-witness-not-half-proofs]]` · `[[built-but-vacuous-reground-ledger-asis]]` · `[[r-cxa-seam-wiring-is-producer-discovery]]` · `[[spine-ledger-forward-arc-registration]]` · `[[verification-shape-sharpened-grep-vs-e2e]]` · `[[cleared-spec-resolves-it-before-first-principles-fix]]`.
