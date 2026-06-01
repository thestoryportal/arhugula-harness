# Fork-doc Status audit log

*Home for the recurring "survey fork-doc files for Status-line refreshes against current production state" audit (dashboard `.harness/roadmap_status.md` → Outstanding fork docs → **Audit-owed**; cadence every ~5 PRs or operator-discretion). Append a dated entry per audit pass. Mirrors the survey-log convention codified for the clearance-marker survey at `.harness/clearance/README.md` (PR #175).*

---

## Method

For each `.harness/class_*_fork_*.md`:

1. Extract the leading `**Status:**` verdict token.
2. Classify terminal (`APPLIED` / `RATIFIED-AND-APPLIED` / `FULLY-APPLIED` / `CLOSED` / `RESOLVED` / `RESOLVED-AS-INVALID` / `SUPERSEDED` / `DEFERRED-INDEFINITELY`) vs. non-terminal (`PROPOSING` / `OPEN` / `PENDING` / `FILED` / `PARTIAL`).
3. For non-terminal + conditional/partial + any **undischarged forward obligation** in the header ("transit owed at batch-N", "co-publication owed", "remains OPEN at §X"), verify against current production state: merged PRs, latest retirement batch, sibling fork docs, current spec/plan versions per workspace `CLAUDE.md` §2.
4. Refresh genuinely-stale Status lines / cross-references in place. Leave accurate terminal + accurately-open verdicts untouched.

---

## 2026-06-01 — audit pass (operator-requested; post-PR-#178)

**Anchor.** Workspace HEAD `df6375d` (origin/main); 43 open fork docs; latest retirement batch `.harness/phase-7d-retirement-events-batch-50.md`; merged PRs through #178; zero open PRs.

**Scope.** All 43 `.harness/class_*_fork_*.md`.

**Distribution (leading verdict).** 41/43 carry accurate terminal verdicts. The two most recent R-100 tool-step forks (`tool_step_no_operator_supplied_converter`, `tool_step_no_bootstrap_sandbox_decision_resolver`) already reflect PR #171/#172 (APPLIED-AS-READING-B). ~13 docs carry an explicit "status-line refreshed 2026-05-27" tag from the prior carry-set sweep.

**Genuinely non-terminal — verified ACCURATE (no edit):**

| Fork doc | Verdict | Verification |
|---|---|---|
| `class_1_fork_harness_toml_default_discovery_unimplemented.md` | `PROPOSING` | Genuinely open; awaiting operator ratification; tracked at roadmap `R-100-mvp-config-discovery`; non-blocking for the MVP. No later PR resolved it. |
| `class_2_fork_tool_invocation_composer_scope.md` | `DEFERRED` (bounded-residual, 2026-05-20) | Path X/Y/Z tool-invocation-composer scoping decision still owed at operator timing. The PR #171/#172 TOOL_STEP work is the *runtime dispatch path* (MCP tool-contract converter + sandbox resolver), not this CP-axis composer-scope design decision — distinct surface; deferral stands (aging, not stale). |
| `class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` | `RATIFIED-AMENDED + PARTIAL-RETIREMENT` | H_T-CP-16/18/AS-2 RETIRED (batches 14/16); H_T-CP-17 (Files arc) preserved PARTIAL, deferred indefinitely per §14.C. Frontmatter refreshed 2026-05-31. Current. |

**Substantive correction applied (1):**

- **`class_1_fork_cp_spec_section_25_contract_id_collision.md`** — headline verdict `FULLY-CLOSED` is correct and unchanged. Its **trailing cross-reference clause** "Reading B full validator-composer arc remains OPEN at §3.2" (appearing at 3 sites: Status line, §"Status post-§9", end-of-doc routing line) was **stale**. That clause is a cross-reference to `class_1_fork_validator_composer_arc_stage_4_absence.md` §3.2, whose Reading B was **APPLIED at runtime spec v1.22 on 2026-05-24** (commit `918f94a`) — and which closed its *own* copy of the stale-carry on 2026-05-27 without propagating to this doc. Refreshed all 3 sites to reflect the APPLIED state. Species-3 (resolved-but-carry-stale-inherited) per workflow v1.9 §7.4.7.2 — sub-shape: stale *cross-reference* (the carrier was a citation to a sibling fork's §3.2, not this fork's own framing).

**Conclusion.** Fork-doc Status corpus is current. 1 stale cross-reference refreshed; 42/43 verdicts accurate (41 terminal + 1 accurately-`PROPOSING`). No headline Status verdict required a change. Next audit cadence: ~5 PRs or operator-discretion.
