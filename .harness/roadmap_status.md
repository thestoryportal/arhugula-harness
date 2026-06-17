# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `4d03a1931cbd` |
| `last_refreshed` | 2026-06-17T08:40:19+00:00 |
| `git_head` | `147bb4d9` — #618 R-FS-1 **B4 Slice 2** (per-role binding **catalog** surface + the `step_id→AgentRole` derivation contract). NEW `harness_cp.per_role_catalog`: `derive_agent_role(step_id)` is the single source of truth for the B1↔B4 derivation (3 inlined `AgentRole(str(step.step_id))` driver sites refactored to it — driver-producer + operator-catalog agree by construction); `validate_per_role_catalog` is the pure live/dead/unbound coherence aid (NOT a runtime gate — respects the committed §14.5.3/§29 fall-through), generic over both manifests. Impl-to-cleared-spec (CP §25.14 + runtime §14.5.3 defer the catalog to impl discretion), no X-AL-3 fork. The "distinct workers → distinct models AND prompts" claim is a contract-bridged composition: PRODUCER (real `execute_workflow` orchestrator-workers fan-out asserts `agent_role == derive_agent_role(step_id)` per worker) + CONSUMER (real wrapper(inner(recording provider)) → distinct model AND prompt per worker) + manifest→map (Slice 1 bootstrap test). Decorrelated: advisor (verification-shape gap → closed by binding the producer test to the contract) + Codex (clean). pyright 0/0/0; ruff clean; harness-cp 1036 passed / 1 xfailed (+9 new). Lags HEAD by one commit (this terminating-refresh fixed point, §12.2.1). Full detail: `git show 147bb4d9` + Recently completed. |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-57.md` |
| `open_fork_doc_count` | 63 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**Purpose.** Section 02 names the next Claude/Codex-executable frontier. Completion history lives in `Recently completed`; the full remaining itemization lives in `Remaining forward work` (next section).

**Frontier.** The single ACTIVE build umbrella is **R-FS-1** (full-spec build beyond MVP; operator directive 2026-06-12). Its capabilities are FROZEN ordered child arcs; §4 derives one next-action from the umbrella so the children stay folded (see `Project_Roadmap_v1.md` §5.0).

**Next = R-FS-1 → B4 Slice 3** — per-step **prompt/role override** on `StepOverride` (today `StepOverride` carries model_binding/engine_class/hitl_placement only; adding a per-step prompt-binding and/or per-step role is a **likely-small CP §6.1 fork** — verify at arc-open whether §6.1's `// additional per-workload fields` extension clause already authorizes it; if not, file the CP spec §6.1 amendment + clearance before impl). **B4 Slice 2 ✅ landed (#618)** — the per-role binding catalog surface (`derive_agent_role` one-source-of-truth contract + `validate_per_role_catalog` coherence aid) + the distinct-workers→distinct-models-AND-prompts conjunction e2e. **Slice 1 ✅ (#616)** — per-role PROMPT threading + IS v1.9 hash coherence. Remaining B4 slices: **Slice 3 (per-step override, next; likely small fork)** → Slice 4 (linear-path role indexing, impl-discretion). Frozen order: B1✅ B3✅ E✅ B2✅ R✅ → **B4 (Slice 1✅ 2✅; 3→4)** → CA → B5 → B6 → B7 → M. Re-ground at arc-open per `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` Arc B4 (Slice 3 = the fork-gated slice) + `.harness/beyond-mvp-capability-boundary-ledger.md` (B4 execution-decomposition; LEADS, presence-not-correctness).

**Recurring lanes** run on cadence alongside: `R-600-*` (pattern bake-in, codex out-of-family review), `R-IF-roadmap-refresh`.

**Do not re-open as next action.** Closed/parked: `R-411/412/420/421/430`, `R-500`, `R-810/820/830`, `R-008`/OD-4, `R-CXA-1/2/4`, `R-100-*`, `R-300-*` (both routing-activation #213 and second-provider #281/#283 RESOLVED), `R-901` (research frontier closed). `R-CL-Q1→C1` (quality track) BLOCKED behind R-FS-1 (full-spec runs once, on the complete harness).

---

## Remaining forward work

**The full-spec build (R-FS-1).** All remaining forward build work is child arcs of the single ACTIVE umbrella **R-FS-1** (operator FULL-SPEC directive 2026-06-12 — nothing deferred; every capability built beyond MVP).

**Single arc→unit source.** The full itemization — all 11 arcs in plain language, with status, build position, before/parallel dependencies, and every atomic unit (real as-built for the 5 done arcs; anticipated slices for the 6 remaining) — lives in **`.harness/r-fs-1-arc-and-unit-map.md`**. The dashboard's Build-progress section parses that file; this section is a pointer, not a second parseable copy (no duplicate to drift). Per-arc grounding leads: `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` (re-ground at arc-open, presence-not-correctness). Spine ledger (every surfaced boundary + standalone arc): `.harness/beyond-mvp-capability-boundary-ledger.md`.

**Frozen order** (B1→B3→E→B2→R→B4→CA→B5→B6→B7→M). DONE: **B1✅ B3✅ E✅ B2✅ R✅** (R incl. L3 LLM_AS_ROUTER #604 + L2 EMBEDDING #606). NEXT: **B4** → then CA → B5 → B6 → B7 → M. Plus **8 standalone design-fork-first `B-*` arcs** and the visibility-only **routing-activation gate** (UNOWNED until a second production provider is configured) — both detailed in the arc-and-unit map.

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(none)* | — | — | No open PRs at refresh time. |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #618 | 2026-06-17 | **feat(cp): R-FS-1 B4 Slice 2 — per-role binding catalog surface + step_id→AgentRole contract.** The catalog deliverable of arc B4 (impl-to-cleared-spec; CP §25.14 + runtime §14.5.3 defer the catalog to impl discretion — no X-AL-3 fork). NEW `harness_cp.per_role_catalog`: **`derive_agent_role(step_id)`** = the single source of truth for the B1↔B4 derivation (the 3 inlined `AgentRole(str(step.step_id))` driver sites refactored to it, so the fan-out driver-producer and the operator-authored catalog agree by construction); **`validate_per_role_catalog`** = the pure live/dead/unbound coherence aid (NOT a runtime gate — a dead binding never fires + an unbound role is the committed §14.5.3/§29 fall-through; generic over both `RoutingManifest` + `PromptSelectionManifest`). Verification is a **contract-bridged composition** (CP⊥runtime axis isolation forecloses one monolithic driver→provider span): PRODUCER — the real `execute_workflow` orchestrator-workers fan-out now asserts each worker's `agent_role == derive_agent_role(step_id)` (the observed producer↔catalog bridge); CONSUMER — `test_b4_slice2_distinct_workers_distinct_models_and_prompts_e2e` drives the real wrapper(inner(recording provider)) stack so two derived-role workers get distinct `model=` AND `system=` at the provider; manifest→map covered by Slice 1's bootstrap test. **advisor** flagged the dispatch-vs-real-driver verification-shape gap (`[[test-bypass-as-runtime-truth-pattern]]`) → closed by binding the producer test to the contract; **Codex** clean. pyright 0/0/0; ruff clean; harness-cp 1036 passed / 1 xfailed (+9 new). → NEXT = **B4 Slice 3** (per-step prompt/role override; likely small CP §6.1 fork). |
| PR #616 | 2026-06-17 | **feat(runtime): R-FS-1 B4 Slice 1 — per-role prompt threading + procedural-tier hash coherence (IS v1.9).** A fan-out branch's `agent_role` now selects + injects its per-role system prompt at the §14.5.2 translate seam (pre-resolved at bootstrap stage 0; unbound/linear roles fall through to the default-role `active_system_prompt`, §14.5.3). The per-role MODEL half already landed (B1 U-RT-114); §14.5.3 assigned per-role PROMPT to B4. **Bundled-absorption arc** (fork + clearance; X-AL-3 guard green): IS spec C-IS-05 §5.2 v1.8→v1.9 widened the procedural-tier hash recipe 3→4 components — NEW `prompt_selection_manifest_sha` (whole-`PromptSelectionManifest` SHA-256, mirroring `routing_manifest_sha`) makes per-role bindings audit-hash-visible, closing the coherence gap per-role injection would reintroduce (the v1.8 recipe hashed only the default-role `active_prompt_version.version_sha` → a `per_role_bindings` flip changed injected content while the hash reported "unchanged" — the §14.5.2 invariant, per-role dimension). Recipe reads `config.prompt_selection_manifest` (NO new HarnessContext carrier / runtime-spec §4 C-RT-04 row — not stage-enriched; **advisor** caught the initial dedicated-carrier draft as C-RT-04 impl-ahead-of-spec drift + a bootstrap-e2e coverage gap, both fixed; **Codex** clean). pyright 0/0/0; ruff clean; 1586 non-integration + 210 integration tests green (+14 new). → NEXT = **B4 Slice 2** (per-role binding catalog). |
| PR #614 | 2026-06-17 | **feat(dashboard): per-arc atomic-unit map — plain-language view of every R-FS-1 arc + unit.** Operator request: all atomic units visible per arc with non-technical descriptions, prioritized, with before/parallel deps. NEW `.harness/r-fs-1-arc-and-unit-map.md` = the single arc→unit home (program→arc→leg→unit primer; all 11 arcs w/ plain-language capability, status, build position, deps, units). DONE arcs (B1/B3/E/B2/R) carry REAL as-built units from `git log` (B1=14, B3=8, E=9, B2=8, R=4); REMAINING (B4/CA/B5/B6/B7/M) carry anticipated slices marked "units decomposed at arc-open" (no fabricated U-* — X-AL-3). `generate.py`: `parse_arc_unit_map()` + `derive_remaining_forward()` make the map the SINGLE source (roadmap_status.md "Remaining forward work" → pointer); new expandable per-arc card render. Verified by in-browser RENDER (no console errors; counts reconcile) + out-of-family codex (caught [P3] maybe-serial collapse → fixed + regression-tested); 14 dashboard tests + ruff green. Mode-agnostic; X-AL-3 clean. → NEXT = B4. |
| PR #612 | 2026-06-16 | **ops(dashboard): R-FS-1 build progress as the headline + legibility (fix misleading "build closure 100%").** Operator feedback: the dashboard ran three overlapping forward-accounting systems with no unifying frame/legends + a mislabeled masthead. Fixes (legibility, no new data sources): masthead ticker → **R-FS-1 build 5/11 arcs** (parsed from the DONE markers); section 01 leads with a done/next/remaining arc strip (B1✓ B3✓ E✓ B2✓ R✓ → B4•next → CA B5 B6 B7 M); substitution-retirement 100% demoted + captioned (not full-spec completion); surface legend on the R-NNN board; post-Phase-8 "25" → "2 open of 25 (23 resolved)" naming R-CL-P3/Q4. **Verified by in-browser RENDER** (the #608 lesson) — caught + fixed a real `rf1`-scope ReferenceError that blanked the closure/board/register; Codex caught 2 hardcoded-text drift-traps → derived from parsed data. Tools assessed: spec_overlay = agent cite-grounding instrument (not a dashboard source); understand-anything = code-graph for impl. Mode-agnostic. → NEXT = **B4**. |
| PR #610 | 2026-06-16 | **ops(roadmap): reconcile 2 stale DEFERRED entries (R-CL-P1/P2) → RESOLVED — superseded by R-FS-1 arc R/E.** Follow-up audit (operator question) of the derived sections (status board / post-Phase-8 register / dependency graph — all derive from §5, auto-current on regen) found two §5 entries never flipped when R-FS-1 built their capability: **R-CL-P1** (routing — EMBEDDING + LLM_AS_ROUTER, built arc R #602/#604/#606) + **R-CL-P2** (engine-recovery, built arc E #562–#576 + tier→driver R-410-family/#503). Both → RESOLVED (record already-merged reality); residuals forward-tracked (P1 → routing-activation gate / B-L2-EMBEDDING-ACTIVATION; P2 → B6/B-TOOL-GATE/B-EFFECT-FENCE/B-ENGINE-OUTPUT-REPLAY). No cascade (Q1..C1 blocked by R-FS-1, not P1/P2). forward-activation open 4→2; 12/12 dashboard tests; mode-agnostic, X-AL-3 trivially clean. → NEXT = **B4**. |

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


_Showing the 10 most recent drift/reconciliation events. The full audit history (155 events) is archived at `.harness/roadmap_drift_log_archive.md`._

| Date | Source | Resolution |
|---|---|---|
| 2026-06-10 | **Claude release-candidate handoff authored locally at `a5215dde`; post-handoff refresh.** | Hash `e13d42d7874c` → `dbfe6623fc76` (state at `a5215dde`, open PRs unavailable/empty, fork count 47, batch-56). Added `.harness/release-candidate-deployment-readiness-runbook.md` and Claude/context pointers. Next selector is the HIL release-candidate deployment-readiness scope gate, then provider-free readiness before any live deployment smoke. |
| 2026-06-10 | **Overlay-check ignored-artifact fix merged locally at `d4b6b4e3`; post-merge refresh.** | Hash `c28613a1f0a3` → `e13d42d7874c` (state at `d4b6b4e3`, open PRs unavailable/empty, fork count 47, batch-56). `overlay-check` now ignores stale gitignored `tools/semantic_overlay/overlay.json` artifacts while preserving the hard gate for stale tracked snapshots. Next selector moves to an HIL release-candidate deployment-readiness scope discussion before opening new implementation. |
| 2026-06-10 | **Post-#447 terminating refresh — PR #447 BMad runtime config restore merged at `9cf968d2`; §12.2 owed follow-on.** | Hash `48f9537038cf` → `f9c6f1ebe73d` (state at `9cf968d2`, open PRs empty, fork count 47, batch-56). `_bmad/bmm/config.yaml` is restored on main; no roadmap item status changes beyond clearing the last in-flight PR. Next selector remains recurring R-600/R-IF lanes unless the operator selects a new non-recurring frontier. |
| 2026-06-09 | **PR #440 supersession / post-#464 open-PR refresh branch opened from `d24dcf57`.** | Hash `78617c29740a` → `48f9537038cf` (state at `d24dcf57`, open PRs #447 only, fork count 47, batch-56). #440 was closed as superseded: it was conflicting, predated the later R-CXA-2 implementation/back-flow sequence, and a current-main comparison showed it would remove later R-CXA-2 implementation, tests, batch records, and dashboard/overlay updates if merged. Next selector remains recurring R-600/R-IF lanes unless the operator selects a new non-recurring frontier. |
| 2026-06-09 | **Post-#463 terminating refresh — PR #463 R-IF-112 semantic overlay closeout merged at `925f021a`; §12.2 owed follow-on.** | Hash `ebb6d51193e6` → `78617c29740a` (state at `925f021a`, open PRs #440/#447, fork count 47, batch-56). R-IF-112 is now RESOLVED: `tools/semantic_overlay` derives the design-substrate contract keyspace, source cite layer, CXA seam endpoint graph, and substitution join; CI gates hard CXA/stale-artifact drift and reports advisory code/contract/substitution orphan classes. Next selector moves to this terminating refresh, then recurring R-600/R-IF lanes unless the operator selects a new non-recurring frontier. |
| 2026-06-09 | **Substantive R-IF-112 implementation closeout branch opened from `62f9a327`; §12.2 owed after merge.** | Hash `a0ddc2154026` → `ebb6d51193e6` (branch base `62f9a327`, open PRs #440/#447, fork count 47, batch-56). The existing semantic overlay linter is completed against the roadmap must-pass by adding design-substrate `C-*` keyspace scanning and advisory `contract_without_code` orphan reporting, alongside the existing code-without-cite, CXA missing-endpoint, and substitution-without-carrier classes. `R-IF-112` is moved to RESOLVED on this branch; a terminating refresh is owed after merge to pin the final merge commit/dashboard hash. |
| 2026-06-09 | **Post-#461 corrective fixed-point refresh — PR #461 post-#460 roadmap/status/dashboard refresh merged at `41297c2a`; §12.2 anchor re-pin.** | Hash `b958e3438c97` → `a0ddc2154026` (state at `41297c2a`, open PRs #440/#447, fork count 47, batch-56). PR #461 completed the post-#460 refresh but included a dashboard test update, so the default-branch guard could not classify the merge as the expected status/dashboard-only lag. This two-file refresh restores the fixed-point shape and keeps the selector on `R-IF-112` plus recurring R-600/R-IF lanes. |
| 2026-06-09 | **Post-#460 terminating refresh — PR #460 R-CXA-1 AS→IS edge-scope/sidecar closeout merged at `b9a9ec87`; §12.2 owed follow-on.** | Hash `39009757fd12` → `b958e3438c97` (state at `b9a9ec87`, open PRs #440/#447, fork count 47, batch-56). R-CXA-1 is now merged closed; the live substitution ledger is 54/54 RETIRED and 54/54 pipeline-advanced. Next selector moves off CXA build-close work to this terminating refresh, then the post-substitution governance/process frontier (`R-IF-112` if operator selects a new substantive arc; recurring R-600/R-IF lanes by cadence). |
| 2026-06-09 | **Substantive R-CXA-1 AS→IS edge-scope/sidecar branch opened from `22d7d53`; §12.2 owed after merge.** | Hash `ffe9044984c8` → `39009757fd12` (branch base `22d7d53`, open PRs #440/#447, fork count 47, batch-56). Filed `.harness/r-cxa-1-as-is-edge-audit-2026-06-09.md`, threaded the stage-5 procedural-tier resolver into the production `RuntimeAsIsWiring` secret-fetch callback, and moved H_T-CXA-1 from PARTIAL to SUBSTANTIVE_RETIRED. Live ledger is now 54/54 RETIRED on this branch; a terminating refresh is owed after merge to pin the final merge commit/dashboard hash. |
| 2026-06-09 | **Post-#458 terminating refresh — PR #458 R-CXA-1 scoped secret-fetch producer merged at `d236480`; §12.2 owed follow-on.** | Hash `53da62ac5c58` → `ffe9044984c8` (state at `d2364808`, open PRs #440/#447, fork count 47, batch-55). R-CXA-1 must_pass #1 is closed by the workflow-time secret-fetch producer; H_T-CXA-1 remains PARTIAL pending must_pass #2 / AS→IS edge-scope back-flow audit. |

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
