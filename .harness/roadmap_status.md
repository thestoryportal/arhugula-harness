# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `33e90cca7cfa` |
| `last_refreshed` | 2026-06-17T03:32:41+00:00 |
| `git_head` | `a7bbf65d` — #610 reconciled 2 stale DEFERRED entries (R-CL-P1 routing, R-CL-P2 engine-recovery) → RESOLVED: superseded by R-FS-1 arc R (#602/#604/#606) + arc E (#562–#576); residuals forward-tracked in "Remaining forward work". Follows the #608 deep-hygiene reorg (the derived board/depgraph/register now reflect that those capabilities are built). Lags HEAD by one commit (this terminating-refresh fixed point, §12.2.1). Full detail: `git show a7bbf65d` + Recently completed. |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-57.md` |
| `open_fork_doc_count` | 62 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**Purpose.** Section 02 names the next Claude/Codex-executable frontier. Completion history lives in `Recently completed`; the full remaining itemization lives in `Remaining forward work` (next section).

**Frontier.** The single ACTIVE build umbrella is **R-FS-1** (full-spec build beyond MVP; operator directive 2026-06-12). Its capabilities are FROZEN ordered child arcs; §4 derives one next-action from the umbrella so the children stay folded (see `Project_Roadmap_v1.md` §5.0).

**Next = R-FS-1 → B4** — per-role / per-step dispatch indexing (thread `AgentRole` + per-step override through dispatch so the per-role model + prompt actually take effect). Frozen order: B1✅ B3✅ E✅ B2✅ R✅ → **B4** → CA → B5 → B6 → B7 → M. Re-ground at arc-open per `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` (LEADS, presence-not-correctness).

**Recurring lanes** run on cadence alongside: `R-600-*` (pattern bake-in, codex out-of-family review), `R-IF-roadmap-refresh`.

**Do not re-open as next action.** Closed/parked: `R-411/412/420/421/430`, `R-500`, `R-810/820/830`, `R-008`/OD-4, `R-CXA-1/2/4`, `R-100-*`, `R-300-*` (both routing-activation #213 and second-provider #281/#283 RESOLVED), `R-901` (research frontier closed). `R-CL-Q1→C1` (quality track) BLOCKED behind R-FS-1 (full-spec runs once, on the complete harness).

---

## Remaining forward work

**The full-spec build (R-FS-1).** All remaining forward build work is child arcs of the single ACTIVE umbrella **R-FS-1** (operator FULL-SPEC directive 2026-06-12 — nothing deferred; every capability built beyond MVP). Authoritative per-arc detail (re-ground at arc-open — these are LEADS, presence-not-correctness): `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md`. The spine ledger (every surfaced boundary + standalone arc): `.harness/beyond-mvp-capability-boundary-ledger.md`.

### R-FS-1 child arcs — FROZEN order (B1→B3→E→B2→R→B4→CA→B5→B6→B7→M)

DONE: **B1✅ B3✅ E✅ B2✅ R✅** (R incl. L3 LLM_AS_ROUTER #604 + L2 EMBEDDING #606). Remaining, in build order:

| # | id | Item | Track | Gate / shape |
|---|---|---|---|---|
| 1 | R-FS-1·B4 | Per-role / per-step dispatch indexing | build | NEXT — thread `AgentRole` + per-step override through dispatch so per-role model+prompt take effect (partially-built; mixed fork/impl; thin-to-medium) |
| 2 | R-FS-1·CA | Cost aggregate — `RunResult.cost_attribution` rollup | build | Thin-to-medium; small pre-auth C-RT-09 spec fork (Slice 0) + owns the R router-call cost-bucket sub-item |
| 3 | R-FS-1·B5 | Memory per-deployment-surface backend selection (U-RT-80 factory) | build | Thin impl-discretion; surface→backend dispatch (backends already live via R-830; built-but-vacuous) |
| 4 | R-FS-1·B6 | Per-tool sandbox-tier resolution + STDIO transport-floor | build | Medium fork+impl; per-tool resolver runtime-spec amendment (fork-owed) |
| 5 | R-FS-1·B7 | OD composite sampler §9.2 conditional-row over-sampling | build | Small impl-discretion; predicate refinement (over-sampling is safe today; built-but-vacuous) |
| 6 | R-FS-1·M | managed_agents C-RT-28 contract + production wiring | build | Thin contract+wiring; capability live-proven (R-820), contract unauthored + zero prod callers |

### Standalone forward arcs — design-fork-first, unsequenced (surfaced during impl; not in the frozen order)

Each is a committed BUILD (FULL-SPEC directive), sequenced as a follow-on R-FS-1 child arc when its turn comes. Full disposition in the spine ledger.

| id | Owner-axis | Shape |
|---|---|---|
| B-INTERSTEP | runtime | Inter-step DATA-flow channel (driver threads control-flow only today); composes B1+B4 |
| B-FANOUT-PAUSE | CP+runtime | Resumable fan-out `pause` cascade (honest-FAILED interim landed; resume-re-entry + output-persistence owed) |
| B-ENGINE-OUTPUT-REPLAY | CP+runtime/IS | Output-carrying event-history substrate + cached-output replay (event-sourced/WAL replay = skip-prefix today) |
| B-EFFECT-FENCE | runtime+AS | At-most-once EXECUTION of non-idempotent step side-effects (sink-fencing; durable engines are at-most-once-claim only) |
| B-EDIT-CARRIER | runtime+CP | HITL `EDIT` carrier-healing (str↔Mapping); EDIT raises until built |
| B-LAYER-BUDGET-OVERRIDE | CP | Per-layer wall-clock budget enforcement honoring per-workload/persona overrides + dispatcher budget-threading + realistic L3 budget |
| B-TOOL-GATE | runtime | Tool-step HITL gate site = the real per-server MCP-trust producer (gate sites are host-less today → AUTO) |
| B-L2-EMBEDDING-ACTIVATION | runtime+CP | L2 EMBEDDING + L3 router production activation: the routing-activation gate (below) + factory-wire `embedding_classifier=`/`router=` + promote fastembed required |

### Routing-activation gate — visibility-only, currently UNOWNED

The shared production-activation gate for **both** L2 EMBEDDING and L3 LLM_AS_ROUTER: make the DECLARATIVE layer **conditional** so `route()` reaches the EMBEDDING / LLM_AS_ROUTER layers (today `_declarative_echo` always resolves → `route()` short-circuits before them; both routing layers are BUILT + PROVEN but production-inert). **Both R-300 items are RESOLVED without doing this work** — routing-activation (#213) kept DECLARATIVE behavior-preserving by design; second-provider (#281/#283) added credentials + cross-family fallback only. So this gate has **no open owner**; it is captured (with a now-stale `Owner = R-300-second-provider` pointer) at `B-L2-EMBEDDING-ACTIVATION` in the spine ledger. Visibility-only — NOT a derivation-eligible R-NNN (minting one would split §4's single-next-action invariant); it is a real forward unit that needs an owner once routing-among-candidates becomes meaningful (a second production provider configured).

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(none)* | — | — | No open PRs at refresh time. |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #610 | 2026-06-16 | **ops(roadmap): reconcile 2 stale DEFERRED entries (R-CL-P1/P2) → RESOLVED — superseded by R-FS-1 arc R/E.** Follow-up audit (operator question) of the derived sections (status board / post-Phase-8 register / dependency graph — all derive from §5, auto-current on regen) found two §5 entries never flipped when R-FS-1 built their capability: **R-CL-P1** (routing — EMBEDDING + LLM_AS_ROUTER, built arc R #602/#604/#606) + **R-CL-P2** (engine-recovery, built arc E #562–#576 + tier→driver R-410-family/#503). Both → RESOLVED (record already-merged reality); residuals forward-tracked (P1 → routing-activation gate / B-L2-EMBEDDING-ACTIVATION; P2 → B6/B-TOOL-GATE/B-EFFECT-FENCE/B-ENGINE-OUTPUT-REPLAY). No cascade (Q1..C1 blocked by R-FS-1, not P1/P2). forward-activation open 4→2; 12/12 dashboard tests; mode-agnostic, X-AL-3 trivially clean. → NEXT = **B4**. |
| PR #608 | 2026-06-16 | **ops(roadmap): deep-hygiene — itemize all R-FS-1 remaining arcs; derive dashboard remaining-work from markdown.** Found the "Remaining to complete" panel rendering EMPTY (stale hardcoded `REMAINING_ORDERED` all RESOLVED-filtered) while build-closure read "100% / is the harness built?" — the full-spec program invisible. NEW `## Remaining forward work` = single authoritative itemization: R-FS-1 FROZEN child arcs (B1✅B3✅E✅B2✅R✅ → **B4** → CA → B5 → B6 → B7 → M) + 8 standalone design-fork-first B-* arcs + the UNOWNED routing-activation gate. `generate.py`: `parse_remaining_forward()` (one home) + `assert_remaining_nonempty()` fail-loud guard; relabeled closure panel → "Substitution-retirement closure" + a not-full-spec caveat (54/54 R-600 metric untouched). roadmap_status.md 389→167 lines (drift log archived); §5.0 next_pointer → B4; ledger 4 stale R-300-owner pointers → UNOWNED. 12/12 dashboard tests (5 new + 1 stale-red fixed); 38 affected green; advisor-designed + Codex ([P2] snapshot regen → done). Mode-agnostic; X-AL-3 trivially clean. → NEXT = **B4**. |
| PR #606 | 2026-06-16 | **R-FS-1 — arc R / L2: EMBEDDING Layer-2 — Option B in-process fastembed classifier.** CP-pure injected-`EmbeddingFn` k-NN classifier + corpus carriers (`embedding_routing.py`) + light `fastembed` realization + default corpus (`embedding_resolution.py`) + `RuntimeLLMDispatcher.embedding_classifier` injection seam. **L2-sync = pure Phase-7 impl, no spec amendment** (realizes the cleared §2.4 deferral). Optional `[embedding]` extra (`onnxruntime<1.24` — x86-mac wheel cap). Production-inert until R-300 (B-L2-EMBEDDING-ACTIVATION). CP 1028 + runtime 1776 + real-fastembed live e2e 2 green; pyright strict 0 base-lane; advisor + Codex ([P1] dynamic-import fix) converged. → NEXT = B4. |
| PR #604 | 2026-06-16 | **R-FS-1 — arc R / R-impl-2: LLM_AS_ROUTER L3 vendor gate — real Ollama router + gated live e2e.** The vendor-gate realization over the R-impl-1 units (impl-discretion per CP spec §2.4/§2.5.5; NO new unit / NO spec amendment). `router_resolution.py` — a real `RouterResolutionFn` (`make_ollama_router`: router prompt + direct `adapter.client.chat` [`format=json` + capped tokens + temp 0] + its OWN child `llm.inference` span [§2.5.4] + candidate-set-constrained robust parser; terminal leaf) + 15 unit tests + a `@pytest.mark.e2e` model-gated live e2e (real Ollama resolves L3 through `infer()`). Free-local, **NO paid call**. BUILDS+PROVES the router; does NOT route production traffic (prod `router=None`; L3 activation needs R-300-second-provider + realistic budget + dispatcher budget-threading — captured in B-LAYER-BUDGET-OVERRIDE). The e2e calls `infer()` directly (60 s budget) because the dispatcher hardcodes the 200 ms L3 default, unmeetable by a real local router (`[[test-bypass-as-runtime-truth-pattern]]`, composition gap registered). Decorrelated: advisor pre-done (composition gap → first-class register) + Codex **converged after 4 [P2] fixes** (out-of-set rejection, model-gate, prefix-collision, trailing-punctuation) + pyright 0 + 15 unit + live e2e pass (full `just check` 4263; 3 reds = macOS/Docker/gVisor env artifacts). Additive-only, X-AL-3-clean. **Next = R-L2-gate → R-spec-2 (Layer 2 EMBEDDING).** |
| PR #602 | 2026-06-16 | **R-FS-1 — arc R / R-impl-1: LLM_AS_ROUTER L3 (U-CP-99/100 + U-RT-132/133; mock router, NO paid call).** All 4 R-plan-1 units co-landed (the `ProviderDispatchFn` Protocol-ization TYPE-RIPPLE co-land): `RouterResolution` + `RouterResolutionFn` + Protocol-ized dispatch seam (U-CP-99); the `infer()` L3 router branch + `asyncio.wait_for` timeout wrap + 4 no-regress paths (U-CP-100); rationale-consume span emitter (U-RT-132); router-injection binding, prod `router=None` + a test-only `layer_decisions` seam for the spec-§2.5.5 e2e (U-RT-133). Decorrelated: advisor (forward-caveat added re the e2e `[0]` span ordinal) + Codex 1×[P2] **reasoned-rejected with spec evidence** (§2.5.3 bounds L3 by the FLAT 200 ms `time_budget_ms`; the per-workload/persona `effective_budget()` override gap is built-but-vacuous + structurally cannot serve the L3 site → honoring it = X-AL-3; registered as forward arc **B-LAYER-BUDGET-OVERRIDE**, not dropped); pyright 0-err + 4250 passed (2 macOS AF_UNIX + R-410 Docker env reds outside the changed set) + 14/14 CI. Phase-7 impl vs cleared CP spec v1.36 §2.5; X-AL-3-clean. **Next = R-impl-2 (vendor gate — surface the paid call).** |

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
