# Adversarial Review — R-FS-1 E-impl-2 / WAL_SEGMENT (U-CP-94 + U-RT-121 + U-CP-95 + U-RT-122)

## Summary

- **Mode:** Phase-7 pre-merge impl-against-cleared-spec review (no `design-substrate/**` edit in this arc; the changed `design-substrate` plan files v2.34/v2.45 were cleared in the prior E-plan PR and are NOT part of this diff).
- **Artifact reviewed:** uncommitted working tree — 14 modified + 7 untracked files; the 4 coupled atomic units U-CP-94 / U-RT-121 / U-CP-95 / U-RT-122 + the substitution-ledger transit + fork-doc flips + the finding doc `.harness/r-fs-1-e-impl-2-finding.md`.
- **Date:** 2026-06-15
- **HEAD at review:** `7a4120a`
- **Finding count by class (§4.1 review-severity):** Class 3 (severe — phase re-opening): **0** · Class 2 (moderate — current-phase revision): **0** · Class 1 (minor — doc drift): **3**
- **Highest-severity finding:** F1-01 (finding-doc §6 file-list omission + undocumented `has_captured_pause` / Codex [P2] gate) — a transparency gap, not a code defect.
- **Disposition recommendation:** **APPROVE-WITH-CHANGES** — clearance with three inline documentation fixes to the finding doc (`.harness/r-fs-1-e-impl-2-finding.md`). The code, tests, substitution flip, and X-AL-3 posture are all clean and verified by execution. No Phase-7 §2.7.6 fork results. The two findings the finding doc records as Class-3 (recorded-not-gated) are correctly classified.

The linchpin (per advisor): **the materialized `test_u_rt_95` path-(i) e2e is non-vacuous.** It drives `execute_workflow` to `RunStatus.PAUSED` then resume across two real cycles, reads the actual state-ledger via `read_ledger(handle)`, and asserts the load-bearing persisted surface (`cp.pause-captured` / `cp.resume-attempted` entries land with engine-layer `action_id`s distinct from the workflow-layer `cp.pause-resume-protocol`). Because this is real, Finding 1's "not built-but-vacuous" claim holds, R-CXA-2 go-live is genuine, and the substitution flip is honest. The verdict is APPROVE-WITH-CHANGES, not REJECT.

---

## Class 3 findings (severe — phase re-opening)

**None.** Discriminator (b) [requires upstream-phase artifact revision] and discriminator (c) [project-commitment violation] both miss for every candidate. See "Findings considered and rejected" for the X-AL-3 (c), the spec-underspecification (b), and the verification-shape attacks that were applied and did not surface a defect.

---

## Class 2 findings (moderate — current-phase revision)

**None.** No domain-precision defect, no spec-vs-plan drift, no external-canon divergence surfaced that requires revising a current-phase artifact's substantive content. The WAL torn-write recovery semantics (the adversarial magnet) are correct and tested; the engine-firing gate is correct; the substitution flip is count-neutral and the tally gate passes.

---

## Class 1 findings (minor — documentation drift)

### F1-01 — Finding doc §6 omits two changed files + does not document the `has_captured_pause` / Codex [P2] correctness gate

- **Location:** `.harness/r-fs-1-e-impl-2-finding.md` §6 "Files" (lines 60-71) and §1 table row U-CP-95 (line 15).
- **Defect:** Two files in the diff are **absent from the finding doc's §6 Files list**, and the load-bearing correctness fix they carry is undocumented anywhere in the finding doc:
  - `harness-runtime/src/harness_runtime/lifecycle/engine_recovery_loop.py` — gained the new `has_captured_pause(...)` non-emitting peek method (`+25` lines). This is the **gate that closes the Codex [P2] spurious-ABORT finding** (a clean step-prefix crash recovery, where `resume_at > 0` but no engine pause was captured, must NOT emit a spurious `cp.resume-attempted = ABORT_SNAPSHOT_CORRUPTED`). The finding doc nowhere mentions `has_captured_pause`, the `[P2]` gate, or the spurious-ABORT hazard it closes (grep-confirmed: 0 mentions of `has_captured_pause` / `P2` / `spurious` / `ABORT` in the finding doc).
  - `harness-runtime/tests/test_engine_recovery_loop.py` — gained `test_has_captured_pause_is_a_nonemitting_peek` (`+24` lines), the test proving the peek discriminates True/False AND writes no ledger entry.
- **Discriminator that classifies as Class 1:** (a/b/c all miss). The underlying mechanism is correct and tested (verified by execution — `test_has_captured_pause_is_a_nonemitting_peek` + `test_path_i_clean_prefix_recovery_emits_no_spurious_resume` both pass). This is a documentation-completeness gap, not a substantive defect: a reviewer reading only the finding doc would not learn that a decorrelated-reviewer ([P2]) finding was closed, nor that two files changed.
- **Evidence:** `git diff --stat HEAD` lists both files with line changes; the finding doc §6 lists neither. The driver comment at `workflow_driver.py:1606`-region documents the gate ("Codex [P2]"), but the finding doc — the back-flow record an operator/future-session reads — does not.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing — the finding doc under-represents the arc's changed surface).
- **Resolution path:** Add `engine_recovery_loop.py` (`has_captured_pause` peek) and `test_engine_recovery_loop.py` to the §6 Files list; add a short note documenting that the `has_captured_pause` gate closes the Codex [P2] spurious-ABORT-on-clean-recovery hazard. Inline doc fix to the finding; no code change.

### F1-02 — Substrate test count stated as "14" in two places; the actual count is 15

- **Location:** `.harness/r-fs-1-e-impl-2-finding.md` §1 table row U-RT-121 ("14 substrate tests incl. …", line 14) and §6 ("NEW 14 substrate tests", line 66).
- **Defect:** `test_wal_segment_pause_resume_substrate.py` contains **15** test functions, not 14 (verified by execution: `15 passed in 6.80s`).
- **Discriminator that classifies as Class 1:** (a/b/c all miss). A count typo in the prose; the tests themselves are present and pass.
- **Evidence:** `pytest harness-runtime/tests/test_wal_segment_pause_resume_substrate.py -q` → `15 passed`. The finding doc says "14".
- **Resolution path:** Correct "14" → "15" in both locations. Inline doc fix.

### F1-03 — Architect-rec annotation lag: §5 attribution superseded by the E-plan re-grounding (cosmetic, already noted)

- **Location:** `.harness/architect_recommendation_e_engine_fork_vs_impl.md` §5 (the bracketed E-plan annotation at line 89) vs the as-built reality that R-CXA-2 activates at E-2 (WAL_SEGMENT), not E-1.
- **Defect:** The architect rec §5 originally attributed R-CXA-2 go-live to E-1 (EVENT_SOURCED_REPLAY); the E-plan re-grounding moved it to E-2 (WAL_SEGMENT) and annotated the rec in-place. This is NOT a defect introduced by E-impl-2 — the annotation was already applied at the E-plan PR, and the as-built E-impl-2 correctly homes R-CXA-2 at WAL_SEGMENT. Surfaced only for completeness: the architect rec is a back-flow record carrying a superseded attribution that is correctly bracket-annotated, not silently stale.
- **Discriminator that classifies as Class 1:** (a/b/c all miss). The superseding annotation is present and correct; no current-phase artifact requires revision. The as-built impl matches the corrected (E-plan §5) attribution.
- **Evidence:** Architect rec line 89 carries the bracketed `[E-plan annotation 2026-06-15: … SUPERSEDED … R-CXA-2 engine-layer activation homes at E-2 (WAL_SEGMENT)]`; the as-built `r_cxa_2_producer_loop_factory.py` binds the WAL substrate and the U-CP-95 firing gates on `engine_class == WAL_SEGMENT`.
- **Resolution path:** None required (already correctly annotated). Recorded for transparency that the review checked the supersession chain and found it honestly disposed (no stale-carry defect).

---

## The linchpin verification (advisor-flagged) — the materialized e2e is non-vacuous

The whole arc's honesty (Finding 1's not-built-but-vacuous claim, the R-CXA-2 go-live, the substitution flip) reduces to whether `test_path_i_wal_segment_engine_recovery_pause_resume_cycle` is a real e2e. Verified by **reading the asserts** (not the docstring) + **executing**:

- **Drives a real cycle:** Run 1 calls `execute_workflow(...)` and asserts `paused.status is RunStatus.PAUSED` + `paused.terminal_step_index == 0` + `dispatcher.dispatched == ["step-0"]` (proving the pause fired AFTER step 0 committed — the `resume_at > 0` prerequisite). Run 2 calls `execute_workflow(...)` again (same `run_id`) and asserts `resumed.status is RunStatus.SUCCESS` + `dispatcher.dispatched == ["step-0", "step-1"]` (the materialized segment prefix was NOT re-dispatched — segment_replay "no re-execution").
- **Asserts the load-bearing persisted surface** (NOT just control-flow — the negative example #1 trap is avoided): `after_pause = [entry.action_id for entry in read_ledger(handle)]` then `assert "cp.pause-captured" in after_pause` and `assert "cp.pause-resume-protocol" not in after_pause`; symmetrically on resume `assert "cp.resume-attempted" in after_resume` + `assert "cp.pause-resume-protocol" not in after_resume` (ZERO `CPAuditLedgerEntry` greenfield; distinct engine-layer action_ids per CP §16.5.9 invariant 5). It reads the actual ledger entry `action_id` shape a consumer would read.
- **Durable-across-restart proof:** a FRESH `WALSegmentEnginePauseResumeSubstrate` instance over the same on-disk segment dir resumes the pause the production driver captured (`restart.outcome_kind is ResumeOutcomeKind.RESUME_CLEAN`) — proving crash-survivability, not in-memory Deterministic.
- **Contrasting baseline is real, not a tautology:** `test_path_i_engine_firing_is_wal_segment_gated_not_universal` runs the SAME pause-after-step-0 flow on `PURE_PATTERN_NO_ENGINE` and asserts `"cp.pause-captured" not in [...]` — it would FAIL if the engine firing were ungated. Plus `test_path_i_clean_prefix_recovery_emits_no_spurious_resume` proves the [P2] gate (clean recovery → no `cp.resume-attempted`).
- **Fails-if-unmaterialized (task step 4, structurally guaranteed):** the `:1351` gate raises `EngineClassNotYetMaterializedError` for any class not in `_IN_SCOPE_ENGINE_CLASSES` (established at E-impl-1). Removing WAL_SEGMENT from `_IN_SCOPE` would make `execute_workflow` throw BEFORE reaching PAUSED, so `assert paused.status is RunStatus.PAUSED` would fail. The e2e is therefore not a tautology — it exercises the real materialized path, and the contrasting-baseline test already proves the `cp.pause-captured` assertion is WAL_SEGMENT-gated.
- **Execution:** `10 passed` (path-(i) e2e + recovery loop), `15 passed` (substrate), `68 passed` (CP driver), `996 passed / 1 xfailed` (full harness-cp), `40 passed` (runtime lifecycle incl. #475 journal base — confirming the `json_default`/`json_object_hook` rename did not break the base).

**Verdict on the linchpin: REAL.** Finding 1's Class-3 (recorded-not-gated) holds; REJECT is not warranted.

---

## Findings considered and rejected (transparency)

1. **X-AL-3 silent design-extension (Attack A8, discriminator (c)) — REJECTED.** No new H_T primitive minted. `EngineClass` enum remains exactly 5 closed members (verified `engine_class.py:31-50`); `engine_class.py` / `pause_resume_protocol.py` / `workflow_driver_types.py` (the contract carriers) are UNTOUCHED by this diff. The only new public symbol is `WALSegmentEnginePauseResumeSubstrate`, which *implements* the pre-existing `EnginePauseResumeSubstrate` Protocol — no new contract. `has_captured_pause` is a runtime-internal peek method, not a CP contract. The driver consumes `ctx.engine_recovery_loop` via `getattr(ctx, "engine_recovery_loop", None)` duck-typed — `harness_runtime` appears in `workflow_driver.py` only in comments/docstrings + one pre-existing local import (`validator_escalation_composer:1970`, not in this diff). Adding WAL_SEGMENT to `_IN_SCOPE_ENGINE_CLASSES` is the same impl move U-CP-56 made for save-point. Clean.

2. **Spec under-specification forcing a fork (discriminator (b)) — REJECTED.** C-CP-07 §7.1 row 5 + §7.4 ("specific WAL implementation at WAL-segment class" deferred to impl-discretion) + C-CP-08 §8.1 `segment_replay` + §8.2 row 5 fully specify the slice. Verified the §7.4 deferral clause names WAL-segment by reading `Spec_Control_Plane_v1_2.md:704`. The architect rec correctly split E-1/E-2 (impl, no fork) from E-3 (narrow fork, OUT of scope here). E-3 RECONCILER_LOOP is correctly excluded — the still-raises vehicle tests were re-pointed to RECONCILER_LOOP (now the sole out-of-scope class), verified by the CP driver tests passing.

3. **WAL torn-write recovery gap-unsafety (the adversarial magnet) — REJECTED.** Traced `_valid_prefix` / `_append` / `_read_latest` / `_parse_segment`: the prefix scan stops at the FIRST corruption (`break` on torn tail / bad checksum / decode failure / blank line / out-of-order `segment_index`), so replay NEVER resumes past a gap (gap-safe). `_append` truncates any torn/garbage tail back to `valid_extent` (with its own fsync) BEFORE appending — torn-tail-then-append recovers. The divergence from #475's fail-closed-on-torn-latest is justified and documented: a torn tail is an un-fsync-acknowledged (uncommitted) write, so recovering to the last committed segment loses nothing the caller was told was durable; the base's stricter rule guards a different single-record-per-workflow hazard. The 15 substrate tests construct GENUINELY corrupt bytes (real partial trailing segment with no newline; flipped checksum on a middle segment; mismatched `segment_index`), not valid-data-read-back. All pass. **Crash scenarios probed:** torn tail (no final `\n`), torn-tail-then-append (truncate-before-append), corrupt middle (gap-safe), checksum mismatch on first/only segment (fail-closed abort), out-of-order `segment_index` (ordering integrity), absent log, cross-workflow corruption isolation, invalid-UTF-8 mid-segment (byte-robust scan), and cross-process restart durability are all covered. The one crash class genuinely NOT exercised is **concurrent multi-process append / lease coordination** — but that is scoped-out-by-design (F3 floor (iii) lease is deferred by the U-CP-94 / U-RT-121 plan ACs and the save-point precedent does not exercise it either), so it is NOT a finding (flagging it would be FM-D mechanical domain-attack application).

4. **`has_captured_pause` naive-file-exists (sharp probe) — REJECTED.** The peek runs the C-CP-22 free-function `attempt_resume` against the bound substrate, which dispatches to the WAL override `_read_latest` → `_valid_prefix`. A torn-only log → `_valid_prefix` returns `[]` → `_read_latest` None → `ABORT_SNAPSHOT_CORRUPTED` → `has_captured_pause` returns False. So it uses the valid-prefix logic, NOT a naive file-exists (which would return True for a torn-only log and re-introduce the spurious ABORT). Verified by `test_has_captured_pause_is_a_nonemitting_peek` (True for captured, False for absent, no ledger write).

5. **Engine firing vacuous / spurious-ABORT (Codex [P2], negative example #2) — REJECTED.** The U-CP-95 resume firing is gated on `_engine_recovery_loop.has_captured_pause(...)`, so a clean step-prefix crash recovery (`resume_at > 0`, no captured pause) does NOT emit a spurious `cp.resume-attempted = ABORT_SNAPSHOT_CORRUPTED`. Verified by `test_path_i_clean_prefix_recovery_emits_no_spurious_resume` (asserts `"cp.resume-attempted" not in [...]` for the clean recovery). The gate genuinely closes the [P2].

6. **Verification-shape grep-vs-e2e (checklist 7, negative example #1) — REJECTED.** The R-CXA-2 go-live is proven by execution: the e2e drives `execute_workflow` to PAUSED then resume and reads the persisted state-ledger entry `action_id` shape, not "is bound" / grep. See the linchpin section.

7. **Stale docstring after repurposing (negative example #5, checklist 1) — REJECTED.** The `test_u_rt_95...py` module docstring + path matrix were repointed off the prior HITL-composer mechanism to the engine-layer recovery loop (lines 12-18 path-(i) row now reads "Driver WAL_SEGMENT pause-trigger fires the engine-layer recovery loop (U-CP-95)"; lines 33-45 explicitly state "It supersedes the prior HITL-composer framing of path (i)"). No stale-carry.

8. **Substitution-ledger flip honesty + count-neutrality (checklist, R-600) — REJECTED.** `H_T-CXA-2` transits `BOUNDED_RESIDUAL → SUBSTANTIVE_RETIRED` at batch-57. Count-neutral: `BOUNDED_RESIDUAL` 3→2, `SUBSTANTIVE_RETIRED` 43→44, `retired` stays 54. The re-open trigger ("event-sourced/reconciler/WAL recovery") genuinely fired — the WAL recovery engine now exists and fires in production (ties to the real e2e). `tools/substitution_ledger.py --check` → `ledger OK — 54/54 RETIRED, 54/54 pipeline-advanced`. `test_substitution_ledger.py` → `16 passed`; the bucket-breakdown + batch-57 tests were updated honestly; OD-6 correctly retained as the canonical BOUNDED_RESIDUAL exemplar.

9. **Finding 2 (`resumption.is_replay` deferred to L9 OTel) Class-3 vs halt-route-split-AC (checklist 9) — REJECTED as halt-route-split.** Class-3 (recorded-not-gated) holds: the cleared spec DEFERS the span-attribute layer. Verified `Spec_Control_Plane_v1_2.md` §8.3 item 3 ("the v1 commitment is the resumption-kind enum + idempotency-key join; the v1.2 closure will commit span-re-emission semantics per engine class") + §8.4 (the F2-12 carry-forward, "out of scope at this spec revision"). The plan AC (U-CP-94 functional AC) explicitly asserts the `is_replay` flag value is the in-scope part and span re-emission cadence is deferred under F2-12 — consistent with the cleared spec. The E-impl-1/save-point precedent left it unmaterialized and was accepted. Not a split-AC defect.

10. **CP↔RT cycle / carrier-home (checklist, `[[carrier-home-defect-pattern]]`) — REJECTED.** The single cross-axis edge U-RT-122 → U-CP-95 runs runtime→CP (downstream package direction). The CP driver reads `ctx.engine_recovery_loop` duck-typed; U-CP-94's `resume_at` reads the F2 IS ledger (CP→IS), not the runtime segment-log substrate. The WAL substrate, recovery loop, and factory are all `harness-runtime`. No `harness_cp → harness_runtime` import. Verified the driver has no new harness_runtime import.

11. **SINGLE_THREADED_LINEAR byte-unchanged regression (CP §25.10 Invariant 1) — REJECTED.** The U-CP-95 pause-firing branch is gated `engine_class is WAL_SEGMENT and _engine_recovery_loop is not None and pause_requested_flag.is_set()`, checked BEFORE the workflow-layer branch; the resume branch is reached only for `engine_class == WAL_SEGMENT`. Full harness-cp suite `996 passed / 1 xfailed` (the lone xfail pre-exists). No regression.

12. **`PauseEvent` JSON round-trip inversion (low-risk source-glance) — REJECTED.** `_canonical_payload` uses `model_dump(mode="python")` round-tripped through the promoted `json_default` / `json_object_hook` (same functions the proven #475 base uses). `test_material_diff_revalidates` exercises a `PauseEvent` carrying a `bytes` snapshot anchor (`snapshot_capture_at_pause=b"..."`) and passes — proving the bytes-sentinel round-trip inverts. The `json_default`/`json_object_hook` privacy promotion is a one-source-of-truth refactor; the 40-test runtime lifecycle run (incl. the base journal substrate tests) confirms the base still works post-rename.

---

## Disposition

**APPROVE-WITH-CHANGES** (§4.1.1 clearance with inline documentation fixes).

- **0 Class-3** and **0 Class-2** findings → no Phase-7 §2.7.6 fork; no phase re-opening; no current-phase substantive revision.
- **3 Class-1** findings, all confined to the finding doc `.harness/r-fs-1-e-impl-2-finding.md` (and one cosmetic note on the already-correctly-annotated architect rec):
  - **F1-01** — add `engine_recovery_loop.py` + `test_engine_recovery_loop.py` to §6 Files; document the `has_captured_pause` gate that closes the Codex [P2] spurious-ABORT hazard. *(strongest of the three — a transparency gap on a decorrelated-reviewer correctness fix.)*
  - **F1-02** — correct "14 substrate tests" → "15" in §1 + §6.
  - **F1-03** — no action (recorded for supersession-chain transparency; already correctly annotated).

The two findings the impl finding doc records as **Class-3 (recorded-not-gated)** — (Finding 1) CP/IS-level `resume_at` degenerate-vs-save-point with the genuine capability being the durable substrate + loop firing, and (Finding 2) `resumption.is_replay` riding the standing-deferred L9 OTel layer — are **correctly classified Class-3**, NOT Class-1 (the spec genuinely defers the span layer at §8.3/§8.4; the genuine WAL capability is real and proven by execution). The finding doc's §4 "Class-3, NOT Class-1" classification table is sound.

**Severity-distribution sanity:** 0 Class-3 / 0 Class-2 / 3 Class-1 is a low-finding-density review of a careful, well-tested impl-against-cleared-spec arc — consistent with (not smoothing of) the evidence: the adversarial magnet (WAL torn-write recovery) is genuinely correct and tested, the linchpin e2e is genuinely non-vacuous, the substitution flip is honest and count-neutral, and X-AL-3 is clean. The findings that exist are documentation completeness, not code defects. This is the expected shape when an arc was already run through Codex ([P1] truncate-before-append + [P2] spurious-ABORT gate, both applied) + advisor before review — the decorrelated reviewers caught the substantive issues pre-review; what remains is the finding-doc transparency lag.

The changes are inline doc fixes to a `.harness/` back-flow record; they do not block merge and can land in the same PR or a follow-on. Recommend applying F1-01 + F1-02 before merge for back-flow-record completeness.
