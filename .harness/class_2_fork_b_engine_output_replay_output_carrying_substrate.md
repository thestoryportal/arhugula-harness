# Class 2 (in-execution, FULL-SPEC-pre-authorized) — `B-ENGINE-OUTPUT-REPLAY`: output-carrying event-history substrate (LINEAR EVENT_SOURCED_REPLAY)

**Status:** ✅ BUILT (2026-06-19) — bundled-absorption arc co-landing runtime spec v1.62 → **v1.63** (NEW §14.23 C-RT-32 `EngineOutputStore`) + clearance marker + `harness-runtime/src` (store + bootstrap wiring) + `harness-cp/src` (producer + rehydrate) + by-execution tests. Materializes the C-CP-08 §8.1 "activity outputs cached and replayed" clause that `EVENT_SOURCED_REPLAY` ships DEGENERATE (E-impl-1 Finding 2).
**Filed at:** R-FS-1 standalone arc `B-ENGINE-OUTPUT-REPLAY` (the 12th standalone `B-*` arc since the FROZEN order completed)
**Locus:** `harness-runtime/.../lifecycle/engine_output_store.py` (the store) + `harness-cp/.../workflow_driver.py` (`_record_durable_step_output` producer + `_rehydrate_inter_step_channel_on_replay` on the EVENT_SOURCED_REPLAY resume branch) vs cleared `Spec_Control_Plane` C-CP-08 §8.1 `engine_replay` + `.harness/r-fs-1-e-impl-1-finding.md` §2/§4
**Classification:** Class 2 (in-execution; FULL-SPEC directive 2026-06-12 pre-authorizes the build + design back-flow). **NO operator gate** (see below).
**Routing:** Bundled-absorption per workspace `CLAUDE.md` §11.4.

## What was built

C-CP-08 §8.1 `engine_replay`: *"Prior steps replay from Event History deterministically; **activity outputs cached and replayed**; no re-execution of activities."* U-CP-93 (E-impl-1) delivered "no re-execution" (skip-prefix), but "outputs cached and replayed" was DEGENERATE because: (1) **no output-carrying substrate** — the F2 `EntryPayload` (C-IS-07 §7.1) carries only a `response_hash` digest, never the activity output (E-impl-1 Finding 1); (2) the consumer (B-INTERSTEP, #651) is now built, but on a skip-prefix resume the fresh inter-step channel reads EMPTY, so a downstream consumer reads `None` where a fresh run reads the upstream output.

The build supplies the storage half + the rehydration:

1. **Substrate** — a dedicated, hand-rolled durable `EngineOutputStore` (per I-6, no vendored event-sourcing framework), mirroring `JournalWorkflowPauseStore` crash-safety (per-run JSONL, `fsync` + dir-fsync, torn-append self-heal, fail-soft-per-line), keyed by `run_idempotency_key` (the SAME stable id the resume join `_determine_resume_at` uses — the EVENT_SOURCED_REPLAY restart re-runs with the same `run_id` → the same `run_idempotency_key`), co-located under `<state_ledger_dir>/engine-output`. Bound at stage-5 LOOP_INIT when `RuntimeConfig.engine_output_replay=True`.
2. **Producer** — the CP driver `_record_durable_step_output` (the `cp_is_wiring` getattr idiom — harness-cp does not import the runtime store) records each completed step output to the store **BEFORE** `_append_step_ledger_entry`.
3. **Rehydrate** — on an EVENT_SOURCED_REPLAY resume, `_rehydrate_inter_step_channel_on_replay` replays the stored prefix outputs into the inter-step channel so the first re-dispatched step reads its recovered predecessor.

## Why a dedicated store, not the IS F2 ledger (probe-resolved, advisor not council)

The substrate-shape fork (dedicated runtime store vs. extending the IS `EntryPayload` to carry outputs) is **probe-resolved to the dedicated store**: the F2 ledger stores a `response_hash` digest BY DESIGN (the ledger is causality + integrity, not data storage); extending `EntryPayload` to carry outputs would ripple the C-IS-05 §5.2 entry hash + the JSONL shape + the IS contract for a CP/runtime-local replay concern — foreclosed by I-6 (hand-roll) + ADR-F2 (the six-field ledger is frozen) + the `JournalWorkflowPauseStore` precedent (a harness-internal recovery substrate co-located under STATE_LEDGER, NOT a canonical `PathClass` artifact). The IS-purity ⊥ avoid-a-second-store tension is foreclosed by the constraints → advisor, not council (`[[probe-resolves-fork-prescribed-council]]`).

## The store ↔ ledger SKEW discipline (the load-bearing correctness rule, advisor)

Two durable substrates now record per step: the F2 ledger (the `resume_at` authority) + the output store (the data). A crash between them de-syncs them. Two rules close it:
- **RESERVE-before-COMMIT** — the producer writes to the store BEFORE the ledger-append `resume_at` counts (verified against the live append site: `workflow_driver.py` records the durable output immediately before `_append_step_ledger_entry`). So the store always holds ≥ the ledger's materialized prefix; a resume never finds a materialized step with a missing stored output. (The B-EFFECT-FENCE RESERVE-before-fire / COMMIT=ledger-entry shape.)
- **Rehydrate-by-`resume_at` + fail-closed** — rehydration is driven by `resume_at` (NOT "load whatever's in the store" — a crash after the store-write but before the ledger-append leaves one extra uncommitted record, ignored), and FAILS CLOSED if a step the ledger says materialized is missing from the store OR its stored `step_id` ≠ the re-supplied body (`engine-output-replay-missing-output` / `-identity-mismatch` — the B-FANOUT-PAUSE identity fail-close symmetry).

## Why NO operator gate (§1.1 reuse)

Carrying outputs across a resume breaks the R-CC-1 design §1.1 "position-only / data-stateless resume" model — but §1.1 is a *descriptive MVP scoping note with an explicit §6 re-open trigger* ("a future execution model … would need a state-restoration story + a durable store carrying more than the position-only PauseSnapshot"), NOT a forbidding invariant. This arc IS that designed re-open firing (the linear analogue of B-FANOUT-PAUSE's fan-out re-open). Adopt-and-note + clearance under the FULL-SPEC directive; reuse the B-FANOUT-PAUSE gate-discriminator verbatim (contrast B4-Slice-4 §14.5.3 inv 2 → gated). `[[grounding-reveals-claude-closeable-slice-close-honestly]]`.

## Scope + registered forward arcs

LINEAR `EVENT_SOURCED_REPLAY` only (the cleared E-impl-1 slice + the U-CP-56 precedent). Registered forward arcs: `B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT` (WAL_SEGMENT shares the store, E-impl-2 — its CP/IS resume_at is the same F2-prefix shape); the non-linear resume-blind strategies inherit the already-registered B-FANOUT-PAUSE-family resumption arcs (the non-linear strategies compute no `resume_at` for ANY engine class — a pre-existing limitation, E-impl-1 sub-finding).

## Decorrelated review (pre-merge) — complementary findings on the resume edge

advisor (full-transcript) + out-of-family Codex (the diff), per `CLAUDE.md` §13.1. The two reviewers' findings COMPOSED on the same `read_outputs()==empty` edge — the same silent-degradation/false-signal class this session keeps surfacing:
1. **advisor [P2] — the fail-closed conflated config-flip with corruption (a false FAILURE).** A run with `engine_output_replay=False` that crashes after a step, then resumes with the flag now `True`, has an empty store → the original fail-closed turned a previously-working (degraded) resume into a hard FAILED. Fixed: degrade to the empty-channel path (the pre-arc behavior) when there is NO recorded history.
2. **Codex [P2] — but a READ FAILURE must NOT be degraded (a false SUCCESS).** `read_outputs()` returns empty for BOTH "no journal file" AND "file present but unreadable/corrupt" (caught `OSError`/`UnicodeDecodeError`). Degrading the latter silently drops cached outputs → wrong upstream context. Fixed: a **FILE-EXISTENCE discriminator** (`EngineOutputStore.journal_exists`) — file absent → degrade (config-flip); file present but no readable records → FAIL-CLOSED (`engine-output-replay-unreadable-store`). RESERVE-before-COMMIT keeps the partial-prefix case (store has SOME records, missing a committed step) a separate, exact fail-close.
3. **advisor [minor] — the producer was engine-class-agnostic.** Fixed: gated on `engine_class is EVENT_SOURCED_REPLAY` so a non-replay run with the flag on does not write a never-rehydrated journal (WAL_SEGMENT extends the gate at its arc).

Tests added: `...no_journal_degrades_not_fails` (config-flip degrade) + `...unreadable_store_fails_closed` (corruption fail-close) + the `journal_exists` store unit test. advisor also confirmed the witness split is NOT a half-proof (the CP + runtime witnesses meet at the real `_rehydrate_inter_step_channel_on_replay`, exercised on both sides) + #1 whole-workspace pyright (clean — the B-FANOUT-PAUSE durable-override lesson).

## Verification

- harness-runtime: `test_engine_output_store.py` (7 store crash-safety unit tests — restart round-trip, isolation, last-wins, torn-line self-heal, corrupt-skip-with-gap); `test_lifecycle_llm_dispatch.py::test_b_engine_output_replay_rehydrated_output_reaches_real_provider_call` — the **full-chain witness**: a prior run's output durably stored on disk → the CP rehydrate into a fresh channel → the REAL `RuntimeLLMDispatcher` injects it → the recording provider RECEIVES the recovered output (NOT a channel-unit proxy).
- harness-cp: `test_workflow_driver.py` — the CP rehydrate witness (a channel-reading dispatcher proves the first re-dispatched step SEES the recovered predecessor) + a NEGATIVE CONTROL (no store → `None` upstream) + 2 fail-closed tests (missing-output skew + identity-mismatch).
- Gates: pyright 0/0/0 · ruff · harness-cp 1087 passed + 1 xfailed · runtime bootstrap/types 305 passed · decorrelated review advisor (substrate-fork + skew rule + §1.1) + out-of-family Codex (pre-merge).
