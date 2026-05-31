# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `47c763cb4fb3` |
| `last_refreshed` | 2026-05-31T19:30:00-06:00 |
| `git_head` | `65ed6463` (main) — `ops: NotebookLM skill installed + R-600 RESOLVED in single arc (#118)` |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-49.md` |
| `open_fork_doc_count` | 39 |

**Hash recipe.** `sha256(git_head[:8] + "|" + sorted_open_pr_csv + "|" + open_fork_doc_count + "|" + latest_retirement_batch_path)[:12]`. See `Project_Roadmap_v1.md` §7.1.

---

## Next action

**`R-IF-108`** — workflow v1.12 §7.4.7.3.C audit at per-axis CLAUDE.md §4.1 (in-flight PR; mode-agnostic posture; verification: grep). Per §4 derivation rule: priority 1 mode-agnostic infrastructure, lowest R-NNN among ACTIVE entries with all `depends_on` RESOLVED.

**Fallback if all R-IF-* close before next session:** `R-002` (remaining substitution retirements survey; surface I; posture phase-7; skill `phase-7-substitution-retirement`; verification grep). First execution decomposes §I atomic-unit set.

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| #108 | `worktree-claude-md-section-4-1-audit-2026-05-31` | `R-IF-108` | mode-agnostic |
| #109 | `worktree-memory-audit-round-3-2026-05-31` | `R-IF-109` | mode-agnostic |
| #110 | `worktree-cxa-v2-18-item-11-od-is-edge-drift` | `R-IF-110` | design-phase |
| #111 | `worktree-od-plan-v2-27-item-12-od-internal-formalization` | `R-IF-111` | design-phase |
| *(this PR)* | `worktree-roadmap-post-merge-refresh-pr-112` | *(self, post-merge refresh)* | mode-agnostic |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #118 (`65ed646`) | 2026-05-31 | ops: NotebookLM skill installed + R-600 RESOLVED in single arc |
| PR #117 (`6401e2a`) | 2026-05-31 | ops: roadmap status refresh post-PR-116 |
| PR #116 (`63c4464`) | 2026-05-31 | roadmap-design-extension: NEW §XI surface + 3 R-XI PROPOSED entries |
| PR #115 (`675c321`) | 2026-05-31 | ops: roadmap status refresh post-PR-114 |
| PR #114 (`7da53e5`) | 2026-05-31 | roadmap(v1.1) §12.2.1 recursion-stopping codification + §12.1 step 6 fixed-point carve-out |

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
| PARTIAL | H_T-IS-2 + others | H_T-IS-2 awaits ~13 producer-site lifts per R-003 |
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

**Audit protocol exercised across 3 closure events.** Discipline operational at pure-refresh + bundled-roadmap-extension + bundled-tooling-setup shapes.

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
