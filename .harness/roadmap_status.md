# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `7f251d6c7cc5` |
| `last_refreshed` | 2026-05-31T15:12:27-06:00 |
| `git_head` | `6f8dd66` (main) — `roadmap(R-002): Surface-I decomposition — 5 new per-row entries + reconcile stale R-001/R-004 (#130)` |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-49.md` |
| `open_fork_doc_count` | 39 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**`R-003`** — producer-site lifts at ~7 sites per IS spec v1.3 §C-IS-05 §5.2 `procedural_tier_snapshot` consumers (surface I; **phase-7 posture**; skill `phase-7-implementation` + `phase-7-cross-axis-composition`; **cross_axis: yes**; advisor_required: yes; verification: integration). The 7 remaining producer sites (post-PR #107): `harness-cp/.../sibling_ledger_entry_composition.py:144` + `workflow_driver.py:1360`; `harness-runtime/.../lifecycle/{sub_agent_dispatch.py:474, hitl_gate_composer.py:770, audit_writer.py:120, as_is_wiring.py:110}`; `harness-is/.../shadow_git_rollback.py:114`. Each populates `EntryPayload.procedural_tier_snapshot_ref` via the U-RT-112 resolver closure; landing all 7 unblocks `R-001-h-t-is-2-retired` (IS-2 PARTIAL → RETIRED). Per §4 derivation rule: with R-002 RESOLVED, R-003 is the lone executable-now ACTIVE phase-7 entry (all `depends_on` RESOLVED; R-005..R-009 are BLOCKED/DEFERRED on real-deployment or operator-decision). **Note:** R-003 is substantive phase-7 cross-axis implementation (edits `harness-cp/**` + `harness-runtime/**` + `harness-is/**` src + integration tests; PR-per-cluster of ~3-5 sites per L9-* precedent) — recommend a fresh decision + advisor pass before opening.

**(R-002 RESOLVED at PR #130 merge `6f8dd66` — Surface-I decomposition complete: 7 non-RETIRED rows mapped to R-NNN; R-001 (OD-5) + R-004 (AS-8d) reconciled stale BLOCKED → RESOLVED; dashboard retirement-progress table corrected.)**

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(none — in-flight chain + hygiene cascade + R-002 decomposition all cleared 2026-05-31)* | — | — | — |
| *(this PR)* | `worktree-roadmap-refresh-post-pr-130` | *(self, post-merge refresh)* | mode-agnostic |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #130 (`6f8dd66`) | 2026-05-31 | R-002 — Surface-I decomposition; 5 new per-row substitution entries (R-005..R-009); reconciled stale R-001 (OD-5) + R-004 (AS-8d) BLOCKED → RESOLVED (both RETIRED via mech-β batches 31-32); dashboard retirement-progress table corrected |
| PR #128 (`3ba4fae`) | 2026-05-31 | R-IF-HYGIENE-CXA-COUNT-CASCADE — CXA v2.18 count cascade to canonical pointers (aggregate 107→105; phase-2-runtime 22→20; OD→IS 6→4; OD outbound 27→26); mode-agnostic; §108/§109 sibling-completeness applied |
| PR #111 (`fdf120b`) | 2026-05-31 | R-IF-111 — OD plan v2.27 NEW §4.6.OD-INTERNAL carve-out; halt-doc Item 12 closed; sibling to #110; design-phase posture, clearance marker present (operator-ratified) |
| PR #110 (`2f14604`) | 2026-05-31 | R-IF-110 — CXA v2.18; CXA-OD-IS-EDGE-DRIFT (Item 11) closed; §2.3.4 6→4, aggregate 107→105; design-phase posture, clearance marker present (operator-ratified) |
| PR #129 (`84b9908`) | 2026-05-31 | ops: roadmap status refresh post-PR-128 (tenth terminating refresh; next-action → R-002) |

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
| RETIRED | 35+ (per batch-49; incl. AS-8d batch-31 + OD-5 batch-32 via mech-β) | See `harness-*/CLAUDE.md` §4.1 + `phase-7d-retirement-events-batch-*.md` for canonical enumeration. CP-axis §4.1 fully RETIRED. |
| RETIRE-READY | 2 active (**OD-3 + OD-6**) | OD-3 (R-007) + OD-6 (R-009) await real-deployment X-AL-2 second conjunct OR operator-AUQ Reading α. **Corrected at R-002 survey 2026-05-31: AS-8d + OD-5 are RETIRED (batches 31-32), not RETIRE-READY — prior table was stale.** |
| PARTIAL | H_T-IS-2 (R-003) + H_T-OD-4 (R-008) | IS-2 awaits 7 producer-site lifts post-PR #107 (R-003); OD-4 awaits §13.1 per-session toggle + §13.2 tokenization gate closures (R-008). |
| STILL-BOUNDED-INDEFINITELY | 2 (AS-8e + AS-8f) | AS-8e files.* (R-005 DEFERRED) + AS-8f managed_agents.* (R-006 DEFERRED) — indefinite-defer per runtime spec v1.17 §14.C / v1.33; X-AL-2 bounded-residual carry. |
| RETIRED-AS-AUTHORING-ONLY | 4 | Sub-species 10 closures (OD-1, OD-7, IS-4, CP-23) per batches 37+38+39+41 |

**Decomposition COMPLETE (R-002 RESOLVED 2026-05-31):** all non-RETIRED rows mapped to R-NNN entries at roadmap §5.2 — IS-2 (R-003 + R-001-h-t-is-2-retired), OD-3 (R-007), OD-4 (R-008), OD-6 (R-009), AS-8e (R-005), AS-8f (R-006). R-001 (OD-5) + R-004 (AS-8d) reconciled stale BLOCKED → RESOLVED. Execution of each per-row entry gated as noted (most on real-deployment / operator-decision; R-003 producer-lifts is the lone executable-now phase-7 entry).

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

**Audit protocol exercised across 11 closure events + 1 fresh-session reconciliation.** Discipline + enforcement layers both operational. **In-flight chain + hygiene cascade + R-002 decomposition fully cleared 2026-05-31; deterministic next-action = R-003 (phase-7 cross-axis producer-site lifts).**

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
