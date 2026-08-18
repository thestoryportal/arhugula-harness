# E1 A2 — C11 operator loop / local deployment (consultant, reacting to C9/C10/C7)

## Reactions to primaries

| primary | reaction | evidence | resulting fix |
|---|---|---|---|
| C7-F7 (`lane_id` column) | REFINE | `loop_lib.sh:231` operator-facing printf `'[loop] ⏸ %s item(s) await your input … See .harness/loop_status.md'`; `loop_cap_list()` `:209-216` truncates with no lane token | C-HE-09 §3: "`loop_pending_hil_summary()` and `loop_cap_list()` MUST render the `lane_id` token in every emitted item (e.g. `[lane-2] R-410 — …`), not merely carry it as a column." |
| C7-F10 (`loop_status_path()` body-only) | REFINE | `grep -rn '\.harness/loop_status\.md'` → 7 non-test hits: `loop_lib.sh:6,231`; `loop-start/SKILL.md:16,34`; `loop-stop/SKILL.md:23`; `resolve/SKILL.md:15`; `ship-pr/SKILL.md:309` | C-HE-09 §2: "The venue move MUST sweep every literal `.harness/loop_status.md` citation (enumerated at HEAD above); a grep for the literal with zero hits outside test fixtures is the acceptance check." |
| C10-T7 (demotion row) | REFINE | A C-HE-24 row is pull, not push; the operator never sees a silent gate weakening | C-HE-31 §4 (composing with C10): "the demotion event MUST also fire a non-blocking informational notification through the loop_status venue at the moment it occurs (check name, triggering count, harness continues)." |
| C10-T8 (`strict:true` tiebreaker) | REFINE | No `main-protection-*` recipe exists (`grep justfile` → 0); C-HE-08 §2/§4 hand the operator raw `gh api -X PUT/DELETE` prose — contradicts `CLAUDE.md` §12.4.1 ("The operator executes nothing manually") | Fold into C11-F1: the recipe's `--dry-run`/tiebreaker mode runs the stale-branch fast-forward check itself. |

## Own findings

| id | class | contract | quote | defect | fix |
|---|---|---|---|---|---|
| C11-F1 | 2 | C-HE-08 §2–4 | "the plan owns the recipe; the operator answers the gate" / "Recipe: `gh api -X PUT …`" | The contract writes a raw `gh api` command for a non-coding operator; §8.1 tags the live step "operator (live)" — a chore, not a decision. | "The apply / show / rollback / tiebreaker steps MUST be wrapped as `just main-protection-{apply,show,rollback,tiebreaker}` that Claude runs outside loop mode; the recipe embeds the JSON payload, runs the §4 stale-refresh-branch fast-forward check, prints one before/after diff. The operator's role reduces to one AskUserQuestion: 'Apply branch protection to `main` now? [diff shown]'. §8.1 row: `loop, live — operator answers one decision`." |
| C11-F2 | 2 | C-HE-09 §2 | "resolved by one function `loop_status_path()`" | 7 hardcoded pointers (above) become wrong after the venue move | Sweep list in C-HE-09 §2 acceptance |
| C11-F3 | 2 | C-HE-06 §10, C-HE-31 §4 | "routes a **non-blocking** HITL notification" | `loop_log` kinds (`loop_lib.sh:2-9,73-74`): `ACTIVATE / DEACTIVATE / DEFERRED-HIL / RESOLVED-HIL / COMPLETED / DENY / RESOLVE-SPLIT / RESUME` — no informational kind; misusing `DEFERRED-HIL` enters `loop_skip_set()` (`:134-157`) and turns an FYI into a hard-stop | Add a `NOTIFY` row kind (C-HE-09/C-HE-06 §10 jointly): append-only, rendered at SessionStart beside (never merged into) the DEFERRED-HIL summary, excluded from `loop_skip_set()`; used by C-HE-06 §10 tiering and the demotion notice. |
| C11-F4 | 2 | C-HE-29 §2–3 | "adjudicator of **neither model family**" | No delivery mechanism for the round-15 kill/keep decision (D-D: "operator to accept or amend"); no rubric; identity unresolved (operator vs an unsanctioned automated judge) | "The round-15 evaluation MUST fire as an escalation-kind HITL request presenting the 15 rows' `unique_catch` dispositions and the threshold; responses ∈ {approve-kill / reject-keep / respond-amend-threshold}. The per-round adjudicator MUST be named as 'operator' or a specific third-party reviewer identity; if operator, sessions persist in `hitl_queue` with `kind='shadow-trial-adjudicate'`." |
| C11-F5 | 3 | C-HE-13 §3 | pilot-success iff-clause | Requires correlating three stores; no command computes it | Add `just lanes-pilot-report <pilot-run-id>` printing PASS/FAIL + friction rows. |
| C11-F6 | 2/3 | C-HE-11 §1 | per-lane compose stacks | Operator machine is Intel i5/16 GB; 4 lanes × 3 containers + Docker VM + 4 sessions; only the daemon-absent case is handled; a resource-starved OOM mid-pilot is indistinguishable from a coordination defect. [MODERATE confidence — architectural read, not benchmarked] | "Lane-init MUST probe memory/Docker-VM headroom before bringing up a stack at `HARNESS_LANE_INDEX ≥ 2` on a machine below an operator-configured RAM floor (default 32 GB), and on shortfall MUST emit `NOTIFY` naming the constraint; such a failure MUST NOT be recorded under a `merge-door-`/`reservation-` cause_signature." |

## Position on T2 / T8 / T7 / T9

T2 RECONCILE(wording): mechanism accepted; the fix is incomplete without the pointer sweep (C11-F2) and rendered `lane_id` (C7-F7 refinement). T8 RECONCILE(wording): D5 accepted + C10's `strict:true` addition, but un-runnable by the operator as written — C11-F1 must land. T7 RECONCILE(wording): C10's row is necessary, not sufficient — `NOTIFY` push notice (C11-F3). T9 RECONCILE(wording): C7's marker-row + actor fix accepted; the kill/keep decision needs a HITL delivery contract (C11-F4).

## Verified at HEAD

`loop_lib.sh:18-27,73-85,134-157,225-232` · `lib.sh:18-22` · 7 literal `.harness/loop_status.md` hits · `HARNESS_LOOP_STATUS_PATH` 0 hits · `justfile:463-480` no `-p`; `main-protection` 0 hits · `compose.yaml:1-49` three services, project-prefixed volumes · `.claude/skills/two-lane/SKILL.md:1-40` · `CLAUDE.md` §12.4.1 verbatim.

## Voice self-check

Stayed in operator-experience/local-deployment; did not re-litigate CAS semantics or specify the GitHub API payload. C11 is the wrong voice to judge whether four-lane Docker isolation is architecturally sound — flagged as an on-real-hardware risk with an explicit confidence caveat.
