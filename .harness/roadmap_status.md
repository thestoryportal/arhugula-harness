# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `640d4ba167ab` |
| `last_refreshed` | 2026-08-14T00:00:00Z |
| `git_head` | `85fbd11d` —  |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-57.md` |
| `open_fork_doc_count` | 117 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**Purpose.** Live pointer to the next Claude/Codex-executable frontier. Full round-by-round history (every prior round, verbatim, most-recent-first) lives in the archive below — grep it by PR/`B-`/`R-`-id/round, never read wholesale.

**Current next action (post-#1348).** **`B-178` IS CLOSED (#1348) — the flake class's first REPAIR, and it corrected its own witness's mutation probe on the way out.** The test compared a SYNTHETIC `now` against a REAL-clock `first_observed_at` and so held only while under ~0.15 s of real time elapsed across two sweeps, a JSON read+write and three file ops. **The repair is the shape, not the margin:** both remaining sweeps now pass `observed_at`, matching the idiom the test's OWN first sweep already used (`gc_sweep(now=at, observed_at=at)`) — the later calls had simply omitted it, and `_observe_candidates` falls back to `time.time()` at `protected_result_store.py:1342`. Load-independence is verified BY EXECUTION: the 0.25 s delay that reproduced the original failure now passes, and so does 3.0 s — 20x the breaking delay. **THE FINDING WORTH CARRYING FORWARD IS THE FALSE NON-KILL.** Conjunct (a) has TWO carriers — the `tmp_age > ttl` filter building `provisional_tmp` at `:1103`, and the `current_time - tmp_mtime > ttl` re-check building `verified_tmp` at `:1174`. Dropping only the second leaves the first gating and the test PASSES, which grades as evidence the witness is weak when it is not; with BOTH dropped it fails on its own `conjunct (a) is not gating` assertion at `age_s=0.9`, and the PRE-FIX test fails identically, so witness strength is provably unchanged. **A probe that reports NOT-KILLED is a claim needing the same scrutiny as one reporting KILLED** — the `B-165` arc learned the KILLED half (a SyntaxError graded as detection); this arc learned the symmetric half, and the two-carrier note now lives in the docstring so the next prober cannot repeat the mis-grade. The new `_read_observation_record(store) == {}` assertion also proved load-bearing under adversarial review rather than decorative: with `_observe_candidates` mutated to accumulate instead of replace, removing ONLY that assertion lets the regression pass SILENTLY. **THE NEXT AUTO-`ACTIVE` ITEM IS `B-177`** — decide whether AC #5's 100 ms flush budget is a LATENCY CEILING or a REGRESSION GUARD. It is ~40x looser than the ~2.5 ms it measures, so it cannot catch the 16x per-row-commit regression that is already measured and recorded; its two carriers frame it differently (the canonical AC at `design-substrate/Implementation_Plan_Operational_Discipline_v2_14.md:147` says only "Integration test: 100-span batch flush in < 100ms", while the `flush_to_sqlite` docstring at `ring_buffer.py:333` calls the same number a "latency target"), and one number is currently doing both jobs. If a guard is wanted it needs a SEPARATE measurement-derived assertion, not a re-pointing of the ceiling. **The one genuine operator gate remains `B-165`'s** three-way spec repair (narrow NOTE 6-i / widen the CP §0.4(2) basis / build the missing workflow-validation layer). **PROCESS FINDING — SHARED-CHECKOUT CONTENTION, new this arc:** two merge-gate lenses ran REAL mutation probes in the shared working checkout while codex reviewed the same tree; one found and restored the other's leftover debris. No damage resulted (tree verified clean, commits intact, `src/` undrifted, 99 tests re-run green) and codex defended itself by polling `git status` until the tree matched HEAD before concluding — but a reviewer that MUTATES belongs in a worktree, and until it is one, verify the checkout after every such review rather than trusting the reviewer's own restore.

**Archive.** `.harness/roadmap-next-action-archive.md` (PRIOR rounds only, verbatim as each stood when superseded — the current round lives only in this head; the newest superseded round may lag there until the next content PR archives it, and is always losslessly recoverable from this file's own git history meanwhile).

## Remaining forward work

**The full-spec build (R-FS-1).** The single full-spec umbrella **R-FS-1** has no `B-*` forward build arcs remaining and is RESOLVED after manual Tier-1 gates G1.4/G1.7/G1.8 were signed. `R-CL-Q1`, `R-CL-Q2`, `R-CL-Q3`, `R-CL-Q4`, `R-CL-D1`, and `R-CL-C1` are RESOLVED; stale governance entries `R-IF-114` and `R-IF-115` are RESOLVED; `R-600-pattern-bake-in-sweep` cadence-8 is ACTIVE-SURVEYED (promoted `mutation-probe-as-load-bearing-witness` as PD-8 at workflow v1.18 — the cadence-7 card-frontier flag, now closed); `R-600-codex-out-of-family-review` is RESOLVED. The new operator-selected implementation frontier is the full memory substrate build below.

**Full memory substrate build.** The approved design packet from PR #853 is now implemented through the planned provider-free closeout sequence. U-MEM-01 is merged at PR #855, U-MEM-02 is merged at PR #857, U-MEM-03 is merged at PR #859, U-MEM-04 is merged at PR #861, U-MEM-05 is merged at PR #863, U-MEM-06 is merged at PR #865, U-MEM-07 is merged at PR #867, U-MEM-08 is merged at PR #869, U-MEM-09 is merged at PR #871, U-MEM-10 is merged at PR #877, U-MEM-11 is merged at PR #879, U-MEM-12 is merged at PR #881, U-MEM-13 is merged at PR #883, U-MEM-14 is merged at PR #885, U-MEM-15 is merged at PR #887, U-MEM-16 is merged at PR #889, U-MEM-17 is merged at PR #891, U-MEM-18 is merged at PR #893, U-MEM-19 is merged at PR #895, U-MEM-20 is merged at PR #897, U-MEM-21 is merged at PR #899, U-MEM-22 is merged at PR #901, U-MEM-23 is merged at PR #903, U-MEM-24 is merged at PR #905, and U-MEM-25 is merged at PR #907. No U-MEM forward implementation unit remains. Live Anthropic native-memory plus Claude Code and Codex CLI auth confirmations are recorded by U-MEM-live-confirmations; Antigravity is CONFIRMED live via `agy` (PR #1136) and generic-command PASSED live with the standing `ollama list` probe (PR #1137); legacy Gemini is terminally NOT CONFIRMED on this host — its declared `gemini -p` probe fired live and was refused upstream (`IneligibleTierError`, client deprecated for individual accounts, superseded by the Antigravity route).

**Single arc→unit source.** The full itemization — every arc + unit in plain language, with status, build position, dependencies, and as-built units — lives in the single structured source **`.harness/arc-ledger.yaml`** (derived by `tools/arc_ledger.py`, rendered in the dashboard's Arc & unit map; the forward `B-*` register is shown with decompose-at-open markers). The spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` carries every surfaced boundary's rationale; per-arc grounding leads at `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` (re-ground at arc-open, presence-not-correctness).

**Frozen order** (B1→B3→E→B2→R→B4→CA→B5→B6→B7→M) — **COMPLETE, 11/11.** R-FS-1 standalone `B-*` register is **69 closed / 0 forward / 0 gated / 4 resolved** in `.harness/arc-ledger.yaml`; `snapshot.rfs1_status: resolved` and `closure_gate.py` G1.1 = **0+0**. Manual Tier-1 closure gates G1.4/G1.7/G1.8 are recorded at `.harness/r-fs-1-tier1-manual-signoff.json`; **R-CL-Q1**, **R-CL-Q2**, **R-CL-Q3**, **R-CL-Q4**, **R-CL-D1**, and **R-CL-C1** are resolved.

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| #1292 | `fix/codex-hook-contract-recovery` | — | — |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| #1348 | 2026-08-14 | B-178 CLOSED — the flake class's first repair. Test compared a SYNTHETIC now against a REAL-clock first_observed_at (~0.15s headroom); fixed by injecting observed_at on both sweeps, matching the idiom the test's own first sweep already used. Load-independence verified BY EXECUTION: the 0.25s delay that reproduced the failure now passes, and so does 3.0s (20x). STEP 3 CORRECTED THE DOCSTRING'S OWN MUTATION PROBE: conjunct (a) has TWO carriers (:1103 provisional_tmp, :1174 verified_tmp) and dropping only the second is a FALSE NON-KILL; with both dropped the test fails on its own assertion at age_s=0.9, and the PRE-FIX test fails identically, so witness strength is provably unchanged. The new _read_observation_record=={} assertion was mutation-proven load-bearing by the L3 lens (removing only it lets an accumulate-not-replace regression pass silently). 3-lens gate all-APPROVE; codex converged clean (and defended itself by polling git status until the tree matched HEAD). PROCESS FINDING: two lenses ran real mutation probes in the SHARED checkout while codex reviewed it — no damage, but mutating reviewers belong in worktrees. CI 18/18. |
| #1347 | 2026-08-14 | B-176 CLOSED — step 1 discharged BY EXECUTION (idle median 2.51ms/max 4.54ms n=40; heavy-load median 5.96ms/max 139.92ms with 3 of 60 BREACHING, zero code change), step 2 = best-of-5 with the 100ms threshold untouched. Fresh db + per-attempt inserted==100 make every attempt real. THE FIRST MUTATION-PROBE ANNOTATION WAS WRONG AND ITS OWN PROBE CAUGHT IT: per-row execute+commit runs 33-57ms and PASSES; retracted, verified kill is fullfsync+per-row at ~2.0s. That non-kill became B-177 (100ms budget has ~40x slack; registered not patched since tightening re-specs AC #5). Grounding caught two errors in my own draft pre-commit: the plan text does NOT say 'latency target' and the cite was off by one. B-178 registered: an UNRELATED reddened CI test, REPRODUCED by positive control — synthetic now vs real-clock first_observed_at, ~0.15s headroom. 3-lens gate all-APPROVE (1 L3 nit absorbed); codex converged clean at the final head. CI 18/18. |
| PR #1345 | 2026-08-14 | B-165 CLASS 1 FORK FILED + register transit registered_finding -> design_substrate_gated (doc-only follow-on to #1343, split because DESIGN_RE x IMPL_RE would fire HARD DESIGN_IMPL_MIX on a bundled patch -- verified by running stop_gate.py, not assumed). The spec defect: §14.8.7 NOTE 6-i asserts a per-placement distinctness that holds only for DIFFERING positions. Three repairs enumerated; (A) narrow the note is recommended; the choice is the operator's. B-176 registered (ring-buffer wall-clock flake, third of the B-166/B-169 class). Owed --archive-superseded write landed. |
| PR #1343 | 2026-08-14 | B-165 GROUNDING LEG — premise CONFIRMED by execution; the deliverable is a Class 1 fork filing, not code. Two same-position placements compose ONE audit identity; the key is also the F2 idempotency_key and dedup is key-only, so the second gated placement's entry is DROPPED (silent omission of oversight evidence). Holds on all four blast-radius tiers including READ_ONLY, where the gate auto-approves and prompts nobody. NOT a B-71 regression (test 4 asserts both halves). Defect is in the SPEC: §14.8.7 NOTE 6-i asserts distinctness that holds only for DIFFERING positions. 13 test functions / 16 nodes across three modules, 13/13 mutation-proven. SEVEN annotation failures absorbed — six named undetectable sites, and the seventh was the probe DRIVER counting a SyntaxError collection failure as a KILL; driver now compile()-guards and REFUSES. Nine codex rounds; three-lens merge gate BLOCK→fixed→BLOCK→fixed→APPROVE. B-176 registered (ring-buffer wall-clock flake). |
| 1341 | 2026-08-14 | B-71 CLOSED — impl leg (U-CP-102 + U-RT-155) co-landed. 44 witnesses / 24 probe annotations / 26 distinct mutations, all PINNED. EIGHT out-of-family rounds + a 3-lens merge gate absorbed after the first green build: 11 P2s and 1 P1. Four were one class (an advisory diagnostic able to abort a resume via warnings-as-errors, a raising log handler, a raising tree walk, and by preempting the drain gate); two were defects the arc's own round-5 fix introduced; five were vacuous witnesses of mine. main GREEN at 0af632f4. |

---

---

## Outstanding fork docs (47 total — latest additions filed by PR #434)

Sample (highest-leverage open):

| Fork doc | Class | Status |
|---|---|---|
| `class_1_fork_sandbox_tier_no_execution_driver_contract.md` | Class 1 | ✅ APPLIED-AS-BOUNDED-READING-B (status-line refreshed 2026-06-08) — R-410 supplied `ToolExecutionDriver` + local Docker provider; R-411 added gVisor/runsc; R-412 adds managed E2B full-VM. |
| `class_1_fork_tool_step_no_operator_supplied_converter.md` | Class 1 | ✅ APPLIED (PR #171, spec v1.40) — converter config surface landed (Reading B) |
| `class_1_fork_tool_step_no_bootstrap_sandbox_decision_resolver.md` | Class 1 | ✅ APPLIED-AS-READING-B (PR #172, spec v1.41 §14.9.8) — resolver + 5 bootstrap gaps wired; AC #2 final close = operator live e2e |
| `class_1_fork_llm_cost_attribution_not_firing_on_real_dispatch.md` | Class 1 | ❌ RESOLVED-AS-INVALID (PR #168) — test-observation bug, not a defect; cost-attribution fires + writes; OD-5 retirement VALID |
| `class_1_fork_harness_toml_default_discovery_unimplemented.md` | Class 1 | ✅ APPLIED-AS-READING-A (PR #305 status refresh after PR #279 implementation) — CWD `harness.toml` discovery shipped; no longer open. |
| `class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` | Class 1 | ✅ APPLIED-AS-READING-C (PR #107, spec v1.30) |
| `class_1_fork_yaml_loader_step_payload_scalar_coercion_gap.md` | Class 1 | ✅ APPLIED-AS-READING-A (spec v1.39, pyyaml StrictSafeLoader) — R-100-mvp-yaml-loader-shipped verified done at non-live level (41 loader/equivalence tests pass) |
| `class_1_fork_topology_admissibility_check_load_time_vs_runtime_asymmetry.md` | Class 1 | ✅ APPLIED-AS-READING-A (spec v1.38, defer-to-runtime) |
| `class_2_fork_audit_stub_timestamp_universal_fix_plus_per_tier_annotation.md` | Class 2 | ✅ APPLIED-AS-(D) |
| *(complete enumeration at `ls .harness/class_*_fork_*.md`)* | — | — |

**Audit status:** 2026-06-07 cadence pass closed in this PR: sandbox execution-driver fork refreshed from historical PROPOSING; Path (i) durable-async fork leading status token normalized to `**Status:**`; stale roadmap sample row for the already-applied `harness.toml` fork refreshed; no other stale fork-doc headline status lines found. Next cadence: ~5 PRs or operator-discretion.

---

## Phase 7 retirement progress

> **🎓 PHASE-8 GRADUATION + BATCH-56 LIVE LEDGER.** The R-700 reconciliation is CLOSED — the operator ratified **accounting (i)** (PR #246) and lifted the declaration hold. Historical declaration: **RETIRED 46/54 (85.2%) + pipeline-advanced 49/54 (90.7%)**. Batch-52 back-flowed the live R-810/R-820 evidence for AS-8e, AS-8f, and CP-17; batch-53 back-flows the OD-4 runtime residual and the 0-wireable CXA-4 bookkeeping row; batch-54 lands the CP→AS runtime composer; batch-55 records CXA-2 as a counted bounded residual; batch-56 records CXA-1 as substantively retired after the AS→IS producer and edge-scope audit: **live ledger RETIRED 54/54 (100.0%) + pipeline-advanced 54/54 (100.0%)**. Prior batch records stand verbatim; this section reports the current live 54-row set derived from `.harness/substitutions.yaml`.

The bucket rows below sum to **54** under the batch-56 live ledger (RETIRED 54).

| Bucket | Count | Notes |
|---|---|---|
| RETIRED | **54/54 (100.0%)** live (batch-56) | 43 substantive + 8 authoring-only + 3 bounded-residual (CP-16, OD-6, CXA-2). IS 9/9; AS 11/11; CP 21/21; OD 8/8; CXA 5/5. Phase-8 historical declaration remains 46/54; batch-52 added AS-8e, AS-8f, and CP-17 after R-810/R-820 live proofs; batch-53 adds OD-4 and CXA-4 after accounting/back-flow; batch-54 adds CXA-3 after the CP→AS runtime composer landed; batch-55 adds CXA-2 as bounded residual after producer-loop evidence landed; batch-56 adds CXA-1 after the AS→IS producer and edge-scope audit landed. |
| RETIRE-READY | **0 active (bucket EMPTY post-batch-51)** | OD-3 + OD-6 transited RETIRE-READY → RETIRED at batch-51 (PR #200). |
| PARTIAL | **0** | Empty after batch-56. CXA-1 moved to SUBSTANTIVE_RETIRED after the AS→IS edge-scope audit and resolver-bound secret-fetch write landed. |
| STILL-BOUNDED | **0** | Empty after batch-55 and remains empty after batch-56. |
| RETIRED-AS-AUTHORING-ONLY | **8** (of the 54 RETIRED) | accounting (i): IS-4, IS-10, AS-9, CP-12, CP-23, OD-1, OD-7, OD-8 (accounting (ii) = 9, adds CP-24). The H_T contract is the typed declaration itself; no runtime behavior (sub-species 10 categorical-mismatch). |
| RETIRED-AS-BOUNDED-RESIDUAL | **3** (of the 54 RETIRED — *counted*) | CP-16 (memory, batch-44) + OD-6 (OTLP, batch-51 — FIRST in ledger) + CXA-2 (CP→IS durable recovery, batch-55). Production substrate dormant or post-MVP at MVP; substantive close deferred to a real deployment/recovery surface (X-AL-2 §5.3). |

**Decomposition status (R-002 RESOLVED 2026-05-31) + R-700 draft correction (2026-06-01):** R-002 mapped all non-RETIRED rows *in the per-axis `§4.1` view* to R-NNN entries — IS-2 (R-003 + R-001-h-t-is-2-retired), OD-3 (R-007), OD-4 (R-008), OD-6 (R-009), AS-8e (R-005), AS-8f (R-006); R-001 (OD-5) + R-004 (AS-8d) reconciled stale BLOCKED → RESOLVED. **The R-700 draft surfaced that the R-002 survey covered only `§4.1`, which excludes the CXA axis (no `§4.1` file) + CP-17's SB-INDEF reclassification — so 5 non-RETIRED rows (`CXA-1`/`CXA-2`/`CXA-3`/`CXA-4` + `CP-17`) have NO `R-NNN` entries.** Recommended follow-on (draft §C item 2): an `R-002`-style Surface-I decomposition pass over CXA + CP-17. **→ CLOSED at PR #246 (R-700 PART C item 2):** grounding found CXA-1/2/3/4 already had `R-CXA-1..4` (authored #209); NEW `R-010-cp-17-files-indefinite` authored for CP-17 → all 5 flagged rows now have dedicated entries. Ratified at the Phase-8 graduation (2026-06-02).

---

## Drift detection log


_Showing the 10 most recent drift/reconciliation events. The full audit history (183 events) is archived at `.harness/roadmap_drift_log_archive.md`._

| Date | Source | Resolution |
|---|---|---|
| 2026-07-26 | session-start hook reported stored=9b206c8417d5 computed=f14c14a35ce3, predating this arc (from fc4e0b0f, the post-#1116 refresh) | resolved by this refresh recomputing against current HEAD; root cause was the routine one-commit lag per §12.2.1, not investigated further mid-arc since B-78 was already the derived next-action |
| 2026-07-24 | Session-start audit, autonomous /loop continue — the post-#1100 terminating refresh (commit `8ceab938`) updated the hash/head/recently-completed fields but left the Next-action prose stale: it still named `R-600-pattern-bake-in-sweep`'s "tripped cadence" as the highest-priority next action, even though PR #1100 (landed in the SAME merge as the terminating refresh) was itself that cadence-9 sweep closing the tripped cadence. | Corrected in this direct commit: Next-action re-derived (R-600 cadence-9 closed, no other ACTIVE mode-agnostic infra item due; recommend opening B-70's spec-leg arc or continuing the registered_finding grounding sweep). Also performed this session's own grounding pass over the `registered_finding` file-order queue (§12.4.1): B-70 grounded, Class 2 fork filed, register row flipped `registered_finding` → `design_substrate_gated` (11 registered_finding remain: B-16/B-30/B-44/B-45/B-56/B-57/B-66/B-68/B-69/B-71/B-72, all previously grounded and correctly dormant-awaiting-a-trigger per prior sessions). Hash `a355fb8a67bd` → `ccfe42fe2781` (state at `8ceab938`, open PRs empty, fork count 98, batch-57). |
| 2026-07-22 | Post-#1083 merge - merge-gate 3-lens review (concurrency APPROVE; test-witness BLOCK->fixed->APPROVE; spec-conformance BLOCK on AC 9 scope wording -> reconciled via operator AskUserQuestion, bundle-per-U-IS-19-precedent selected) | Merged at 5146c461; main CI green post-merge; branch feat/u-is-20-rotation-correlation-id-carrier auto-deleted by gh pr merge |
---

## Audit checklist (run at session start)

- [ ] `workspace_state_hash` matches computed value per recipe above
- [ ] All open PRs at GitHub appear in `In-flight`
- [ ] `recently_completed` reflects last 5 merged PRs
- [ ] `latest_retirement_batch` matches `ls .harness/phase-7d-retirement-events-batch-*.md | tail -1`
- [ ] No `R-NNN` at `Project_Roadmap_v1.md` §5 has `status: ACTIVE` while its `depends_on` are not all RESOLVED (re-derive per §4)

If any check fails → HALT, route per `Project_Roadmap_v1.md` §7.1 step 4.

---

*End of dashboard. Master roadmap at `Project_Roadmap_v1.md`. Enforcement at `CLAUDE.md` §12.*
