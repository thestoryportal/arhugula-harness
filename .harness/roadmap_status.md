# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `35586f56e497` |
| `last_refreshed` | 2026-06-01T01:00:00-06:00 |
| `git_head` | `5431ed1` (main) — `ops: ratify converter fork as Reading B (per-server default policy) (#169)` |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-50.md` |
| `open_fork_doc_count` | 42 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**`R-100-tool-step-converter` apply arc (status: ACTIVE; surface II; **design-phase posture**; advisor_required: conditional; cross_axis: no)** — apply the operator-ratified **Reading B** (per-server default tool-contract policy): runtime spec amendment (§14.9.3 stage-3a MCPClientHost factory + MCP-client config contract gain `default_minimum_tier` + `default_blast_radius`; factory builds a default-policy converter) + harness-runtime impl (MCPClientConfig +2 fields; `mcp_client_host_factory` builds the converter) + extend `test_r100_real_workflow_e2e.py` with a TOOL_STEP-via-`api.run` (echo MCP) closing R-100-mvp-real-workflow-execution AC #2.

**§4 derivation:** both R-100-mvp-real-workflow-execution forks are now resolved — cost fork RESOLVED-AS-INVALID (PR #168; was a test-observation bug, OD-5 retirement valid), converter fork RATIFIED-AS-READING-B (PR #169). R-100-mvp-real-workflow-execution is **3 of 4 ACs PASS** (AC #1 + #3 + #4 green via `test_r100_real_workflow_e2e.py`); only AC #2 remains, and its resolution (Reading B) is ratified-and-ready. The apply arc is the next executable §II step. **It is a `design-phase` posture arc** (touches `design-substrate/Spec_Harness_Runtime_v1.md`) — a mixed-posture bundled-absorption per `CLAUDE.md` §11.4 (spec amendment + impl + clearance marker). Per §11.6, confirm posture before opening. Alternatively `R-100-mvp-yaml-loader-shipped` stays gated behind its own OPEN YAML fork.

**(PR #169 `5431ed1` ratified converter fork → Reading B. PR #168 `a9ee48d` closed the cost fork as INVALID — cost-attribution DOES fire + write [WriteResult.APPENDED ×3]; the "no cost" was a test-observation-layer bug [cost entries land as `audit:` thread entries; the `cost:` action_id is in the hashed payload]; R-100 AC #4 test fixed → PASSES; OD-5 retirement VALID. PR #166 `97c8943` real 3-step Anthropic e2e [AC #1 + #3 PASS]. PR #164 `44c668d` R-100 operator-usable CLI scaffolding [RESOLVED]. PR #161 §III CI substrate complete.)**

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(this PR)* | `roadmap-refresh-post-169` | *(terminating refresh §12.2.1)* | mode-agnostic — `workspace_state_hash` recompute (`0deb499daab5` → `35586f56e497`) + anchor refresh covering #167→#169 (substantive R-100 fork-ratification cluster: #168 cost-fork-INVALID + #169 converter-Reading-B). ONLY `.harness/roadmap_status.md`; title `ops: roadmap status refresh post-PR-169` → next §12.1 audit sees expected lag-by-one |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #169 (`5431ed1`) | 2026-06-01 | **Converter fork RATIFIED-AS-READING-B** — operator AskUserQuestion ratified per-server default tool-contract policy (`MCPClientConfig` gains `{default_minimum_tier, default_blast_radius}`; factory builds a default-policy converter → TOOL_STEP dispatchable via `api.run`). Fork doc Status → RATIFIED; roadmap `R-100-tool-step-converter` → ACTIVE (apply arc owed: spec amendment + impl + AC #2-closing test). Records ratification only. |
| PR #168 (`a9ee48d`) | 2026-06-01 | **Cost fork RESOLVED-AS-INVALID** — fork-ratification grounding (live instrumentation) flipped it: cost-attribution DOES fire + write (`WriteResult.APPENDED` ×3). "No `cost:` entries" was a test-observation-layer bug — `RuntimeAuditLedgerWriter` writes the OD cost entry under the audit thread (`audit:<tenant>:<hash>` state-ledger entry; `cost:` action_id is in the hashed `payload`). `test_r100_real_workflow_e2e.py` AC #4 corrected (`startswith("cost:")`+xfail → ≥1 `audit:` entry per dispatch); **test now PASSES**. **OD-5 retirement (batch-32) re-validated VALID.** R-100-cost-attribution-firing → RESOLVED-AS-INVALID. |
| PR #167 (`2b678f0`) | 2026-06-01 | Terminating refresh post-PR-166 (dashboard-only; §12.2.1). Hash `0deb499daab5` (state at `97c8943`). |
| PR #166 (`97c8943`) | 2026-06-01 | **R-100-mvp-real-workflow-execution PARTIAL** — `test_r100_real_workflow_e2e.py`: real 3-step Anthropic `api.run` workflow. **AC #1 ✓** (status=completed) + **AC #3 ✓** (3 hash-chained `workflow:...:step:N` ledger entries) via 2 live operator-authorized runs. **AC #2** (tool dispatch via api.run) BLOCKED — no operator surface for `MCPClientHost.tool_contract_converter`; surface exercised at dispatcher level by U-RT-86; fork `class_1_fork_tool_step_no_operator_supplied_converter.md` → R-100-tool-step-converter. **AC #4** (cost-attribution) runtime `pytest.xfail` — real inference emits ZERO `cost:` entries despite wiring (llm_dispatch.py:517 + stage_5:147-149); fork `class_1_fork_llm_cost_attribution_not_firing_on_real_dispatch.md` → R-100-cost-attribution-firing + **OD-5 retirement-validity question** (grep-vs-e2e). Key-gated test (skips in CI). Zero src change. |
| PR #165 (`2862e7e`) | 2026-05-31 | Terminating refresh post-PR-164 (dashboard-only; §12.2.1). Hash `48e2fffa4434` (state at `44c668d`). |

---

## Outstanding fork docs (42 total)

Sample (highest-leverage open):

| Fork doc | Class | Status |
|---|---|---|
| `class_1_fork_tool_step_no_operator_supplied_converter.md` | Class 1 | ✅ RATIFIED-AS-READING-B (PR #169) — per-server default policy; apply arc owed (R-100-tool-step-converter) |
| `class_1_fork_llm_cost_attribution_not_firing_on_real_dispatch.md` | Class 1 | ❌ RESOLVED-AS-INVALID (PR #168) — test-observation bug, not a defect; cost-attribution fires + writes; OD-5 retirement VALID |
| `class_1_fork_harness_toml_default_discovery_unimplemented.md` | Class 1 | PROPOSING (PR #164) — spec §3.7 auto-discovery declared-but-unimplemented; tracked at R-100-mvp-config-discovery; does NOT block the MVP |
| `class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` | Class 1 | ✅ APPLIED-AS-READING-C (PR #107) — pending file-status refresh |
| `class_1_fork_yaml_loader_step_payload_scalar_coercion_gap.md` | Class 1 | OPEN — gates R-100-mvp-yaml-loader-shipped |
| `class_1_fork_topology_admissibility_check_load_time_vs_runtime_asymmetry.md` | Class 1 | OPEN — defer-to-runtime apply |
| `class_2_fork_audit_stub_timestamp_universal_fix_plus_per_tier_annotation.md` | Class 2 | ✅ APPLIED-AS-(D) |
| *(complete enumeration at `ls .harness/class_*_fork_*.md`)* | — | — |

**Audit-owed:** survey fork-doc files for Status-line refreshes against current production state. Cadence: every ~5 PRs or operator-discretion.

---

## Phase 7 retirement progress

| Bucket | Count | Notes |
|---|---|---|
| RETIRED | **46/54 (85.2%)** per batch-50 (**IS-axis 9/9 = 100% — FIRST axis fully RETIRED at the strict view**; CP-axis fully RETIRED; incl. AS-8d batch-31 + OD-5 batch-32 via mech-β) | See `harness-*/CLAUDE.md` §4.1 + `phase-7d-retirement-events-batch-*.md` for canonical enumeration. |
| RETIRE-READY | 2 active (**OD-3 + OD-6**) | OD-3 (R-007) + OD-6 (R-009) await real-deployment X-AL-2 second conjunct OR operator-AUQ Reading α. **Corrected at R-002 survey 2026-05-31: AS-8d + OD-5 are RETIRED (batches 31-32), not RETIRE-READY — prior table was stale.** |
| PARTIAL | **H_T-OD-4 (R-008) only** | **H_T-IS-2 RETIRED at batch-50 (PR #141) — transited out of PARTIAL** (R-003 + R-001-h-t-is-2-retired chain RESOLVED). OD-4 awaits §13.1 per-session toggle + §13.2 tokenization gate closures (R-008, BLOCKED). |
| STILL-BOUNDED-INDEFINITELY | 2 (AS-8e + AS-8f) | AS-8e files.* (R-005 DEFERRED) + AS-8f managed_agents.* (R-006 DEFERRED) — indefinite-defer per runtime spec v1.17 §14.C / v1.33; X-AL-2 bounded-residual carry. |
| RETIRED-AS-AUTHORING-ONLY | 4 | Sub-species 10 closures (OD-1, OD-7, IS-4, CP-23) per batches 37+38+39+41 |

**Decomposition COMPLETE (R-002 RESOLVED 2026-05-31):** all non-RETIRED rows mapped to R-NNN entries at roadmap §5.2 — IS-2 (R-003 + R-001-h-t-is-2-retired), OD-3 (R-007), OD-4 (R-008), OD-6 (R-009), AS-8e (R-005), AS-8f (R-006). R-001 (OD-5) + R-004 (AS-8d) reconciled stale BLOCKED → RESOLVED. Execution of each per-row entry gated as noted (most on real-deployment / operator-decision). The IS-2 chain (R-003 + R-001-h-t-is-2-retired) RESOLVED 2026-05-31; **Surface-I substitution work is fully drained** — next executable = `R-200-ci-pytest-pyright-ruff-matrix` (§III CI substrate) per §4 re-derivation (Surface II/III multipliers remain).

---

## Drift detection log

| Date | Source | Resolution |
|---|---|---|
| 2026-05-31 | Dashboard creation (v1 origin) | n/a |
| 2026-05-31 | First post-merge refresh — PR #112 merged at `7f3e6ce`; dashboard hash recomputed `9c31e4978c3d` → `5a077d17765f` | Refreshed via PR #113 per CLAUDE.md §12.2. |
| 2026-05-31 | Recursion-stop discipline gap surfaced — PR #113 merge left dashboard stale by 1 commit; §12.2 as written would recurse | Codified at PR #114 via §12.2.1 termination clause + §12.1 step 6 carve-out. |
| 2026-05-31 | First terminating refresh per §12.2.1 — PR #114 merged at `7da53e5`; this PR is the terminating event | Single-file dashboard-only refresh; does NOT trigger another refresh per §12.2.1. Hash `5a077d17765f` → `9bd06cb83b73`. |
| 2026-05-31 | Second terminating refresh — PR #116 bundled change merged at `63c4464`; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `9bd06cb83b73` → `12f34637fd3a`. |
| 2026-05-31 | Third terminating refresh — PR #118 NotebookLM skill setup merged at `65ed646`; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `12f34637fd3a` → `47c763cb4fb3`. |
| 2026-05-31 | Fourth terminating refresh — PR #120 NotebookLM MCP server supplement merged at `622790c`; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `47c763cb4fb3` → `6283a744645e`. |
| 2026-05-31 | Fifth terminating refresh — PR #122 SessionStart audit hook (enforcement layer) merged at `27bfeaf`; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `6283a744645e` → `82ce25e90fd5`. From this PR forward, audits auto-fire at every session start. |
| 2026-05-31 | Fresh-session reconciliation — local `main` found 13 commits stale (showed `#106`) vs `origin/main` `#123`; SessionStart hook not yet on local main so no auto-orient | Fast-forwarded local main; reset to `origin/main` `9f1bbf4` after parallel process pushed equivalent post-#122 refresh (#123); identical-tree sibling discarded. No divergence created. |
| 2026-05-31 | Sixth terminating refresh — PR #108 R-IF-108 audit merged at `54337c1`; `[ROADMAP DRIFT] action=§12.3` flagged by on-main hook; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `82ce25e90fd5` → `a9f8cc1bd85d`. R-IF-108 closed; next action recomputed to R-IF-109. |
| 2026-05-31 | Seventh terminating refresh — PR #109 R-IF-109 memory audit merged at `a81fe2d`; `[ROADMAP DRIFT] action=§12.3` flagged; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `a9f8cc1bd85d` → `25d4b36d4359`. R-IF-109 closed; next action recomputed to R-IF-110 (first design-phase posture entry in chain). |
| 2026-05-31 | Eighth terminating refresh — PR #110 R-IF-110 CXA v2.18 (design-phase) merged at `2f14604`; `[ROADMAP DRIFT] action=§12.3` flagged; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `25d4b36d4359` → `17fe5dac2209`. R-IF-110 closed; next action recomputed to R-IF-111 (last in-flight entry). Downstream `CLAUDE.md` §1.1 count cascade (107→105) flagged as owed hygiene arc per CXA v2.18 §0.9 FM-2 deferral. |
| 2026-05-31 | Ninth terminating refresh — PR #111 R-IF-111 OD plan v2.27 (design-phase) merged at `fdf120b`; `[ROADMAP DRIFT] action=§12.3` flagged; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `17fe5dac2209` → `a51d65ed22a2`. R-IF-111 closed — **in-flight chain #108→#109→#110→#111 fully cleared this session**. Next action recomputed to the owed hygiene cascade (CLAUDE.md §1.1 aggregate 107→105 + harness-od refresh), R-002 fallback after. |
| 2026-05-31 | Tenth terminating refresh — PR #128 R-IF-HYGIENE-CXA-COUNT-CASCADE merged at `3ba4fae`; `[ROADMAP DRIFT] action=§12.3` flagged; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `a51d65ed22a2` → `adb1e71359dd`. Hygiene cascade closed (canonical pointers now read 105). **All in-flight + deferred-hygiene work cleared this session.** Next action recomputed to **R-002** (substantive phase-7 substitution-retirement survey — recommend a fresh decision before opening). |
| 2026-05-31 | Eleventh terminating refresh — PR #130 R-002 Surface-I decomposition merged at `6f8dd66`; `[ROADMAP DRIFT] action=§12.3` flagged; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `adb1e71359dd` → `7f251d6c7cc5`. R-002 RESOLVED (7 non-RETIRED rows mapped to R-NNN; R-001/R-004 reconciled stale→RESOLVED). Next action recomputed to **R-003** (producer-site lifts, ~7 sites; substantive phase-7 cross-axis impl — recommend fresh decision + advisor before opening). **Survey-surfaced finding:** the roadmap §5.2 was authored 2026-05-31 with R-001/R-004 as RETIRE-READY-awaiting-deployment, but OD-5/AS-8d had been RETIRED via mech-β at batches 31-32 (2026-05-28) — a 3-day-stale authoring error, now corrected. |

| 2026-05-31 | Twelfth terminating refresh — PR #132 R-003 orientation-checkpoint merged at `7c79fb4`; `[ROADMAP DRIFT] action=§12.3` flagged; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `7f251d6c7cc5` → `754826ddff19`. Next action UNCHANGED at **R-003** but now **ACTIVE-ORIENTATION-COMPLETE** with a resume pointer to `.harness/R-003-checkpoint.md` — a fresh session (`/clear` → hook → `continue`) resumes at Cluster A without re-deriving. Demonstrates the **stop-short seamless-resume** discipline: a paused phase-7 entry persists its orientation as a checkpoint artifact + entry sub-status + dashboard pointer. |

| 2026-05-31 | Thirteenth terminating refresh — PR #134 roadmap §3 schema amendment merged at `f8572b3`; `[ROADMAP DRIFT] action=§12.3` flagged; §12.2 owed follow-on refresh | Single-file dashboard-only refresh per §12.2.1. Hash `754826ddff19` → `1c852278bfc9`. Next action UNCHANGED at **R-003 Cluster A**. §3 now declares the `resume:` field + `satisfied:<date>` advisor value + checkpoint-on-pause rule (status enum kept closed); R-003 entry reconciled to schema-legal `ACTIVE`. Closes the §3↔§5 drift the operator caught (3 off-schema constructs landed at #132 before the schema sanctioned them — schema-first discipline restored). |

| 2026-05-31 | **R-003 RESOLVED** — Cluster A (#136 `5e4a112`) + Cluster B (#137 `c339728`) merged; substantive roadmap PR (this) marks R-003 → RESOLVED + R-001-h-t-is-2-retired BLOCKED → ACTIVE | Bundled change (Project_Roadmap_v1.md + dashboard) → NOT a terminating refresh per §12.2.1; title drops the `ops: roadmap status refresh` prefix; **follow-on terminating refresh owed**. Hash `1c852278bfc9` → `03714383e971` (state at `c339728`, pre-this-PR-merge). Next action re-derived: **R-001-h-t-is-2-retired** (IS-2 producer cascade complete; file the PARTIAL → RETIRED retirement event). |

| 2026-05-31 | Fourteenth terminating refresh — PR #138 substantive R-003-close refresh merged at `a943caf`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `03714383e971` → `3111061f3b6b` (state at `a943caf`). Next action UNCHANGED at **R-001-h-t-is-2-retired**. This is the recursion-stopping fixed point for the R-003 close: dashboard now lags by exactly one commit (this refresh's own merge), recognized as `lag-expected` by the next §12.1 session-start audit. |

| 2026-05-31 | **Fresh-session reconciliation (Cluster A/B drift) + R-001 close** — a `/clear`→`continue` session's hook reported `next=R-003` though R-003 (Clusters A+B) was already shipped+merged (#136–#139); the primary checkout's local `main` was 4 commits behind `origin/main` and the hook never fetched (2nd instance of the line-92 class). | Fixed via `git merge --ff-only origin/main` (clean ff, no divergence); **hardened the hook** with a default-branch behind-origin guard (**PR #140** `e55e99b`). Then executed the true next-action: **R-001-h-t-is-2-retired RESOLVED** at **PR #141** `4a0aa1d` (H_T-IS-2 PARTIAL → RETIRED, batch-50; IS-axis 9/9 = 100%, FIRST axis fully RETIRED). This PR marks R-001 RESOLVED + reconciles stale-ACTIVE R-IF-108/109/110/111 → RESOLVED (confirmed merged) + logs this event. Substantive (roadmap + dashboard) → NOT a terminating refresh; **follow-on terminating refresh owed** per §12.2.1. Hash `1c852278bfc9` → `8780c87985f2` (state at `4a0aa1d`, pre-this-PR-merge). Next action re-derived: **R-200-ci-pytest-pyright-ruff-matrix** (§III rank 3 — §I drained, §III outranks §II). |

| 2026-05-31 | Fifteenth terminating refresh — PR #142 substantive R-001-close merged at `5ca46f5`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `8780c87985f2` → `ec4f50af797b` (state at `5ca46f5`). Next action UNCHANGED at **R-200-ci-pytest-pyright-ruff-matrix**. Recursion-stopping fixed point for the R-001 close: dashboard now lags by exactly one commit (this refresh's own merge), recognized as `lag-expected` by the next §12.1 session-start audit. |

| 2026-05-31 | **R-200-ci-coverage-gating RESOLVED** + sixteenth terminating refresh — substantive close PR #151 merged at `51f4131` (blocking `pytest` green; advisory od/pyright/ruff legs red-as-expected); this PR is the owed follow-on terminating refresh per §12.2.1 | Single-file dashboard-only refresh. Hash `b0d5c85c1136` → `e30b9dd81864` (state at `51f4131`). Next action UNCHANGED at **R-200-ci-od-cp-dependency-leak** (re-derived at PR #151; mode-agnostic §III drained → §III phase-7 entries next). Recursion-stopping fixed point: dashboard lags by exactly one commit, recognized as `lag-expected` by the next §12.1 audit. |

| 2026-05-31 | **R-200-ci-od-cp-dependency-leak RESOLVED** (PR #153, substantive) — od axis-isolation leg was advisory due to undeclared OD→CP + OD→IS consumer deps; advisor-gated resolution = option (a) declare the deps | Bundled (touches `Project_Roadmap_v1.md`) → NOT a terminating refresh; follow-on owed. `harness-od/pyproject.toml` declares `harness-cp` (canonical OD→CP §2.3.3; forcing consumer = `ReplayDisposition` read-only at `idempotency_join_dedup.py`) + `harness-is` (OD→IS §2.3.4; tests); both acyclic-safe. Broadened grep caught the `harness_is` 2nd dep a cp-only grep would miss. od leg green in isolation + in CI as blocking (887 passed) + `continue-on-error` carve-out dropped → full 6-leg matrix blocks. Corrected the "reverse-direction / relocate the seam" framing (OD→CP is canonical) at `.harness/class_3_drift_od_cp_undeclared_dependency.md`. Hash left stale `e30b9dd81864` (recompute owed at the post-merge terminating refresh). Next action re-derived: **R-200-ci-lint-typecheck-blocking** (§III phase-7, sole remaining ACTIVE §III; outranks §II MVP). |

| 2026-05-31 | Seventeenth terminating refresh — PR #153 substantive R-200-ci-od-cp-dependency-leak close merged at `4d0914d`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `e30b9dd81864` → `7fe422eb023c` (state at `4d0914d`). Next action UNCHANGED at **R-200-ci-lint-typecheck-blocking**. Recursion-stopping fixed point: dashboard lags by exactly one commit (this refresh's own merge), recognized as `lag-expected` by the next §12.1 session-start audit. |

| 2026-05-31 | Eighteenth terminating refresh — PR #155 ruff mechanical sweep (R-200-ci-lint-typecheck-blocking **progress**, not a close) merged at `f1f9a52`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `7fe422eb023c` → `e077fe676860` (state at `f1f9a52`). Next action UNCHANGED at **R-200-ci-lint-typecheck-blocking** (entry still ACTIVE — sweep dropped ruff 366 → 136 + cleaned format tree-wide, zero regression; manual ruff + pyright + flip-blocking remain). Recursion-stopping fixed point: dashboard lags by exactly one commit, recognized as `lag-expected` by the next §12.1 audit. |

| 2026-05-31 | Nineteenth terminating refresh — PR #157 F821 real-defect fixes (R-200-ci-lint-typecheck-blocking **progress**, not a close) merged at `ce211ee`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `e077fe676860` → `8070fa6466c7` (state at `ce211ee`). Next action UNCHANGED at **R-200-ci-lint-typecheck-blocking** (entry still ACTIVE — 3 F821 real defects fixed, ruff 136 → 133, F821 tree-wide now 0; 133 manual ruff residual + ~894 pyright + flip-blocking remain). Recursion-stopping fixed point: dashboard lags by exactly one commit, recognized as `lag-expected` by the next §12.1 audit. |

| 2026-05-31 | Twentieth terminating refresh — PR #159 lint-half close (R-200-ci-lint-typecheck-blocking **lint half closed**, entry stays ACTIVE) merged at `1b87f08`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `8070fa6466c7` → `72ce1ef25437` (state at `1b87f08`). Next action UNCHANGED at **R-200-ci-lint-typecheck-blocking** (entry still ACTIVE — `ruff check .` + `ruff format --check .` clean tree-wide; `lint` CI job flipped to blocking + verified green-as-blocking; ~894 pyright + `typecheck`-flip remain). Recursion-stopping fixed point: dashboard lags by exactly one commit, recognized as `lag-expected` by the next §12.1 audit. |

| 2026-05-31 | **R-200-ci-lint-typecheck-blocking RESOLVED** (PR #161 pyright-half close, substantive) — `uv run pyright` 846 → 0 tree-wide; `typecheck` job flipped `continue-on-error` → blocking (renamed `pyright (strict) — blocking`), verified green-as-blocking in CI with all 6 axis-isolation legs + ruff + pytest | Bundled (touches `Project_Roadmap_v1.md` §5 status ACTIVE → RESOLVED) → NOT a terminating refresh; follow-on owed. Approach: test dirs scoped via `[tool.pyright.executionEnvironments]`; src real-fixed incl. the named two-`Skill`-class bug (empty `types.Skill` stub re-exported as concrete `lifecycle.skills.Skill`; same `LedgerWriter`; `HarnessMCPServer` kept-as-stub — Pydantic-forward-ref regression caught + reverted mid-flight) + `AuditLedgerWriter.append` Protocol completion + mcp `streamablehttp_client`→`streamable_http_client` deprecation rename. 3543 passed / 0 regression. cp+od axis-isolation legs run locally (813 / 887 passed). Hash `72ce1ef25437` → `c0c447454969` (state at `d904055`, pre-this-PR-merge). **§III CI substrate gate COMPLETE** (both lint + typecheck blocking). Next action re-derived: **R-100-mvp-operator-usable-cli-shipped** (§II MVP rank 4 — §III drained, §I drained, §II is next priority tier with a dependency-met ACTIVE entry). |

| 2026-05-31 | Twenty-first terminating refresh — PR #162 bundled R-200-close merged at `149c9a0`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `c0c447454969` → `038c75a5245e` (state at `149c9a0`). Next action UNCHANGED at **R-100-mvp-operator-usable-cli-shipped** (§II MVP — §III CI substrate gate complete). Recursion-stopping fixed point: dashboard lags by exactly one commit (this refresh's own merge), recognized as `lag-expected` by the next §12.1 session-start audit. |

| 2026-05-31 | **Fresh-session audit + R-100 close** — `/clear`→`continue` session: §12.1 audit clean (local main 3 behind origin; ff'd to `fcfa568` #163, a terminating refresh whose dashboard hash = `compute(149c9a0)` = expected lag-by-one fixed point per §12.1 step 6; no new refresh PR). Derived next-action R-100-mvp-operator-usable-cli-shipped; use-the-product probe surfaced 4 operator-blocking gaps → shipped scaffolding + fixes + operator-authorized live green at **PR #164** `44c668d`. | Substantive R-100 close (PR #164 touches Project_Roadmap_v1.md: R-100 ACTIVE → RESOLVED + NEW R-100-mvp-config-discovery) → NOT a terminating refresh; **follow-on terminating refresh owed**. Hash `038c75a5245e` → recomputed below. Next action re-derived: **R-100-mvp-real-workflow-execution** (R-100 RESOLVED unblocks it; was BLOCKED → ACTIVE). |

| 2026-05-31 | Twenty-second terminating refresh — PR #164 bundled R-100-close merged at `44c668d`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `038c75a5245e` → `48e2fffa4434` (state at `44c668d`; open_fork_doc_count 39 → 40 for the NEW discovery fork). Next action UNCHANGED at **R-100-mvp-real-workflow-execution**. Recursion-stopping fixed point: dashboard lags by exactly one commit (this refresh's own merge), recognized as `lag-expected` by the next §12.1 session-start audit. |

| 2026-06-01 | **R-100-mvp-real-workflow-execution PARTIAL + 2 forks** — same `/clear`→`continue` session: authored the real multi-step e2e (PR #166 `97c8943`). AC #1 + #3 PASS via 2 live operator-authorized Anthropic runs; AC #2 + #4 surfaced as Class 1 forks (converter gap + cost-not-firing w/ OD-5 retirement-validity question). | Substantive (PR #166 touches Project_Roadmap_v1.md: entry → ACTIVE/partial + NEW R-100-tool-step-converter + R-100-cost-attribution-firing) → NOT a terminating refresh; **follow-on terminating refresh owed**. Hash `48e2fffa4434` → recomputed below. Next action re-derived: **operator ratification of the 2 PROPOSING forks** (all §II forward entries now fork-gated; §VII process-discipline is the executable fallback). |

| 2026-06-01 | Twenty-third terminating refresh — PR #166 substantive R-100-real-workflow PR merged at `97c8943`; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash `48e2fffa4434` → `0deb499daab5` (state at `97c8943`; open_fork_doc_count 40 → 42 for the 2 NEW R-100 forks). Next action = **operator fork-ratification** (see Next action section). Recursion-stopping fixed point: dashboard lags by exactly one commit (this refresh's own merge), recognized as `lag-expected` by the next §12.1 session-start audit. |

| 2026-06-01 | **Fork ratification cluster** — same `/clear`→`continue` session: grounded + ratified both R-100-mvp-real-workflow-execution forks. Cost fork → RESOLVED-AS-INVALID (PR #168 `a9ee48d`; live instrumentation flipped it — test-observation bug, cost fires+writes, OD-5 valid; AC #4 test fixed → PASSES). Converter fork → RATIFIED-AS-READING-B (PR #169 `5431ed1`; operator AskUserQuestion). | Two substantive PRs (#168 touches roadmap+test; #169 touches roadmap+fork doc) → NOT terminating refreshes; this is the **owed follow-on terminating refresh** covering #167→#169. Hash `0deb499daab5` → `35586f56e497` (state at `5431ed1`). R-100-mvp-real-workflow-execution now 3/4 ACs PASS; next action re-derived: **apply Reading B at R-100-tool-step-converter** (design-phase posture spec+impl arc; confirm posture per §11.6). |

| 2026-06-01 | Twenty-fourth terminating refresh — fork-ratification cluster #168 + #169 merged; §12.2 owed follow-on | Single-file dashboard-only refresh per §12.2.1. Hash recompute `0deb499daab5` → `35586f56e497` (state at `5431ed1`; fork count 42 unchanged — #168/#169 flipped fork Status, added no fork files). Next action = **R-100-tool-step-converter apply arc (Reading B)**. Recursion-stopping fixed point: dashboard lags by exactly one commit (this refresh's own merge), recognized as `lag-expected` by the next §12.1 session-start audit. |

**Audit protocol exercised across 24 terminating-refresh closures + 2 fresh-session reconciliations + 8 substantive closes + 1 substantive partial (R-100-mvp-real-workflow-execution).** Discipline + enforcement layers operational; hook hardened against the local-behind-origin drift class at PR #140. **Both R-100-mvp-real-workflow-execution forks ratified 2026-06-01: cost fork RESOLVED-AS-INVALID (PR #168 — test-observation bug; cost-attribution fires + writes; OD-5 retirement VALID), converter fork RATIFIED-AS-READING-B (PR #169 — per-server default policy).** R-100-mvp-real-workflow-execution now **3 of 4 ACs PASS** (AC #1 + #3 + #4); AC #2 resolution ratified-and-ready. **Deterministic next-action = R-100-tool-step-converter apply arc (Reading B)** — runtime spec amendment + harness-runtime impl + a TOOL_STEP-via-api.run test closing AC #2 (then all 4 R-100 ACs PASS). It is a `design-phase` posture arc (touches design-substrate); confirm posture per §11.6 before opening.**

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
