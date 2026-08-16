# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `d7eab3d7fd6a` |
| `last_refreshed` | 2026-08-16T00:00:00Z |
| `git_head` | `299c63b6` —  |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-57.md` |
| `open_fork_doc_count` | 119 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**Purpose.** Live pointer to the next Claude/Codex-executable frontier. Full round-by-round history (every prior round, verbatim, most-recent-first) lives in the archive below — grep it by PR/`B-`/`R-`-id/round, never read wholesale.

**Current next action (post-#1383).** **THREE GATES WERE RATIFIED BY THE OPERATOR 2026-08-16 (#1383) AND ARE NOW BUILDABLE — this is the largest change to the forward frontier in this register's recent history, because all three had been parked awaiting operator input, one of them across three separate loop runs.** **(1) `B-137` step (3) = `C1` (admit the root)** — the workflow root joins the always-sampled arm, so `ParentBased` hands every child an inherited `RECORD_AND_SAMPLE` and never consults a child's name, which is why the event-carried `B-133` family survives C1 and dies under A′. **The ratified cost is carried forward, NOT erased by the decision:** C1's cost is **data loss, not delay** (under production buffer bounds a trace containing any ordinary non-member child never resolves, drained only by `force_flush`), it **maximises** the `B-136` pressure this row's own step (5) predicts, and **the ordinary-child population frequency is STILL UNMEASURED**. The implementing arc **owes that measurement before shipping C1 to a production-bounded cell** and must carry the `B-136` interaction explicitly; if the steady state turns out to be buffer exhaustion that is a NEW finding to route back, not a licence to reopen a ratified choice. **(2) `B-124` = Reading A (materialize the retry-exit classification at the emission site)** — discharges the Class 2 fork at PR #1283. The fork recommended Reading D at `[MODERATE]`; the operator chose A, recorded as provenance not dissent (D argued only that the derivation could *wait*, and A is the repair that deferral was deferring) and marked **do not re-litigate**. Root cause it fixes: `validator.fail.permanence` is a **frozen Pydantic record field, not an OTel span attribute**, so neither the §10.2 tail-keep predicate nor the §9.2 always-sampled lookup can see it and **both halves are inert**; A puts work at **every emission path** and the arc should expect that breadth. **(3) `R-CTX-1 E7`** — the operator runs the reversible `mv` of the four unused design-skill dirs themselves; Claude does not re-attempt it (classifier-blocked 2026-08-11, never-retry-in-variant-forms). `B-148`'s **656-token miss is the PRE-removal measurement and MUST be re-measured** once the dirs are gone; `.claude/skills/graft/` is outside E7's four-name set. **ALSO NEWLY UN-GATED: `B-182`**, decoupled from `B-183` at #1380 — `cell_rate_limit` is declared a span rate at plan `:978` and nothing contradicts it, so the two caps plausibly carry different quantities by design and #1378's "one decision governs both" is withdrawn. Its close-out step (2) is agent-executable: disposition FACT 1 + FACT 2 together, **deriving placement from `C-OD-20` §20.1, not from the enforcement-layer enum** — §20.1's matrix was read this session and shows exactly one cell unambiguously in-process (`solo-developer × local-development`), with the two multi-tenant cells sidecar/per-tenant-collector and vendor-managed respectively, which is the evidence the "correct-by-design external enforcement vs gap" question needs. **STILL GATED: `B-183`** (`design_substrate_gated`, fork FILED at `.harness/class_1_fork_b183_tenant_limit_quantity_declared_two_ways.md`, no disposition recommended — the contradiction is internal to the OD spec lineage and no codified rule breaks the tie; cheapest first probe is reading `ADR-D6` §1.3 in the design-phase workspace, since it is a bracket placeholder here). **ONE SMALL DEBT OWED, impl-only:** `harness-od/tests/test_b183_tenant_limit_quantity_conflict.py`'s `test_the_plan_signature_declares_spans_per_second` reads `:978` — the **cell** limit — inside a module about the **tenant** limit; true and green but wrongly framed, and it could not ride the doc-only fork PR because fork docs match the codex guard's `DESIGN_RE`. **Other un-gated actionable candidates:** `B-44`, `B-94`, `B-104`, `B-172`; `B-167` step 3 remains open (needs revision-aware replay, validated count semantics, and the gate's own `.md`/`.yaml`/`.yml` carrier eligibility). **A LOCAL-ONLY BLOCKER, operator-owned:** `just codex-check` reds because `.codex/hooks/stop_gate.py` inspects the ROOT checkout, which carries the operator's Graft install plus the four untracked `.claude/skills/` dirs; pre-existing, verified by stashing, CI clean-checkout green throughout. **OPERATOR-FACING INCIDENT 2026-08-16:** a hard reset run to sync main **destroyed the operator's uncommitted Graft wiring** in four TRACKED files (`.claude/settings.json`, `.mcp.json`, `.gitignore`, `AGENTS.md`) — never staged, so absent from reflog and `git fsck --lost-found`, unrecoverable; re-running Graft's install restores it. Saved to memory as a standing discipline: advance a checkout with `git merge --ff-only`, whose **refusal** on local modifications is the feature. **STANDING CAUTION, ten consecutive arcs:** every failure was a claim asserted from a LABEL or a convenient surface instead of the thing that determines it — and this arc added the sharper variant that **an absorption can over-correct past the truth** (round 1's [P1] was right; the rule imported to replace the falsified claim was itself wrong). When a review overturns a claim, fix the claim; do not import a NEW rule without checking that rule holds.

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
| 1384 | 2026-08-16 | Bundled roadmap round for the #1383 ratifications: post-#1380 archived + pointer re-derived. This is the owed follow-on terminating refresh (§12.2.1); the next-action pointer is unchanged because it was authored for this very round and still holds. |
| 1383 | 2026-08-16 | Three operator gates RATIFIED and now buildable: B-137 step (3) = C1 (admit the root, with its unmeasured ordinary-child cost carried forward); B-124 = Reading A (materialize at the emission site, overriding the fork's MODERATE recommendation of D); R-CTX-1 E7 = operator runs the reversible mv themselves. B-182 also newly un-gated after #1380 decoupled it from B-183. |
| 1381 | 2026-08-16 | Bundled roadmap round: post-#1378 archived + live pointer refreshed to post-#1380. This is the owed follow-on terminating refresh (§12.2.1); the next-action pointer is unchanged because it was authored for this very round and still holds. |
| 1380 | 2026-08-16 | B-183 owed Class 1 fork FILED; the per-tenant cap's quantity is contradicted INSIDE the OD spec lineage (contract body says cardinality, two later deltas' change-note prose says spans/sec while disclaiming any change to C-OD-11); no codified rule breaks the tie, so no disposition is recommended. B-182 DECOUPLED — #1378's one-decision-governs-both claim withdrawn. |
| #1378 | 2026-08-16 | B-183 transited to design_substrate_gated with fork doc OWED; three-way quantity conflict located; gates B-182 |

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
