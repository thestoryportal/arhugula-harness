# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `0ec5ddeebf9d` |
| `last_refreshed` | 2026-07-15T00:00:00Z |
| `git_head` | `002c82f3` — B-39 register status update, no code |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-57.md` |
| `open_fork_doc_count` | 91 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**Purpose.** Section 02 names the next Claude/Codex-executable frontier. Completion history lives in `Recently completed`; the full remaining itemization lives in `Remaining forward work` (next section).

**Frontier.** R-FS-1 Tier-1 is closed. The frozen order is complete (11/11), the standalone `B-*` register derives **69 closed / 0 forward / 0 gated / 4 resolved**, `closure_gate.py` G1.1 is **0+0**, automatable Tier-1 predicates pass, and manual G1.4/G1.7/G1.8 sign-off is recorded at `.harness/r-fs-1-tier1-manual-signoff.json`.

**Current next action.** **PR #1005 CLOSED (this refresh) — corrective fix on PR #1003's branch-hygiene mechanism.** PR #1003's `loop_gc_branches` scanned LOCAL `git branch` output cross-referenced against GitHub's historical merged-PR list — operator caught this producing misleading results ("21 branches held") entirely disconnected from the actual remote state, since a local ref can persist long after its GitHub-side branch is deleted. PR #1005 removes `loop_gc_branches` + its helpers + the `branch-hygiene-report`/`-sweep` justfile recipes + their tests entirely, and rewrites `ship-pr`'s close-out step to a direct recipe operating on the REMOTE (GitHub) branch list: verify the PR is MERGED into the default branch and its `headRefName` matches the expected arc branch (guards a mistyped PR# resolving to a different valid merged PR), fail closed unless post-merge CI on the merge commit is exactly `success`, then a lease-guarded remote delete (atomically refuses if the remote tip moved since verification). Documents that loop mode hard-blocks this destructive-git step by design (no allowlist bypass) and should defer via `tools/04-loop/defer.sh`. 5 rounds of out-of-family Codex review to convergence; `just check` clean (5788/10/33/1); operator-confirmed merge. Also fixed: the 3 actual GitHub branches remaining post-#1003 (`b-branch-hygiene-close-out`, `ground-every-arc-directive-post-999`, `roadmap-refresh-post-1003`) were deleted directly via the operator's manual verification — GitHub now shows only `main` plus whatever this arc's own branch resolves to once this refresh lands. **`B-31` grounding remains next up** (paused-child resume guard doesn't validate `child_workflow_id` identity — see prior refresh for detail; `advisor()` still owed before implementation). `B-24`/`B-25`/`B-27` Class-1 fork docs remain FILED, awaiting operator ratification. Per §4's derivation rule there is still no *R-NNN ACTIVE-queue* candidate. The standalone `B-*` register still derives **0 open / 0 forward** (`just forward-register --check` → `0 open / 3 design_substrate_gated / 10 registered_finding / 2 operator_gated / 1 held / 23 closed`) — run `just forward-register --open` for the live operator-selectable item list instead of re-deriving it here. Absent an operator pick from this set, the standing recurring lanes are: (a) resume/finish grounding `B-31`, then continue the register sweep (`B-32` next, adjacent same-carrier-family item), (b) R-600 (next due ~10 PRs out, or sooner if a new candidate reaches independent instance-cardinality ≥2), or (c) a fresh non-recurring frontier (§12.4.1 no-parking directive). **Standing note:** operator has granted forward-work merge permission without per-instance HIL, conditioned on CI fully passing green before any merge — apply this going forward in place of the prior per-PR "Merge now" confirmation pattern.

**Recurring lanes** continue on cadence: `R-600-pattern-bake-in-sweep` (cadence-8 closed this refresh, PD-8 promoted; next due ~10 PRs out) and `R-IF-roadmap-refresh`. Out-of-family review continues as a codified default gate, not as an open roadmap arc.

**Do not re-open as next action.** The R-FS-1 `B-*` build register is closed; R-FS-2's follow-on register is also closed (G2, PR #960); historical Next-action prose below this refresh is lineage only. Closed/parked surfaces remain: `R-411/412/420/421/430`, `R-500`, `R-810/820/830`, `R-008`/OD-4, `R-CXA-1/2/4`, `R-100-*`, `R-300-*`, and `R-901`.

---

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
| #002c82f3 | 2026-07-15 | B-39 re-grounded (2026-07-15 no-parking sweep): all 3 design constraints confirmed still accurate against HEAD by direct read; status moved registered_finding -> design_substrate_gated (needs a Class 1 fork proposing the resume_context threading mechanism before code, per X-AL-3). No code change. Continuing sweep to B-38 next. |
| #1019 | 2026-07-15 | B-37 closed — remote MCP streamable-HTTP transport residuals (latent TypeError fix, auth_secret_name credential field, TLS/trust_env security hardening across 3 codex-review rounds + 3-lens merge-gate all-approve) |
| PR #1017 | 2026-07-15 | Closed B-35: qa_evidence_matrix.py --check was live-red (12 contracts with no test-file citation, C-IS-14 phantom + 11 C-MEM-*) with zero CI signal -- neither it nor test_closure_gate.py was wired into any CI job. C-IS-14 was a documented phantom contract id (runtime spec v1.93's own change-note); moved the exclusion set from closure_gate.py's local incomplete copy to a shared overlay.py::DOCUMENTED_NON_CONTRACTS. 10 of 11 C-MEM-* contracts already had a real passing test -- added a one-line contract-id citation to each. C-MEM-01 (memory-plane-boundary architectural contract) was a genuine gap: added test_memory_plane_boundary.py with two new tests, both mutation-probed against real production code. Wired both test modules + both --check scripts into a new blocking CI job. Side effect: closure_gate.py's Tier-1 automatable predicates now all PASS (was blocked by the same 2 orphans) -- reconciles the tool with an already-RESOLVED R-CL-C1 certification. Merge-gate round 1 (all 3 lenses APPROVE) surfaced two worth-fixing items I self-corrected: my own test docstring accidentally self-cited C-MEM-01 (fixed), and test_closure_gate.py's G1.3 mock couldn't distinguish a hardcoded-True mutation from a genuine pass (added + mutation-probed a new test). Registered B-40 for a real, out-of-scope, pre-existing concurrency gap the reviewer surfaced (memory operation ledger has no cross-process write serialization). just check clean throughout (5796 passed). No standing Claude-derivable next action beyond the R-600 recurring lane or continuing the register sweep (B-37 next, adjacent same-family item). |
| PR #1015 | 2026-07-15 | Closed B-32's pause_reason half: parent pause_reason now checks a nested peer/worker child's OWN pause_reason directly (both PARALLELIZATION and ORCHESTRATOR_WORKERS/HIERARCHICAL_DELEGATION sites) instead of mere non-emptiness, fixing a mislabel Codex caught in a first draft. Two rounds of out-of-family Codex review plus two rounds of the merge-gate 3-lens review: round 1 found (a) the ORCHESTRATOR_WORKERS/HIERARCHICAL_DELEGATION site had zero test witness and (b) design-substrate/Spec_Control_Plane_v1_97.md section21's registered-forward-work note still canonically claimed gaps (b)/(c) were coupled and must land together -- both legitimate, both fixed (second-site tests added + mutation-probed; CP spec delta v1.99->v1.100 correcting the stale framing, with its own follow-on citation-precision fix after a non-blocking round-2 finding). Register: B-32 closed (pause_reason half only); B-39 filed for the still-open per-child HITL response-routing half with 3 concrete design constraints from a reverted first attempt. just check clean throughout (5794 passed). No standing Claude-derivable next action beyond the R-600 recurring lane or continuing the register sweep (B-33 next, adjacent same-family item). |
| PR #1013 | 2026-07-15 | Operator caught that reflect-for-self-improvement + /context-save were skipped at both of this session's prior arc closes (PR #1009 merge-gate skill, PR #1011 B-31 fix) -- a 5th recurrence of a documented-but-unenforced discipline (memory entry existed since #640/#642/#723 but prose alone wasn't a reliable trigger). Made it structural: ship-pr/SKILL.md now carries a mandatory Reflect + /context-save step that fires at every arc close (not only R-NNN closes), cross-referenced from roadmap-continue's step 6. Docs/skill-only, no code -- merge-gate's own scope rule correctly skipped it. Now executing the newly-mandatory reflect + /context-save step for this session before continuing. |
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
| 2026-07-11 | **Post-#935 follow-on refresh — arc-ledger.yaml + roadmap updates committed as non-terminating at `e39de0e5`; clean terminating refresh follows.** | Hash `6f4ec726983a` → `208f6ff224da` (state at `e39de0e5`, open PRs empty, fork count 88, batch-57). Arc-ledger.yaml was included in the first refresh commit rather than PR #935; this second refresh is the §12.2.1-compliant terminating fixed point. |
| 2026-07-11 | **Post-#935 terminating refresh — PR #935 B-18-KEEPALIVE merged at `f86ddfa5`; §12.2 owed follow-on.** | Hash `6ae1095b56c9` → `6f4ec726983a` (state at `f86ddfa5`, open PRs empty, fork count 88, batch-57). PR #935 closes B-18-KEEPALIVE (R-FS-2 Wave 1 first arc): boot-time `max_tokens=1` Anthropic prompt-cache prewarm + 240s daemon keep-alive; `PrewarmOutcome(StrEnum)` + `RuntimeLLMDispatcher.prewarm()`; `HarnessContext.bare_llm_dispatcher` stash; stage-5 best-effort prewarm; `_keepalive_loop` (1h-TTL excluded, 3-failure self-disable, cancel+await before `_shutdown`); runtime spec v1.98→v1.99 + clearance marker; 16 hermetic tests; pyright 0/0/0; grok APPROVE; CI 16/16. Arc-ledger 79→80 closed, 15→14 registered. Next-action re-derived to "open B-WAL-F1-01-EXACTLY-ONCE". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge-commit fixed point. |
| 2026-07-10 | **Post-#925 terminating refresh — PR #925 B-18-3C-PREWARM-COHORTKEY merged at `95e6f27f`; §12.2 owed follow-on.** | Hash `59fa3e76e762` → `39358e3edbb0` (state at `95e6f27f`, open PRs empty, fork count 88, batch-57). PR #925 closes COHORTKEY: `@runtime_checkable CohortKeyCapable(Protocol)` + `cohort_key() -> str | None` dispatcher-oracle replaces the binary predicate; `RuntimeLLMDispatcher` logic-bearing leaf + delegation stubs in 3 wrappers; RK-13 chain witness; CP spec v1.87→v1.88 + clearance; 16 witnesses; 5433 green; Fable-5 NO BLOCKING. arc-ledger standalone 70→71. B-18-3C-PREWARM-DEFAULT-ON prerequisite met. Next-action re-derived to "open B-18-3C-PREWARM-DEFAULT-ON (flip `concurrent_cache_warmup` default True, ADR-D4 §1.8(f))". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge-commit fixed point. |
| 2026-07-10 | **Post-#924 terminating refresh — PR #924 B-18-3C-PREWARM merged at `0ddf7395`; §12.2 owed follow-on.** | Hash `ae0e7892abea` → `59fa3e76e762` (state at `0ddf7395`, open PRs empty, fork count 87, batch-57). PR #924 closes the B-18 concurrent-prompt-cache warm-up arc: ADR-D4 §1.8 opt-in `concurrent_cache_warmup` D4-tunable + `_same_prefix_cohort()` binary predicate + two-phase `_proceed_fanout()` (serialize branch[0]/gather branches[1..N-1]); CP spec v1.86→v1.87 + clearance; 6 witnesses + 5417 green; CI 16/16. arc-ledger B-18-3C-PREWARM status: `closed · #924`. Next-action re-derived to "open B-18-3C-PREWARM-COHORTKEY (Fork B Class 2 fork doc → implement `cohort_key() -> str | None` Protocol method)". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge-commit fixed point. |
| 2026-07-10 | **Post-DDR-review terminating refresh — Fable-5 decorrelated review folded into the `B-18-3C-PREWARM` DDR at `31f3f6ff`; §12.2 owed follow-on.** | Hash `80fc94ae439f` → `ae0e7892abea` (state at `31f3f6ff`, open PRs empty, fork count 87, batch-57). With the advisor tool down, **Fable 5 via `Agent(model:"fable")` was adopted as the decorrelated fallback reviewer** (standing operator directive) and ran the pre-commit review of the DDR → SOUND-WITH-AMENDMENTS, catching 3 must-fix hazards (H1 bare-await ledger-loss, H2 predicate misses the memory packet, H3 empty-branch_plan IndexError) now authoritative at DDR §11. Next-action re-derived to "build §5-as-amended-by-§11". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the review-cleared fixed point. |
| 2026-07-10 | **Post-DDR terminating refresh — `B-18-3C-PREWARM` design decision record committed at `6ff3a4cd`; §12.2 owed follow-on.** | Hash `50c6f6115819` → `80fc94ae439f` (state at `6ff3a4cd`, open PRs empty, fork count 87, batch-57). The pre-warm arc (ADR-D4 §1.8, highest-blast-radius fan-out change) was fully grounded this session; build DEFERRED by operator decision (advisor down → the DDR is the advisor-review gate). `.harness/u1-3c-prewarm-design-decision-record.md` captures the gate-carrier (D4-tunable opt-in default-off), same-prefix binary predicate, reuse-`_proceed_branch` integration (PROCEED-only), crash-resume safety, test plan, and §9 open questions. Next-action re-derived to "advisor-review the DDR → build". This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the DDR-commit fixed point. |
| 2026-07-10 | **Post-#923 terminating refresh — PR #923 B-18-CACHE-TTL-OBSERVABILITY merged at `9eacc221`; §12.2 owed follow-on.** | Hash `421ef964ced0` → `50c6f6115819` (state at `9eacc221`, open PRs empty, fork count 87, batch-57). PR #923 closes the decorrelation-validated B-18 deferral: the Anthropic cache-attr extractor now scans the TRANSLATED wire kwargs (`tools → system → messages`) instead of `payload.messages`, recording `anthropic.cache_breakpoint_id`/`cache_ttl_seconds` for the tools/system-block breakpoints uniformly across slices 1/2/3a/3b (pure observability, byte-identical dispatch; runtime spec v1.97→v1.98 + clearance). Verification: pyright 0/0/0; full harness-runtime non-e2e = 2347 passed; decorrelated `just codex-review` CLEAN; CI 16/16 blocking green. This terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge-commit fixed point. |
| 2026-07-04 | **Post-#912 terminating refresh — PR #912 automatic local-first memory substrate integration merged at `e95e7ee8`; §12.2 owed follow-on.** | Hash `ef13fe8aabe6` → `e940e67fa68c` (state at `e95e7ee8`, open PRs empty, fork count 87, batch-57). PR #912 integrates default local memory initialization, docs, runtime wiring, standard tools, prompt packets, and review-readiness fixes for useful policy-filtered memory exposure and durable persistence; deployed package PR #1 is merged at `87c29817`. Verification: PR #912 all checks green; this terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge commit fixed point. |
| 2026-07-03 | **Post-#910 terminating refresh — PR #910 post-#909 roadmap fixed point merged at `6115e0ca`; §12.2 owed follow-on.** | Hash `c3ae3c660bc2` → `ef13fe8aabe6` (state at `6115e0ca`, open PRs empty, fork count 87, batch-57). PR #910 performed the post-#909 terminating refresh after U-MEM live confirmations merged. This follow-on refresh restores the canonical `ops: roadmap status refresh ...` subject prefix for the next refresh commit so the context guard classifies the one-commit dashboard lag as expected. Verification: PR #910 all checks green; this terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge commit fixed point. |
| 2026-07-03 | **Post-#909 terminating refresh — PR #909 U-MEM live confirmations merged at `6a9cb627`; §12.2 owed follow-on.** | Hash `f3f025ab55ab` → `c3ae3c660bc2` (state at `6a9cb627`, open PRs empty, fork count 87, batch-57). PR #909 records the live Anthropic native-memory confirmation and the Claude Code / Codex external CLI auth confirmations, adds the corresponding e2e resume tests, and leaves Antigravity, legacy Gemini, and generic-command as explicit local live gates until their CLIs/probe are available. Verification: PR #909 all checks green; this terminating refresh updates `.harness/roadmap_status.md` and regenerates `tools/dashboard/roadmap.html` to pin the merge commit fixed point. |

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
