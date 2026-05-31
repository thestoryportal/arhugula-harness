# Roadmap status dashboard

*Refreshed at session-start audit + post-PR-merge audit per workspace `CLAUDE.md` §12. Consumed by the next-action derivation rule at `Project_Roadmap_v1.md` §4. **Do not hand-edit during execution — refresh via the protocol at `Project_Roadmap_v1.md` §7.2.***

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `5a077d17765f` |
| `last_refreshed` | 2026-05-31T18:58:00-06:00 |
| `git_head` | `7f3e6ceb` (main) — `roadmap(v1): Project Roadmap v1 scaffolding — drift-detected deterministic next-action derivation (#112)` |
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
| PR #112 (`7f3e6ce`) | 2026-05-31 | roadmap(v1) scaffolding — drift-detected deterministic next-action derivation (this artifact) |
| PR #107 (`89915af`) | 2026-05-31 | apply PR #105 Reading C — CP spec v1.30 + plan v2.31 |
| PR #106 (`c8918b3`) | 2026-05-31 | overnight expansion summary — 5 work units / 1 fork / 0 hidden halts |
| PR #105 (`2ba7a1f`) | 2026-05-31 | Class 1 fork filing: PR-2 workflow-layer composer ctx-access |
| PR #104 (`4294d41`) | 2026-05-31 | memory audit round-2 — 50 entries / 7 findings |

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
| 2026-05-31 | First post-merge refresh — PR #112 merged at `7f3e6ce`; dashboard hash recomputed `9c31e4978c3d` → `5a077d17765f` | Refreshed via this PR per CLAUDE.md §12.2. |

**Audit protocol exercised end-to-end at v1 publication.** Post-merge refresh discipline confirmed operational.

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
