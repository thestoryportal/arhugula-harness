# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `adb1e71359dd` |
| `last_refreshed` | 2026-05-31T15:00:54-06:00 |
| `git_head` | `3ba4fae` (main) — `hygiene: CXA v2.18 count cascade to canonical pointers (107→105) (#128)` |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-49.md` |
| `open_fork_doc_count` | 39 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**`R-002`** — remaining substitution-retirements survey (surface I; **phase-7 posture**; skill `phase-7-substitution-retirement`; verification grep). First execution decomposes the §I atomic-unit set: survey the non-RETIRED rows across `harness-*/CLAUDE.md` §4.1 (H_T-IS-2 PARTIAL awaiting ~7 producer-site lifts; AS-8d + OD-5 RETIRE-READY awaiting operator deployment substrate; STILL-BOUNDED bucket) and classify each as executable-now vs MVP-blocked vs operator-decision, generating per-row R-NNN entries. Per §4 derivation rule: with the in-flight chain (R-IF-108→111) + the hygiene cascade all CLOSED this session, R-002 is the lowest-R-NNN ACTIVE entry with all `depends_on` RESOLVED. **Note:** R-002 is a substantive phase-7 survey (larger surface than the doc-hygiene chain just cleared); recommend a fresh decision before opening it.

**(R-IF-HYGIENE-CXA-COUNT-CASCADE CLOSED at PR #128 merge `3ba4fae` — CXA v2.18 count cascade landed; canonical pointers now read 105.)**

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(none — in-flight chain #108→#109→#110→#111 + hygiene cascade #128 all cleared 2026-05-31)* | — | — | — |
| *(this PR)* | `worktree-roadmap-refresh-post-pr-128` | *(self, post-merge refresh)* | mode-agnostic |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #128 (`3ba4fae`) | 2026-05-31 | R-IF-HYGIENE-CXA-COUNT-CASCADE — CXA v2.18 count cascade to canonical pointers (aggregate 107→105; phase-2-runtime 22→20; OD→IS 6→4; OD outbound 27→26); mode-agnostic; §108/§109 sibling-completeness applied |
| PR #111 (`fdf120b`) | 2026-05-31 | R-IF-111 — OD plan v2.27 NEW §4.6.OD-INTERNAL carve-out; halt-doc Item 12 closed; sibling to #110; design-phase posture, clearance marker present (operator-ratified) |
| PR #110 (`2f14604`) | 2026-05-31 | R-IF-110 — CXA v2.18; CXA-OD-IS-EDGE-DRIFT (Item 11) closed; §2.3.4 6→4, aggregate 107→105; design-phase posture, clearance marker present (operator-ratified) |
| PR #109 (`a81fe2d`) | 2026-05-31 | R-IF-109 — workspace memory audit round-3 (50 entries / 3 findings); +apply-pass correction (AS-8e is STILL-BOUNDED-INDEFINITELY not PARTIAL) caught at verification |
| PR #108 (`54337c1`) | 2026-05-31 | R-IF-108 — workflow v1.12 §7.4.7.3.C audit at per-axis CLAUDE.md §4.1; +sibling cumulative-counts completeness fix (harness-is §4.1:151) caught at fresh-session verification |

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
| RETIRED | 33+ (per batch-49) | See `harness-*/CLAUDE.md` §4.1 + `phase-7d-retirement-events-batch-*.md` for canonical enumeration |
| RETIRE-READY | 2 active (AS-8d + OD-5) | Both await operator deployment substrate per R-001 + R-004 |
| PARTIAL | H_T-IS-2 + others | H_T-IS-2 awaits 7 producer-site lifts remaining post-PR #107 (6-of-13 LANDED at PR #107 `89915af`) per R-003 |
| STILL-BOUNDED | several | Decomposition-owed at R-002 |
| RETIRED-AS-AUTHORING-ONLY | 4 | Sub-species 10 closures (OD-1, OD-7, IS-4, CP-23) per batches 37+38+39+41 |

**Decomposition trigger:** R-002 execution generates per-row R-NNN entries for all non-RETIRED rows. Run when MVP-usable (§II) is enough closed that exact per-row classification (executable-now vs MVP-blocked vs operator-decision) is reliable.

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

**Audit protocol exercised across 10 closure events + 1 fresh-session reconciliation.** Discipline + enforcement layers both operational. **In-flight chain + hygiene cascade fully cleared 2026-05-31; deterministic next-action = R-002 (phase-7 substitution-retirement survey).**

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
