# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `deb243dcf17d` |
| `last_refreshed` | 2026-07-23T00:00:00Z |
| `git_head` | `ea36044f` — post-#1084 terminating roadmap refresh merge (PR #1085); one-commit §12.2.1 fixed-point catch-up, no new substantive merge |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-57.md` |
| `open_fork_doc_count` | 96 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**Purpose.** Section 02 names the next Claude/Codex-executable frontier. Completion history lives in `Recently completed`; the full remaining itemization lives in `Remaining forward work` (next section).

**Frontier:** B-33-A IMPL LEG ARC (ii) CLOSED at PR #1084 (the genuinely 3-axis CP+OD+Runtime spec+plan rider extending `verify_rotation_6_steps`: CP spec v1.104→v1.105 §20.3.1 row 7 amended + NEW §20.3.2 `RotationPairEvidenceProvider` Protocol; OD spec v1.34→v1.35 NEW §24.8 `find_rotation_pair_evidence`; Runtime spec v1.104→v1.105 NEW §13.6 composition-root inputs; CP/OD/Runtime plan deltas v2.41/v2.30/v2.53; CXA v2.22 NEW §2.3.10 `R-planned`). 4 out-of-family codex review rounds, 24 findings fixed (window-membership authenticity check, `RotationPairEvidence.signatures_verified` construction-time coherence validator, correlation-id echo check, lone-entry-is-a-breach correction, wrong-hash-primitive fix, and 4 clearance-marker/CLAUDE.md staleness propagations) — stopped at round 4 per `advisor()` reconciliation (`[[non-convergent-adversarial-hardening-arms-race]]`: round-N fixes were generating round-N+1 findings, not surfacing residual defects). Two residuals explicitly REGISTERED (not fixed) as leg-(iii) dependencies: (a) the IS-window↔OD-pair join's correlation-id-value-equality binding is the ratified Option A design itself, not a defect; (b) PR #938's already-landed `verify_rotation_pairs` UUID check is parseable-not-canonical (pre-existing, out of this leg's spec-only scope). Followed by terminating refresh PR #1085. `.harness/forward-register.yaml` B-33 row stays `open` — this leg closes only arc (ii), spec+plan surface. **Next: B-33-A impl leg arc (iii)** — the actual CODE: `verify_rotation_6_steps`'s `rotation_window_entries`/`evidence_provider`/`key_identity_resolver` params + IS-side subset-membership check (via `harness_is.entry_hash.compute_response_hash`) + the CP-owned `RotationPairEvidenceProvider` Protocol/DTO/exceptions, OD's `find_rotation_pair_evidence` accessor (C-OD-24 §24.8, U-OD-56), and the Runtime composition-root adapter (U-RT-147) — all mutation-probed per PD-8, all currently producing only the explicit-INCOMPLETE disposition per design (no crypto verifier / write-path producer exists yet). Ground against the merged spec+plan text at HEAD before implementing — do not re-derive from memory of this session.


## Remaining forward work

**The full-spec build (R-FS-1).** The single full-spec umbrella **R-FS-1** has no `B-*` forward build arcs remaining and is RESOLVED after manual Tier-1 gates G1.4/G1.7/G1.8 were signed. `R-CL-Q1`, `R-CL-Q2`, `R-CL-Q3`, `R-CL-Q4`, `R-CL-D1`, and `R-CL-C1` are RESOLVED; stale governance entries `R-IF-114` and `R-IF-115` are RESOLVED; `R-600-pattern-bake-in-sweep` cadence-8 is ACTIVE-SURVEYED (promoted `mutation-probe-as-load-bearing-witness` as PD-8 at workflow v1.18 — the cadence-7 card-frontier flag, now closed); `R-600-codex-out-of-family-review` is RESOLVED. The new operator-selected implementation frontier is the full memory substrate build below.

**Full memory substrate build.** The approved design packet from PR #853 is now implemented through the planned provider-free closeout sequence. U-MEM-01 is merged at PR #855, U-MEM-02 is merged at PR #857, U-MEM-03 is merged at PR #859, U-MEM-04 is merged at PR #861, U-MEM-05 is merged at PR #863, U-MEM-06 is merged at PR #865, U-MEM-07 is merged at PR #867, U-MEM-08 is merged at PR #869, U-MEM-09 is merged at PR #871, U-MEM-10 is merged at PR #877, U-MEM-11 is merged at PR #879, U-MEM-12 is merged at PR #881, U-MEM-13 is merged at PR #883, U-MEM-14 is merged at PR #885, U-MEM-15 is merged at PR #887, U-MEM-16 is merged at PR #889, U-MEM-17 is merged at PR #891, U-MEM-18 is merged at PR #893, U-MEM-19 is merged at PR #895, U-MEM-20 is merged at PR #897, U-MEM-21 is merged at PR #899, U-MEM-22 is merged at PR #901, U-MEM-23 is merged at PR #903, U-MEM-24 is merged at PR #905, and U-MEM-25 is merged at PR #907. No U-MEM forward implementation unit remains. Live Anthropic native-memory plus Claude Code and Codex CLI auth confirmations are recorded by U-MEM-live-confirmations; Antigravity, legacy Gemini, and generic-command remain local live gates until their CLIs/probe are available.

**Single arc→unit source.** The full itemization — every arc + unit in plain language, with status, build position, dependencies, and as-built units — lives in the single structured source **`.harness/arc-ledger.yaml`** (derived by `tools/arc_ledger.py`, rendered in the dashboard's Arc & unit map; the forward `B-*` register is shown with decompose-at-open markers). The spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` carries every surfaced boundary's rationale; per-arc grounding leads at `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` (re-ground at arc-open, presence-not-correctness).

**Frozen order** (B1→B3→E→B2→R→B4→CA→B5→B6→B7→M) — **COMPLETE, 11/11.** R-FS-1 standalone `B-*` register is **69 closed / 0 forward / 0 gated / 4 resolved** in `.harness/arc-ledger.yaml`; `snapshot.rfs1_status: resolved` and `closure_gate.py` G1.1 = **0+0**. Manual Tier-1 closure gates G1.4/G1.7/G1.8 are recorded at `.harness/r-fs-1-tier1-manual-signoff.json`; **R-CL-Q1**, **R-CL-Q2**, **R-CL-Q3**, **R-CL-Q4**, **R-CL-D1**, and **R-CL-C1** are resolved.

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(none)* | — | — | No open PRs at refresh time. |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #1084 | 2026-07-23 | B-33-A spec+plan leg (ii): CP+OD+Runtime rider extending verify_rotation_6_steps with real IS-anchored window presence/uniqueness + OD-anchored evidence checks (4 out-of-family review rounds, 24 findings fixed; leg iii impl remains) |
| PR #1083 | 2026-07-22 | B-33-A impl leg arc (i) merged: U-IS-20 rotation_correlation_id sidecar carrier (IS spec v1.12 sec5.6/sec7.7) - StateLedgerEntry/EntryPayload field + canonical-round-trip UUID validation + omit-when-None hash coverage + verify_rotation_window composed validator. Also fixed a MemoryOperationEntry codec gap (found by codex round 1) + a tautological legacy-round-trip test (found by merge-gate test-witness lens); operator ratified bundling 2 downstream field-set-assertion fixes into this PR per the U-IS-19 (PR 537) precedent after a merge-gate spec-conformance BLOCK on AC 9 wording. Next: B-33-A impl leg arc (ii) - the separate, not-yet-decomposed CP-axis verify_rotation_6_steps extension arc. |
| PR #1082 | 2026-07-22 | B-33-A spec leg merged: IS spec v1.11→v1.12 (NEW §5.6 `rotation_correlation_id` sidecar, C-IS-05; NEW §7.7 join-key read-side invariants, C-IS-07) + IS plan v2.7→v2.8 (NEW U-IS-20). 5 codex rounds to convergence — round 4 re-raised the carrier-shape question a 2nd time (labeling non-fork per `advisor()`, not re-litigated); rounds 4-5 found 2 real security-depth gaps (chain-head tamper coverage; OD-anchored window-boundary trust), both correctly registered as impl-leg-(ii)-owned (U-IS-20 Note (d)) rather than spec-scope-creeping. B-33 itself stays open; forward-register row flipped to `open`. Next: B-33-A impl leg arc (i), U-IS-20 code. |
| PR #1081 | 2026-07-22 | B-59-A impl leg merged: U-RT-146 cross-bootstrap capacity-authority continuity — `FrameLedger` split out of `SubAgentDispatchExecutor`, adopted process-lifetime via `adopt_or_create_process_capacity_ledger()` at `stage_5_loop_init.py`; typed `CapacityAuthorityBudgetShrinkError`; 14 PD-8 mutation-probed tests. Merge-gate round-1 BLOCK (test-witness lens: substring-count lock check + 2 untested ctor guards) fixed + re-verified round-2 all-APPROVE. B-59 CLOSED (spec #1080 + impl #1081). |
| PR #1080 | 2026-07-22 | B-59-A spec leg merged: CP v1.103→v1.104 (§25.11 admission-guarantee row-2 span clarification) + Runtime v1.103→v1.104 (NEW §14.8.10.6 cross-bootstrap capacity-authority continuity + RT-FAIL-CAPACITY-AUTHORITY-BUDGET-SHRINK taxonomy row) + Runtime plan v2.52 (NEW U-RT-146); no CP plan unit owed; 5 codex rounds to clean convergence (ledger-vs-executor split + lock-identity structural witness). |
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
| 2026-07-22 | Post-#1083 merge - merge-gate 3-lens review (concurrency APPROVE; test-witness BLOCK->fixed->APPROVE; spec-conformance BLOCK on AC 9 scope wording -> reconciled via operator AskUserQuestion, bundle-per-U-IS-19-precedent selected) | Merged at 5146c461; main CI green post-merge; branch feat/u-is-20-rotation-correlation-id-carrier auto-deleted by gh pr merge |
| 2026-07-22 | **Post-#1082 follow-on refresh — PR #1082 B-33-A spec leg merged at `eea53a94`, then a drift-log archive trim at `a1729666`; clean terminating refresh follows.** | Hash `47abe4730628` → `4786441b49bf` (state at `a1729666`, open PRs empty, fork count 96, batch-57). PR #1082 closes the B-33-A spec leg: IS spec v1.11→v1.12 (NEW §5.6 `rotation_correlation_id` D-derivative sidecar on `StateLedgerEntry`/`EntryPayload`, C-IS-05, hash-covered per the §5.1/§5.4 typed-sidecar idiom, canonical-round-trip UUID validation; NEW §7.7, C-IS-07, reframed across 5 codex rounds from "presence/uniqueness checkable in isolation" to "a JOIN KEY, not a trust anchor" — real verification trust requires the window boundary be OD-anchored against the dual-signature pair, and a chain-head rotation entry needs independent OD-signature coverage since `verify_chain` has no successor to catch head-of-chain tampering) + IS plan v2.7→v2.8 (NEW U-IS-20, one public composed non-emptiness→presence→uniqueness validator). Round 4 re-raised the ratified carrier-shape question a 2nd time; `advisor()`-triaged as a labeling non-fork (identical artifact either way, no open-dict primitive exists at IS to literally implement) and not re-litigated. Both genuine security-depth gaps (chain-head coverage; OD-anchored boundary trust) found at rounds 4-5 are correctly registered as impl-leg-(ii)-owned at U-IS-20 Note (d), not solved at this spec-only leg. `B-33` itself stays OPEN (forward-register flipped `design_substrate_gated`→`open`); external dependencies for the CP-axis impl leg (`B-22`/`B-36`/`B-47`) are all closed. Next-action re-derived to "B-33-A impl leg arc (i) — U-IS-20 IS-axis code." |
| 2026-07-22 | **Post-#1081 follow-on refresh — merge-gate log recorded as non-terminating at `369780d7`; clean terminating refresh follows.** | Hash `9a101f910d27` → `c4113132a5c8` (state at `369780d7`, open PRs empty, fork count 96, batch-57). PR #1081 closes the B-59-A impl leg (U-RT-146): the `SubAgentDispatchExecutor` frame-budget accounting is factored into a separately-adoptable `FrameLedger` adopted process-lifetime at `stage_5_loop_init.py`; new `CapacityAuthorityBudgetShrinkError`; 14 PD-8 mutation-probed tests (11 unit + 1 real two-bootstrap integration test + 1 AST-based lock-nesting structural witness). Merge-gate 3-lens round-1: concurrency APPROVE, spec-conformance APPROVE, test-witness BLOCK (substring-count lock check couldn't detect scope-narrowing; 2 ctor guard branches untested) — both fixed (AST ancestry check + 2 new tests), mutation-verified, round-2 all-APPROVE. 2 out-of-family codex rounds converged clean on the diff itself. B-59 now fully closed (spec leg #1080 + impl leg #1081). The merge-gate-log.md append (`369780d7`) is a separate, non-`roadmap_status.md`-only commit per §12.2.1 "bundled changes drop the prefix"; this roadmap-status-only commit is the terminating fixed point. Next-action re-derived to "B-33-A spec leg — IS rotation-correlation carrier." |
| 2026-07-19 | **Post-#1060 follow-on refresh — B-48 close-out + B-60/B-61/B-62 registration + roadmap refresh committed as non-terminating at `0a736dc8`, then a drift-log archive trim at `0df9dccf`; clean terminating refresh follows.** | Hash `85275a6baabb` → `c5d84d826cc2` (state at `0df9dccf`, open PRs empty, fork count 93, batch-57). The forward-register.yaml + post-phase-8-forward-register.md + roadmap_status.md updates were bundled into one direct-to-main commit (B-48 status flip to closed, B-60/B-61/B-62 registered, next-action re-derived); per §12.2.1 "bundled changes drop the prefix," that commit did not use the `ops: roadmap status refresh` prefix. A second, purely mode-agnostic commit then archived 2 trimmed drift-log entries (also non-`roadmap_status.md`-only, so also non-terminating). This third, roadmap-status-only commit is the §12.2.1-compliant terminating fixed point. |
| 2026-07-19 | **Post-#1060 terminating refresh — PR #1060 B-48 executor impl arc merged at `c813980a`; §12.2 owed follow-on.** | Hash `64a8edeadf51` → `85275a6baabb` (state at `c813980a`, open PRs empty, fork count 93, batch-57). PR #1060 closes the B-48 apply arc: U-CORE-03 + U-CP-101 + U-RT-140..144 (grow-on-demand thread executor, occupied+N+S shared frame budget, atomic whole-fan-out admission, three-part cancellation fence, exactly-once lease release) + U-CP-82/85/86/88/89 amendments (admission gated at all four fan-out construction sites) + B-39 interim sequential-dispatch constraint + U-IS-11 §7.6. 10 rounds of decorrelated pre-merge review (merge-gate 3-lens + out-of-family Codex) surfaced 35 findings, all PD-8-fixed with mutation-probed witnesses. Round 10 (operator-approved final gate) converged clean on rounds 1-9's fixes; codex round-10 surfaced 3 further findings scoped against pre-existing cancellation-fence coverage from rounds 4-8 (not a round-9/10 regression) — escalated per the pre-committed terminal rule, operator selected "register + merge now," registered as B-60/B-61/B-62. Next-action re-derived to "open the B-51/B-52/B-54/B-53 impl arcs." This terminating refresh updates `.harness/roadmap_status.md` to pin the merge-commit fixed point. |
| 2026-07-11 | **Post-#935 follow-on refresh — arc-ledger.yaml + roadmap updates committed as non-terminating at `e39de0e5`; clean terminating refresh follows.** | Hash `6f4ec726983a` → `208f6ff224da` (state at `e39de0e5`, open PRs empty, fork count 88, batch-57). Arc-ledger.yaml was included in the first refresh commit rather than PR #935; this second refresh is the §12.2.1-compliant terminating fixed point. |
| 2026-07-11 | **Post-#935 terminating refresh — PR #935 B-18-KEEPALIVE merged at `f86ddfa5`; §12.2 owed follow-on.** | Hash `6ae1095b56c9` → `6f4ec726983a` (state at `f86ddfa5`, open PRs empty, fork count 88, batch-57). PR #935 closes B-18-KEEPALIVE (R-FS-2 Wave 1 first arc): boot-time `max_tokens=1` Anthropic prompt-cache prewarm + 240s daemon keep-alive; `PrewarmOutcome(StrEnum)` + `RuntimeLLMDispatcher.prewarm()`; `HarnessContext.bare_llm_dispatcher` stash; stage-5 best-effort prewarm; `_keepalive_loop` (1h-TTL excluded, 3-failure self-disable, cancel+await before `_shutdown`); runtime spec v1.98→v1.99 + clearance marker; 16 hermetic tests; pyright 0/0/0; grok APPROVE; CI 16/16. Arc-ledger 79→80 closed, 15→14 registered. Next-action re-derived to "open B-WAL-F1-01-EXACTLY-ONCE". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge-commit fixed point. |
| 2026-07-10 | **Post-#925 terminating refresh — PR #925 B-18-3C-PREWARM-COHORTKEY merged at `95e6f27f`; §12.2 owed follow-on.** | Hash `59fa3e76e762` → `39358e3edbb0` (state at `95e6f27f`, open PRs empty, fork count 88, batch-57). PR #925 closes COHORTKEY: `@runtime_checkable CohortKeyCapable(Protocol)` + `cohort_key() -> str | None` dispatcher-oracle replaces the binary predicate; `RuntimeLLMDispatcher` logic-bearing leaf + delegation stubs in 3 wrappers; RK-13 chain witness; CP spec v1.87→v1.88 + clearance; 16 witnesses; 5433 green; Fable-5 NO BLOCKING. arc-ledger standalone 70→71. B-18-3C-PREWARM-DEFAULT-ON prerequisite met. Next-action re-derived to "open B-18-3C-PREWARM-DEFAULT-ON (flip `concurrent_cache_warmup` default True, ADR-D4 §1.8(f))". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge-commit fixed point. |
| 2026-07-10 | **Post-#924 terminating refresh — PR #924 B-18-3C-PREWARM merged at `0ddf7395`; §12.2 owed follow-on.** | Hash `ae0e7892abea` → `59fa3e76e762` (state at `0ddf7395`, open PRs empty, fork count 87, batch-57). PR #924 closes the B-18 concurrent-prompt-cache warm-up arc: ADR-D4 §1.8 opt-in `concurrent_cache_warmup` D4-tunable + `_same_prefix_cohort()` binary predicate + two-phase `_proceed_fanout()` (serialize branch[0]/gather branches[1..N-1]); CP spec v1.86→v1.87 + clearance; 6 witnesses + 5417 green; CI 16/16. arc-ledger B-18-3C-PREWARM status: `closed · #924`. Next-action re-derived to "open B-18-3C-PREWARM-COHORTKEY (Fork B Class 2 fork doc → implement `cohort_key() -> str | None` Protocol method)". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge-commit fixed point. |
| 2026-07-10 | **Post-DDR-review terminating refresh — Fable-5 decorrelated review folded into the `B-18-3C-PREWARM` DDR at `31f3f6ff`; §12.2 owed follow-on.** | Hash `80fc94ae439f` → `ae0e7892abea` (state at `31f3f6ff`, open PRs empty, fork count 87, batch-57). With the advisor tool down, **Fable 5 via `Agent(model:"fable")` was adopted as the decorrelated fallback reviewer** (standing operator directive) and ran the pre-commit review of the DDR → SOUND-WITH-AMENDMENTS, catching 3 must-fix hazards (H1 bare-await ledger-loss, H2 predicate misses the memory packet, H3 empty-branch_plan IndexError) now authoritative at DDR §11. Next-action re-derived to "build §5-as-amended-by-§11". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the review-cleared fixed point. |
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
