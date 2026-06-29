---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.46
cleared_at: 2026-06-12T15:00:00-06:00
clearance_type: Phase-7-absorbed-via-design-doc (bundled-absorption — spec + impl + tests)
back_reference:
  - .harness/r-cc-1-arc-3-workflow-durable-resume-design-v1.md (design doc §7b — grounded cascade-step-2 impl plan; advisor-de-risked)
  - .harness/clearance/Spec_Harness_Runtime-v1_45-cleared-2026-06-12.md (cascade step 1 — the resume surface this extends)
  - PR #513 (cascade step 1 — api.resume + C-RT-35, caller-supplied snapshot)
  - PR (cascade step 2 — this arc) — TBD at PR creation
merge_commit: TBD-at-PR-merge
reviewer_chain:
  - advisor (pre-build, full transcript) — sharpened the arc to runtime-only (driver byte-unchanged on both paths; durability at the protocol subclass; resume reads at the api.resume boundary); identified D2-bis as the one real blocker, decidable by C-IS-01 §1 + a glob-safety check (not guessing); flagged keying (workflow_id vs run_id) + restart-determinism + the anchor-validation-deferred carry
  - empirical grounding passes — #475 is fully dormant (never constructed in src → no bootstrap journal-dir precedent); bootstrap path model (materialize_path_registry resolves the 4 PathClass dirs); capture site (workflow_driver.py:795/951 calls ctx.pause_resume_protocol.capture_pause_snapshot via duck-cast); C-IS-01 §1 frames the 4 PathClasses as canonical *artifact* classes (NOT exhaustive over all paths); glob-safety (nothing globs the STATE_LEDGER dir; ledger opens specific state.jsonl); JsonlLedgerHandle.canonical_path is the file (parent = the dir)
  - impl-time green — 11 new tests (5 store-unit, 1 durable-wrapper-unit, 1 durable-handle restart-proof e2e, 4 api.resume arg-guards) + 6 prior #513 resume tests all pass; full harness-runtime suite 1628 passed / 18 skipped (live-provider-gated, unrelated); pyright strict 0/0/0; ruff clean
  - out-of-family Codex (pre-merge, decorrelated) — TBD at PR (run on the full diff)
  - advisor (pre-done) — TBD at PR (reconcile the keying divergence + final review)
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.46`

v1.46 authors **harness-owned durable persistence** for the workflow-layer pause snapshot (R-CC-1 arc #3 **cascade step 2**). Cascade step 1 (v1.45) surfaced `resume()` with a **caller-supplied** `PauseSnapshot`; step 2 makes the **harness** own the snapshot's durability across a process restart, so the caller need not persist it — a process that died holding (and never serializing) the `RunResult` can resume by `workflow_id`. Two amendments, both **extending existing contracts** (no new contract number): **(1)** C-RT-35 §30 `resume()` gains an alternative `resume_handle: str | None` source (the harness reads the latest journaled snapshot for that `workflow_id`), with `pause_snapshot` made optional + an exactly-one-of-source invariant + two new pre-bootstrap fail classes (`RT-FAIL-RESUME-ARGS` / `RT-FAIL-RESUME-HANDLE-UNKNOWN`); **(2)** NEW §14.14.8 (under C-RT-24) authors the durable opt-in — `PauseResumeProtocolConfig.durable: bool` selects a `DurablePauseResumeProtocol` (a subclass of the CP `PauseResumeProtocol` that persists on capture) backed by a `JournalWorkflowPauseStore` co-located under the resolved `STATE_LEDGER` dir. **`run()` (C-RT-08 §8) PRESERVED VERBATIM.**

**What was reviewed.** advisor (pre-build, full transcript) sharpened the arc to **runtime-only**: durability is injected at the `DurablePauseResumeProtocol` subclass, so the workflow driver (duck-`cast`) + the frozen `HarnessContext` field (`isinstance(durable, PauseResumeProtocol)` is `True`) are byte-unchanged — no CP src/spec edit, C-CP-26 consumed unchanged. The one real blocker, **D2-bis** (journal-dir placement), was decided from primary sources, not guessed: C-IS-01 §1 frames the registry as "Four canonical *artifact* classes" (not exhaustive over every filesystem path), so a harness-internal pause journal needs **no new `PathClass`** (IS-AL-1 forecloses inventing a canonical artifact class, not co-locating internal recovery files); a glob-safety check confirmed nothing globs the `STATE_LEDGER` dir (the ledger opens the specific file `state.jsonl`), so co-locating `<state_ledger_dir>/pause-journal/` is safe + restart-deterministic via `PathResolver`. The store reuses #475's crash-survivable journal *mechanism* (per-workflow JSONL, fsync + dir-fsync, latest-record, fail-closed), **reused by pattern, NOT bound** (the engine-layer #475 substrate + recovery loop stay the line-181 CXA-2 bounded-residual). Impl landed + verified green: 11 new tests (store-unit + durable-wrapper-unit + a durable-handle restart-proof e2e + arg-guards), full harness-runtime suite **1628 passed**, pyright strict 0/0/0, ruff clean.

**Caveats for Phase 7 consumers.**
- **D2-bis RESOLVED — no new `PathClass`, no IS fork.** The v1.45 "`JournalWorkflowPauseStore` path-class placement" deferral is closed: the pause journal is harness-internal recovery substrate co-located under the resolved `STATE_LEDGER` dir; C-IS-01 + IS-AL-1 are not engaged.
- **Keying = `workflow_id`** (one file per workflow, latest-record; mirrors #475). The resume handle is `workflow_id` (always known post-crash). Multi-run-disambiguation (handle `(workflow_id, run_id)`) is a documented re-open trigger.
- **Anchor-validation-deferred (U-CP-22) carried.** A fresh-bootstrap durable resume has a fresh ledger; STRICT admits via the MVP constant-sentinel reader. Position-only resume is correct *because* the model is data-stateless (§30 / design §1.1); the `state_ledger_anchor` check stays diff-detection-fidelity-only.
- **`durable=False` is the default** — preserves v1.21 behavior verbatim (the bare CP protocol; caller persists the snapshot).
- **Historical C-RT-30 collision resolved later.** This marker originally surfaced that `C-RT-30` was used twice — §14.19 `WorkflowManifestLoader` and §30 `resume()`. The R-CL-Q1 v1.92 doc-integrity cleanup preserves `C-RT-30` for `WorkflowManifestLoader` and renumbers `resume()` to `C-RT-35`; no behavior changed.

## Notes

- Phase 7 consumers may rely on v1.46 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- `merge_commit` + the final PR back-reference + the pre-merge Codex/advisor reviewer rows are filled at PR creation/merge.
