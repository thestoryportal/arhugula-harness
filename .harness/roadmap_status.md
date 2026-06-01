# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `7abd92ea0952` |
| `last_refreshed` | 2026-05-31T18:30:00-06:00 |
| `git_head` | `3223ab9` (main) — `roadmap(R-200): RESOLVED at PR #144 + flip §III dependents ACTIVE + add lint/typecheck-blocking follow-up (#145)` |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-50.md` |
| `open_fork_doc_count` | 39 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**`R-200-ci-axis-matrix`** (status: **ACTIVE**; surface III CI substrate; mode-agnostic; cross_axis: no) — per-axis test-isolation matrix in CI (each axis runs without sibling-package import leak; matrix < 10 min), now unblocked by **R-200-ci-pytest-pyright-ruff-matrix RESOLVED at PR #144 `f06c30a`** (`.github/workflows/ci.yml`: `test` blocking+green; `lint`+`typecheck` advisory because the tree isn't clean — see R-200-ci-lint-typecheck-blocking). Also newly ACTIVE in §III: `R-200-ci-coverage-gating` + `R-200-ci-lint-typecheck-blocking`. Original R-200-ci-pytest scope below is retained for history. scope = `.github/workflows/ci.yml` + `pyproject.toml`; verification (integration) = CI runs on every PR; all 5 axis packages tested; pyright strict + ruff pass. close_shape = PR-merge; `advisor_required: no`. **§4 derivation:** with R-001-h-t-is-2-retired RESOLVED, §I has no ACTIVE candidate; rank-1 mode-agnostic R-IF entries (108–111) are RESOLVED (reconciled this PR) and R-IF-roadmap-refresh is the perennial refresh mechanism (satisfied by this refresh); so the top candidate is **§III CI substrate (rank 3)** — which outranks §II MVP-operator-usable (rank 4: `R-100-mvp-operator-usable-cli-shipped`, also ACTIVE). The pipeline is **not** drained — Surface II/III multipliers remain executable.

**(R-001-h-t-is-2-retired RESOLVED at PR #141 merge `4a0aa1d` 2026-05-31 — H_T-IS-2 PARTIAL → RETIRED, batch-50; IS-axis 9/9 RETIRED = 100%, FIRST axis fully RETIRED at the strict view. R-003 RESOLVED at #136+#137+#138. Hook hardened against the local-behind-origin drift at PR #140 `e55e99b`.)**

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(none — #144 merged `f06c30a` 2026-05-31; #136–#143 all merged)* | — | — | — |
| *(this PR)* | `roadmap-r200-close` | *(self — substantive R-200 close: marks R-200-ci-pytest RESOLVED + flips §III dependents ACTIVE + adds R-200-ci-lint-typecheck-blocking + dashboard refresh. NOT a terminating refresh → follow-on terminating refresh owed per §12.2.1)* | mode-agnostic |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #144 (`f06c30a`) | 2026-05-31 | **R-200-ci-pytest-pyright-ruff-matrix RESOLVED** — first substantive CI job. `.github/workflows/ci.yml`: `test` (`pytest -m "not e2e"`) BLOCKING + green (3543 passed); `lint`+`typecheck` ADVISORY (tree not ruff/pyright-clean — 366 ruff / 894 pyright, incl. a real dup-`Skill` bug at types.py:1683). §III dependents flipped ACTIVE; follow-up `R-200-ci-lint-typecheck-blocking` added. |
| PR #142 (`5ca46f5`) | 2026-05-31 | **R-001-h-t-is-2-retired RESOLVED** (substantive close) — marks R-001 RESOLVED + reconciles stale-ACTIVE R-IF-108/109/110/111 → RESOLVED + dashboard refresh (next-action re-derived to R-200-ci §III); logs the Cluster A/B drift + #140 hardening |
| PR #141 (`4a0aa1d`) | 2026-05-31 | **R-001-h-t-is-2-retired RESOLVED** — batch-50: H_T-IS-2 PARTIAL → RETIRED (substantive substitution-retirement). All 13 producer sites handled; X-AL-2 both conjuncts MET. IS-axis 9/9 RETIRED = 100% (FIRST axis fully RETIRED at strict view). harness-is/CLAUDE.md §4.1 + ledger v2 §11.4h |
| PR #140 (`e55e99b`) | 2026-05-31 | **Hook hardening** — `session-start.sh` behind-origin guard (fixes the Cluster A/B stale-next-action drift: local main 4 behind origin → hook reported stale `next=R-003`). Default-branch-gated, timeout-guarded fetch; can't hang/fail offline |
| PR #138 (`a943caf`) | 2026-05-31 | **R-003 RESOLVED** substantive roadmap refresh — R-003 → RESOLVED + R-001-h-t-is-2-retired BLOCKED → ACTIVE |
| PR #137 (`c339728`) | 2026-05-31 | **R-003 Cluster B** — CP-axis producer-site lifts: `construct_sibling_ledger_entry` + `workflow_driver._append_step_ledger_entry`; + 3 None-canonical doc-comments. 2281 pass |

---

## Outstanding fork docs (39 total)

Sample (highest-leverage open):

| Fork doc | Class | Status |
|---|---|---|
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

**Audit protocol exercised across 15 terminating-refresh closures + 2 fresh-session reconciliations + 2 substantive closes (R-003, R-001-h-t-is-2-retired).** Discipline + enforcement layers operational; hook hardened against the local-behind-origin drift class at PR #140. **R-001-h-t-is-2-retired RESOLVED 2026-05-31 (PR #141 + #142 substantive close + this terminating refresh); H_T-IS-2 RETIRED, IS-axis 9/9 = 100%; deterministic next-action = R-200-ci-pytest-pyright-ruff-matrix (§III CI substrate).**

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
