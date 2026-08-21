# Specification - H_E Autonomous Loop + Parallel Lanes v1

## Status

Clearance-folded draft (operator draft review ✓ → Codex gate 7/10 ✓ → harness council + adversarial + Codex cold review ✓ → consolidated reconcile + fold ✓ → E4 residual sweep → operator ratification → clearance marker).

Path: `.harness/spec/Spec_HE_Loop_Lanes_v1.md` · Date: 2026-08-18 · **v1.4** (execution-correction change-notes X1 2026-08-18 + X2 2026-08-19 + X3 2026-08-19 + X4a–X4d 2026-08-20; marker `spec-he-loop-lanes-v1.4-cleared-2026-08-20.md`) · Repo at `17011f89c` (all `file:line` cites are pinned to this commit) · Namespace `C-HE-*` (H_E dev tooling; see §0.2)

Authority chain (earlier links govern where later links are silent — HE-1 §0):
`BUILD-PLAN-operator-ratified-2026-08-17.md` (operator-ratified: D-A…D-D, Arcs 1–7) →
`HARNESS-LOOP-AND-LANES-DESIGN-v1.md` (consolidated full-loop design; L-1…L-5, X1–X8, AC#1–10) →
`HARNESS-LOOP-AND-LANES-DESIGN-v2.md` (head; lanes-narrow supersession: flock killed, AC#2 on subprocess, three-state reservation, `concurrent_lanes` cohort key, coalescing enacted, X9; council rulings R-1…R-29) →
`.harness/adr/ADR-HE-1..4` (the four foundational decision records, filed 2026-08-17) →
**this specification** → implementation plan (next phase) → Phase-7-style implementation.

Evidence tags: **[V]** re-verified at HEAD `17011f89c` in this authoring session (2026-08-18) · **[C]** council- or corpus-recorded, not independently re-verified here · **[R]** operator-ratified (BUILD-PLAN 2026-08-17 or the D5–D8 spec-phase decisions of 2026-08-18, §12).

## Change-note (v1.4 — execution correction, 2026-08-20)

**Trigger.** S4b/S4c execution (U-HE-19 #1409, U-HE-20 #1411, U-HE-21 #1412, U-HE-22): four registered wording classes — held under the register-and-hold discipline across 22 (U-HE-19), 7 (U-HE-20) and 7 (U-HE-21) out-of-family rounds and adjudicated by the 3-lens merge gate on each landing PR — reconcile here, at the merge-door landing this spec routes them to (U-HE-19 rev items (vii)/(ix); U-HE-20 rev item (v); the U-HE-21/U-HE-22 flip-timing carrier lines). The landed, multi-round-reviewed behavior governs; each edit conforms the sentence to it.

- **X4a — the flip-timing class (C-HE-03 §4 + C-HE-06 Invariants).** §4 named drain start as the only `pending→open` flip, while C-HE-06 acquisition demands an `open` holder and the closure drain runs post-merge — wired literally, the door would reject every normally-opened arc (U-HE-21 codex r2/r6 P1s). §4 now names the merge lane's pre-acquire flip (ship-pr final gate / land driver) alongside drain-start (closure-capture/bootstrap path). The C-HE-06 Invariants bullet "no lease exists whose reservation is not `open`" could not be read literally across the §4(vi)–(ix) continuation (the reservation legitimately reads `merged` while the lease holds through post-merge CI + the refresh — the plan §6 item 13 candidate): it now binds at ACQUISITION (§7 P2), where the code enforces it — and (r9) the §7 Contract sentence itself is aligned ("MAY be ACQUIRED only ... open" replacing "MAY be held only ... open"), closing the same contradiction at its second carrier.
- **X4b — the merged-gate class (C-HE-03 §6 + C-HE-04 §2(ii)).** The open-only append gate contradicted the §4(vi) door flip preceding the closure drain (U-HE-19 item (vii), 12 rounds re-raised): both sentences now carry the landed carve-out — the merged HOLDER's own FIRST capture is admissible; "re"-append means a second row, foreclosed by the committed-history duplicate guard. Witness: `test_merged_holder_own_capture_drains_normally` (landed U-HE-19).
- **X4c — the §5 drop-vs-keep class (C-HE-04 §5 + Verification (vi)).** "MUST drop those local rows" and interleaving (vi)'s "drops its orphaned local row" contradicted the landed keep-loudly + converge-at-committed-point behavior (U-HE-19 item (ix); U-HE-20 item (v), HELD against two re-raises of the spec-literal drop: dropping a merged-without-committed-replacement row could discard the only capture). Both sentences now state: converge superseded rows WITH a committed replacement to the canonical line; KEEP merged-without-replacement rows loudly. The §5 committed-history read is named as the local `MERGED_REF` snapshot (freshness bounded by fetch cadence), and §4 names the merged-headless-capture stall (dead between flip and first append → holds loudly to §5 HITL; `transfer_holder` is open-only by design) — both U-HE-19 (ix) registered residuals, now spec-carried.
- **X4d — §8.1 lanes row count.** "(5 interleavings)" → "(6 interleavings)" (stale against the C-HE-04 Verification body's six, which governed; U-HE-20 rev item (viii)).

**Scope + reversal.** Wording-only: no `C-HE-*` guarantee, contract number, store count, §5 file set, or §6 order changes; the §8.1 count fix is informational (the Verification body already enumerated six). Clearance is proportionate: every edit conforms spec text to behavior already reviewed to terminal by the out-of-family chain + 3-lens merge gate on #1409/#1411/#1412; no council convened (no committed surface is revisited — the sentences were internally contradictory, which is what the register-and-hold class recorded). **Operator may reverse** by a v1.5 note. Marker: `.harness/clearance/spec-he-loop-lanes-v1.4-cleared-2026-08-20.md`.

## Change-note (v1.3 — execution correction, 2026-08-19)

**Trigger.** S3 execution (U-HE-14, the C-HE-30 store audit `.harness/spec/store-audit-he-loop-lanes.md` + `tools/test_store_audit.py`): out-of-family Codex rounds 2–4 on the U-HE-14 PR held the audit against C-HE-30's clearance-fold parenthetical — *"all derived from the authorities above, none a new authority for an existing fact"* — and showed its first clause is false for six of the families it names: the `transition.<token>` marker (C-HE-06 §6 payload `{pid, host, target_action, created_at}`, from which a third party completes a dead creator's transition after `LEASE` has moved), `merge-door/attempts/` (the rate window), `tier-clean-cycles/` (the §10 counter), `lanes/<k>`, `hil-deliveries/<gen-id>` (exclusive-create registries), and `.harness/mechanized-checks-state.json` (a promotion is recorded only there). Each is the **sole carrier of a NEW coordination fact** this spec introduces — not recomputable from the eight authorities — while the parenthetical's operative invariant (no **existing** fact gains a second carrier; the authority set for existing facts is exactly the eight) holds for every one. An audit that certifies C-HE-30 cannot certify against a sentence it has to call false.

- **X3** C-HE-30, three wording edits. (i) The clearance-fold parenthetical "all derived from the authorities above, none a new authority for an existing fact" is REPLACED by "each either derived from an authority above or the sole carrier of a new coordination fact this spec introduces — never a second authority for an existing fact; the audit document classifies every family as one or the other". (ii) The opening sentence "The store set after this spec is **eight** (seven from HE-1 §5 plus the gate sibling)" becomes "**eight** authorities for the facts HE-1 §5 enumerates (…) **plus the coordination-state carriers the clearance fold adds** (enumerated and classified by the audit document)" — a durable sole carrier is itself a store, so the count sentence can no longer read as the whole durable set. (iii) Verification: "plus the derived families named in the note" becomes "plus the families named in the note (each classified `derived` / part of a store / sole carrier of a new fact)". The contract table (the eight rows), the "any fact with two authorities" rule, both Invariants and the Verification row's mechanics are UNCHANGED. Witnesses: `tools/test_store_audit.py::test_family_table_relation_cells_are_classified` (pins each family's `Relation` cell: `derived` vs `sole carrier (new fact)`), `::test_eight_store_table_one_row_per_store_one_fact_per_row`.

**Scope + reversal.** Wording-only: no `C-HE-*` guarantee, contract number, store count, §5 file, or §6 order changes; no implementation site (the S4 units that create these files land against the unchanged C-HE-06/C-HE-11 contracts). Clearance is proportionate: surfaced and reviewed by the out-of-family chain on the U-HE-14 PR (rounds 2–4); no council convened. **Operator may reverse** by a v1.4 note. Marker: `.harness/clearance/spec-he-loop-lanes-v1.3-cleared-2026-08-19.md`.

## Change-note (v1.2 — execution correction, 2026-08-19)

**Trigger.** S1 execution (U-HE-02/04/06, `tools/review_wrapper_common.py` + `tools/codex_review.py` + `tools/agy_review.py`): the first live `just review-with-failover` on the S1 branch (≈2.4 k-line diff) hit `REVIEWER_UNAVAILABLE (transient: attempt 2 timed out after 550s)` on the codex channel — both attempts were killed at 550 s mid-review (session artifacts `rollout-2026-08-18T23-54-50-*` and `rollout-2026-08-19T00-03-59-*` carry no `task_complete`), and U-HE-01's ten out-of-family rounds on a smaller diff each ran ≈590 s (`duration_ms: 591514` **[C]**). C-HE-16 §3's `per_attempt_timeout: 550 s` was budget arithmetic (two attempts + margin under 1260 s), not a measured channel duration; as written it makes the codex channel systematically unavailable on any non-trivial PR and demotes every such review to the failover — the chain could not review its own PR. Per §14 this lands as a dated change-note; the affected clause carries an in-place tag pointing here.

- **X2** C-HE-16 §3 retry parameters: `per_attempt_timeout` becomes a **cap of 1200 s** (= `MAX_AGY_PRINT_TIMEOUT_SECONDS`, `agy_review.py:23` — the bound the gemini channel already applied to a single invocation before S1); every attempt's actual timeout is `min(1200, remaining − margin)` on the shared 1260 s deadline (margin 0 s on attempt 1, 30 s on attempt 2), so attempt 1 may run to ≈1200 s and a second attempt exists only when the first failed **fast** — which is exactly the transient class the retry is for (empty output, rate-limit, auth flake); a timed-out attempt is not meaningfully retriable under any budget. `max_attempts: 2`, no backoff, `total_budget_s: 1260`, permanent-skips-retry, exhaustion → `HITL-recoverable` are UNCHANGED. Witnesses: `tools/test_review_wrapper.py::test_transient_then_success_uses_two_attempts_and_dynamic_second_timeout` (`[1200, 430]`), `::test_retry_constants`; `tools/test_agy_review.py::test_large_review_shares_one_deadline_across_segments_and_synthesis` (`[1200, 860, 460]`).

**Scope + reversal.** Parameter-only: no terminal state, classifier row, failover rule, contract number, §5 file, or §6 order changes; C-HE-18 §2's 130 s artifact lag is untouched. Clearance is proportionate: reviewed by the same out-of-family chain on the S1 PR (round 3 onward runs under X2). **Operator may reverse** by a v1.3 note; `review_wrapper_common.PER_ATTEMPT_TIMEOUT_S` is the single implementation site (both channels read it). Marker: `.harness/clearance/spec-he-loop-lanes-v1.2-cleared-2026-08-19.md`.

## Change-note (v1.1 — execution correction, 2026-08-18)

**Trigger.** U-HE-01 execution (PR #1395, `tools/finding_record.py`): out-of-family Codex rounds 6–7 held the implementation against C-HE-23 §2's mechanism parenthetical "(append, single `write` under `PIPE_BUF`)" and found it unsatisfiable as written — a C-HE-24 row (two 40-char SHAs, a 64-char digest, evidence text) is ≈700 bytes against macOS `PC_PIPE_BUF` = 512, and `PIPE_BUF` is POSIX's atomicity bound for **pipes and FIFOs**, not regular files. Per §14 this lands as a dated change-note, never an in-place rewrite; the affected clause carries an in-place tag pointing here.

- **X1** C-HE-23 §2 write-order clause: the mechanism parenthetical is REPLACED by the guarantee a regular file can carry — one `write` syscall per row on an `O_APPEND` descriptor; writers serialized by an exclusive lock on the log's own descriptor (an `flock` outside C-HE-02 §1's scope, whose invariant names the three `QUEUE_DIR` coordination modules; the finding log is REPO-resident, per lane, git-merged, and is not cross-lane coordination state); a short write rolled back to the pre-write offset before the failure surfaces, so a torn tail never poisons the log. Write-first order, the fail-closed rule (a verdict that cannot be recorded does not count, C-HE-15 §1), the `warn`-on-markdown-failure rule, and file-order reduction are UNCHANGED. Witnesses: `tools/test_finding_record.py::test_append_is_one_write_syscall_and_a_short_write_rolls_back`, `::test_check_and_append_are_one_critical_section` (mutation-probed).

**Scope + reversal.** Mechanism-only: no `C-HE-*` guarantee, contract number, §5 file, or §6 order changes; C-HE-09 §1's `loop_log()` single-write sentence is untouched (a status line is small; not re-examined here). Clearance is proportionate to the change: reviewed by the same out-of-family Codex chain that surfaced it (rounds 6–8 on the U-HE-01 PR) and by the PR; no council convened. **Operator may reverse** by a v1.2 note (e.g. a bounded-frame row encoding that fits under `PIPE_BUF`); `tools/finding_record.py::_append_line` is the single implementation site. Marker: `.harness/clearance/spec-he-loop-lanes-v1.1-cleared-2026-08-18.md`.

## Change-note (v1 — clearance fold, 2026-08-18)

**Trigger.** Clearance review per D4: Codex executability gate (6/10 → 7/10 after iteration 1), harness council (primaries C9/C10/C7; consultants C5/C1/C11/C8; consolidated reconcile), `harness-adversarial-reviewer` (LOOP-BACK: 3 Class 1 / 3 Class 2 / 1 Class 3), out-of-family Codex cold review (7 Class 1 / 5 Class 2 / 3 Class 3). Ledger: `.harness/council/spec-he-loop-lanes-v1/`. In-place amendment is permitted (the record had not been consumed); each fold is tagged in the affected contract. Fold groups G1–G22 (`05-reconcile/merged-findings-and-proposed-dispositions.md`), with the reconcile's second-order corrections applied:

- **G1** C-HE-03 reservation → generation-versioned immutable files, pure exclusive-create CAS, re-validate-on-loss, full snapshots, tmp sweep (Codex C1-01/C3-03; C9 reconcile).
- **G2** No TTL reclaim at any tier; aged `pending` → `NOTIFY`+HITL (Codex C1-02, ADV-F1; §12 O3 corrected).
- **G3** Lease `lease_token` + `transition.<token>` marker with provenance + idempotent third-party completion; self-resume = reclaim; no path-only unlink (Codex C1-03; C9 poison-pill).
- **G4** Lease held through post-merge CI (45 min) and the terminating refresh **as a continuation under the same lease** (C10; C9's alternative rejected because releasing early stacks content commits into `ROADMAP_STATUS_DRIFT`), bounded, `blocked` state + `just merge-door-unblock`, `main` CI concurrency keyed by SHA with the tradeoff stated (Codex C1-04).
- **G5** Codex-exec lanes OUT of v1 for C-HE-06/07 (C1 ruling); carrier sentence in C-HE-01 §1; `AGENTS.md` dropped from §5 (ADV-F3); §11 #9; runtime cross-carrier `NOTIFY` (C10). **Operator may reverse.**
- **G6** Flip-before-append; holder-gated `append()`; dead-claim holder transfer as a named D2 exception (C9 reconcile); local-row reconciliation; teardown guard incl. ahead-of-`@{u}`; sixth interleaving via `ARC_METRICS_TEST_KILL_AFTER`; liveness-predicate wording (ADV-F6, C9-F2/F6/F7/F9).
- **G7** C-HE-06 §8 split into yield-point (C1) + numbers (C9); primitive rate limit K=5/60 s not counted against the budget; §9 gate rows incl. `merge-door-reconcile` and budget-exhaustion `HITL-recoverable` (C5-F2/F3, C9-F3).
- **G8** T6: uncited server-behavior sentence replaced by an explicit statement of GitHub's per-PR serialization as backstop + `test_inflight_first_attempt_then_reissue` (C9-F8).
- **G9** Wrapper exact arity + explicit push-to-main `emit_deny` with predicates (C10-F1/F2).
- **G10** `just main-protection-{show,apply,rollback,tiebreaker,verify}`; `verify` phase0 read-only, runs local, `gh-auth-absent`; tiebreaker exercises `strict:true` (C11-F1, C10-T8, Codex C1-07, ADV-F5).
- **G11** `record_kind` union (arc rows only in `arc-metrics.jsonl`; finding-class rows in `merge-gate-log.jsonl`); envelope gains `base_sha, diff_digest, cause_attribution, disposition_actor`; schema requires all six binding fields + `severity ∈ {P1,P2,P3}`; `:`-free identifiers; projection wording (`startswith` consumer at `:634`); orphan class in the consistency reducer; `[R: BUILD-PLAN L0.2′]` (Codex C1-06/C2-01/C2-02/C2-04/C3-02, C7-F4/F9/F11, C5-F1/F4/F6, C10-F3 via C5, ADV-F7).
- **G12** `concurrent_lanes_at_open: int` key; joint `(N, arc_type)` stratification; correlational statement; corrected empirical premise (C7-F5, Codex C2-03, C8-F6).
- **G13** `loop_status.md`: option (b) ACTIVATE; structured column BEFORE detail (C7-verified rejoin defect, supersedes C-HE-10's "fifth column"); rendered `[lane_id]`; 7-pointer sweep; `NOTIFY` + `COALESCE-DELIVERED` kinds; pull-based coalescing (C7-F7/F10, ADV-F4, C11-F2/F3, Codex C2-05).
- **G14** Phase spans accrete on the reservation record; N6 defined with the `REVIEWER_UNAVAILABLE` exclusion (C7-F6/F8, C8-F5, C7 reconcile).
- **G15** Shadow trial: `no_finding` marker rows; `unique_catch` operational definition; corrected OC table; v1 default **n=30 / kill-if-<2**; HITL delivery; `disposition_actor` (C7-F3/F4, C8-F1/F2, C11-F4; C7 caught the ≈0.18 vs ≈0.41 error).
- **G16** Mechanized checks: fixed replay for promotion with stated OC; rolling two-strikes demotion; `gate_demotion` row + `NOTIFY`; runtime state file, never the spec (C10-T7, C8-F3, C5-F5, C11, C10 reconcile).
- **G17** K7 BUILD vs EVALUATE gates (C8-F4). **G18** Reviewer-concurrency probe ≥5 reps + pass rule (C8-F7). **G19** Review-wrapper retry table `550 s × 2 / 1260 s`, dynamic second timeout (C9-F4, C5, C9 reconcile). **G20** Port blocks `30000+100k+{0..3}`, lane index via exclusive create, RAM probe → `NOTIFY`, ref-lock numbers (Codex C1-05, C11-F6, C9-F5, C1-F3). **G21** C-HE-30 Invariants/Verification + phase0 row; `mutation-probe` manifest column + coverage check; `lanes-pilot-report`; "recurring" defined; C-HE-02 grep scoped; `CANCELLED` claim corrected (ADV-F2, C8-F8/F9, C11-F5, Codex C3-01).
- **G22** This note. §6 gains the S2 hand-off row (C1-F2/C7-T10/C8).

**Not folded.** T6 safety reading (C10 ACCEPT; adversary rejected the candidate); T1 — C10 ACCEPTS the R-19 supersession, P1 stands normative; C8's SPRT recorded as a permitted alternative (§11 #10). Nothing re-litigates D-A..D-D or D5–D8.

**Initial version (pre-fold) note.** Authored from the four `ADR-HE-*` records plus the un-swept corpus tail the ADRs recorded as a known gap (`parallel-lanes-2026-08-17/STAGE5`, `STAGE7`, `ERROR-LEDGER.md` E1–E49) and the loop-eng `STAGE3/5/7` dispositions of P6–P9. Corrections to the ADR text discovered while authoring, each carried into the contract it affects rather than silently absorbed:

- **HE-4 §8 negative claim is false at HEAD.** `tools/codex_context_guard.py` **is** CI-wired — `.github/workflows/ci.yml:536` invokes `check --base-ref … --head-ref … --allow-roadmap-drift` and `:542` runs its tests **[V]** — and it **has** a local recipe, `just codex-context-check` (`justfile:84-87`: `checkpoint --label local-check --include-branch-diff` then `check --require-fresh-checkpoint --include-branch-diff`) **[V]**. K3's "no local equivalent at all" is therefore a **flag/ref-parity gap**, not absence — see C-HE-33.
- **HE-2 §6's literal "zero occurrences of `author`"** is wrong for a case-insensitive substring search (five hits: "authoritative"/"authorization"/"unauthorized", `agy_review.py:284,292,358,363,372`) but its substantive claim holds: the only CLI argument is `--base` (`:612`) and there is no authorship parameter or logic **[V]** — see C-HE-17.
- **HE-4 §3.2 recorded K5–K8 as "Proposed"** without recording that the loop-eng corpus had already adjudicated them: P7(=K6) **dropped unanimously**, P6(=K5) mandatory alternatives → **optional**, P8(=K7) **deferred**, P9(=K8) **restructured** (`STAGE3-opus-reconciliation-of-debate.md:30-58`, `STAGE5-opus-integrated-reconciliation.md:165-177`, `STAGE7-FINAL-opus-grounded-findings.md:145`) **[V]** — see C-HE-35.
- **E9/E21 loss path** (`ERROR-LEDGER.md:15,38`) — the ABA takeover at `_claim_arc:624-626` can strand an appended-but-uncommitted ledger row with **both** queue entries gone; no ADR states the fix — see C-HE-04.
- **E17** (`ERROR-LEDGER.md:32`) — `two-lane/SKILL.md` instructs picking arcs whose `scope.files` do not overlap while the forward register carries **zero** such keys across 186 rows **[V]** — see C-HE-13.

---

## 0. Scope, posture, and reading rules

### 0.1 What this specification governs

The H_E autonomous loop (`roadmap-continue → ship-pr` and its hooks, `tools/arc_metrics.py`, `tools/hooks/*`, `.claude/skills/{two-lane,ship-pr,merge-gate,roadmap-continue}`) and its extension to **N ≥ 2 concurrently building lanes** landing through one merge door. Four contract areas, one per ADR:

| Part | ADR | Contracts |
|---|---|---|
| A — Coordination | HE-1 | C-HE-01 … C-HE-14 |
| B — Review gate + completion | HE-2 | C-HE-15 … C-HE-22 |
| C — Record + measurement | HE-3 | C-HE-23 … C-HE-30 |
| D — Mechanization + grounding | HE-4 | C-HE-31 … C-HE-35 |
| E — Cross-cutting | all | §6 sequencing · §7 store audit · §8 acceptance · §9 failure modes → detections · §10 out of scope · §11 open items · §12 decision register · §13 references |

### 0.2 Posture and namespace

Mode-agnostic workspace-operational work per `CLAUDE.md` §11.2. `C-HE-*` contracts govern **H_E dev tooling only**; they do not extend the H_T design and do not implicate invariant I-2 / X-AL-3 (README of `.harness/adr/`). The `C-*` families in `design-substrate/` are H_T product contracts and share no number space with this file. Nothing here instantiates H_T's `TopologyPattern` (CP-AL-1) — "lanes" are H_E worktrees, not `orchestrator-workers`.

### 0.3 Requirement language

MUST / MUST NOT / SHOULD / MAY per RFC 2119. Every contract has `### Contract`, `### Invariants`, and `### Verification` (the tests the plan must materialize; each names its RED-first witness where one is required). A verification line marked **mutation-probe** MUST go RED against the unfixed guard it targets and GREEN after the fix, confirmed via `just mutation-probe` (v1 §11: *"A probe that cannot go RED first proves nothing"*).

### 0.4 Definitions

| Term | Meaning |
|---|---|
| **lane** | One autonomous session building one arc in its own git worktree, own gates, own reviewers. Identified by `lane_id`. |
| **arc** | One roadmap unit's build-through-merge lifecycle; identified by `arc_id` (queue-entry / ledger key). |
| **merge door** | The single-writer landing path: acquire lease → verify base → `gh pr merge` → confirm → release → terminating refresh (`CLAUDE.md` §12.2.1). Depth 1 by construction. |
| **reservation** | The durable per-arc, generation-versioned record created at arc **open** (selection) that spans through drain and the hours-long gap to the arc's confirmed merge (C-HE-03). Distinct from the closure-time **queue entry** (`arc_metrics.py queue` `*.json`/`*.taken` files). |
| **lease** | The seconds-long durable exclusive hold on the merge door (C-HE-06). |
| **filesystem CAS** | Atomic exclusive create (`O_EXCL` / `os.link` onto a fresh name) plus atomic rename (`os.replace`). The only coordination family permitted (C-HE-02). |
| **`QUEUE_DIR`** | The shared, outside-`REPO` directory (`ARC_METRICS_QUEUE_DIR`, default `~/.gstack/projects/arhugula-v2/arc-metrics-queue`, `arc_metrics.py:59-63` **[V]**). |
| **`REPO` / `LEDGER`** | Per-worktree module globals (`arc_metrics.py:44-45` **[V]**): the checkout root and `.harness/arc-metrics.jsonl` inside it. |
| **verdict** | A reviewer channel's output for one diff. It *counts* only under C-HE-15. |
| **finding** | One reviewer or deterministic-check observation, recorded per C-HE-24. |
| **HITL queue** | The existing durable operator-attention queue reduced from `loop_status.md` by `loop_lib.sh` (`DEFERRED-HIL` / `RESOLVED-HIL`). |
| **Phase 0 / 1 / 2** | v1/v2 lanes-arc sequencing (correctness floor / measurement / automation). **Arc 1–7** = ratified loop-arc sequencing. **Layer 0–4** = STAGE7. Not interchangeable — §6 gives the single unified order. |

### 0.5 Ratified operator decisions binding on every contract [R]

| # | Decision | Effect here |
|---|---|---|
| D-A | Build through Layer 2 (safety + measurement + speed) — full scope | Parts A–D in scope; STAGE7 Layers 3–4 out (§10) |
| D-B | Extend existing records; do NOT build a new ledger | C-HE-23 |
| D-C | Second cross-vendor reviewer wired as automatic failover | C-HE-17 |
| D-D | Shadow trial wired live; value measured in runtime | C-HE-29 |
| D5 (2026-08-18) | X9 fix = **both** server-side protection and client-side predicate | C-HE-08 |
| D6 (2026-08-18) | `gemini-review` is the D-C failover for Claude-authored diffs, blocking under the identical bar; invariant #3 restated | C-HE-17 |
| D7 (2026-08-18) | K5–K8 carry the corpus dispositions; P9(c) in as K1's siting rule; P9(a) forward item | C-HE-35 |
| D8 (2026-08-18) | HE-1 P1–P4 are normative in v1; council adjudicates at spec review; P1 supersedes R-19 | C-HE-06, C-HE-07, C-HE-09 |

---

# Part A — Coordination (ADR-HE-1)

## C-HE-01 - Lane model: build parallel, land serial

### Contract

1. Lanes MUST build concurrently in isolated git worktrees, each with its own gates and reviewers, and MUST land through exactly one merge door, one arc at a time (L-1; `two-lane/SKILL.md:8` **[V]**: *"Two arcs can be \*built\* concurrently. They cannot be \*landed\* concurrently"*). **Carrier surface (clearance fold G5, C1 ruling).** This contract's carrier surface is `.claude/skills/{two-lane,ship-pr,merge-gate,roadmap-continue}` and the shared `tools/`/`tools/hooks/*` primitives they invoke (§0.1). Codex-exec-driven lanes (`.agents/skills/two-lane/SKILL.md:13` — one `codex exec --profile arhugula-implementer` leg per lane, standing concurrency cap **2** on the reference machine, `AGENTS.md:32` **[V]**) are a distinct carrier governed by `AGENTS.md`'s Orchestrator + Implementer Pattern and are **OUT of scope for C-HE-06/07 merge-door enforcement in v1**: `permission-guard.sh` is a Claude Code `PreToolUse` hook with no jurisdiction over a `codex exec` process, and `tools/merge_door.py`/`safe-merge.sh` are not wired into `.agents/skills/ship-pr/SKILL.md:96` (which issues `gh pr merge` directly **[V]**). If an operator runs a Claude-driven lane and a Codex-driven lane concurrently, this clause's "exactly one merge door" invariant does NOT hold — a known, named residual (§11), surfaced at runtime by C-HE-06 §10's cross-carrier `NOTIFY`. C-HE-08's server-side protection (carrier-agnostic) still bounds the adversarial threat for Codex-exec merges; it does not close this coordination residual.
2. N is a dial. Nothing in Parts A–D is N=4-specific: every item is either N ≥ 2 (reservation, drain guards, Docker isolation, merge lease) or live at N=1 today (verdict validity, review wrapper, unfenced push). After the correctness floor (§6 Phase 0) lands, raising N requires no further gate. The N dial and the `AGENTS.md:32` Codex cap of 2 govern two disjoint pools under two authorities; they compose only as reference-machine resource pressure (worktrees, CPU, Docker ports — C-HE-11), never as one coordination domain.
3. Coordination MUST NOT use a daemon, spawner, coordinator process, or merge-queue lock (L-2). Depth-1 is enforced by the merge-door lease (C-HE-06), **not** by drift detection alone (R-8: `ROADMAP_STATUS_DRIFT` fires against already-landed history, rolls nothing back, blocks no merge — `codex_context_guard.py:774-781` **[V]**).
4. Throughput claims MUST be stated as "well under N×; merges serialize; trailing lanes re-gate on head change" and MUST carry the qualifier "prior, not measurement" until AC#10 (C-HE-28) produces a baseline.

### Invariants

- The merge lane's `§12.2.1` fixed point is preserved: a terminating refresh PR touches only `.harness/roadmap_status.md`; other files are never folded into it (`roadmap_status_refresh.py` enforces one-file shape — v1 AC#4 **[C]**).
- The pilot bar (`two-lane/SKILL.md:140-142` **[V]**) gates **follow-on lane orchestration** (automation of lane spawning) only. It does not gate running N lanes manually (v2 §1) and it does not gate D-A's Layer 2 (§12 O1-resolution).

### Verification

- Documentation witness: `two-lane/SKILL.md` and `roadmap-continue/SKILL.md` state the model at N ≥ 2 without an N=2 literal cap.

## C-HE-02 - Coordination primitive family

### Contract

1. All cross-lane coordination state MUST be established by filesystem CAS: atomic exclusive create (`publish_exclusive`, `arc_metrics.py:516` **[V]**, or `os.link` onto a fresh name) and atomic rename (`os.replace`). No `flock`/`fcntl` locks (zero occurrences at HEAD **[V]**; introducing one is a mechanism-family change into a deliberately lock-free file — R-6, C-HE-14).
2. Every coordination file MUST live `QUEUE_DIR`-adjacent (shared, outside `REPO`) and MUST NOT live under `REPO` — the natural per-worktree placement re-creates X3 split-brain (v1 item 5 rule; R-22).
3. No exclusive gate MAY be held across an unbounded network call. Where a network call must occur while a coordination hold exists (C-HE-06 steps (iv), (vii), (viii)), the call MUST carry a bounded timeout and the hold MUST be reconciled by ground truth on timeout, never blind-retried or blind-released (R-27(c)).
4. Ownership stamps MUST be written in the same atomic operation that creates the claim (`_claim_arc` doctrine, `arc_metrics.py:602-610` **[V]**). A claim MUST never exist unstamped.
5. Unknown ownership MUST be treated as live, never dead (`arc_metrics.py:586-588` **[V]**).
6. Take-over of a dead owner's claim uses a **liveness-predicate compare** (pid + host via `_process_is_alive`/`_claim_owner_is_dead`, `arc_metrics.py:541-548,584-600` **[V]**) — not a generation token (C9-F9 correction). Mutual exclusion is already provided by the second `publish_exclusive` both takeover racers fall through to; the E5/E9 hazard at `:624-626` **[V]** is the read-liveness-then-unlink-by-path window whose consequence is capture **loss**, closed by C-HE-04 §4/§5. **Accepted residual:** OS pid reuse can yield a false "still held" verdict; it fails toward stall (reclaim delayed), never toward duplicate claim.

### Invariants

- `rg -c 'flock|fcntl' tools/arc_metrics.py tools/merge_door.py tools/reservations.py` → 0 at every future HEAD, or a superseding `ADR-HE-N` exists. (Scoped to the lane-coordination modules: seven pre-existing `tools/hooks/**` lock users — `capture-failure.sh`, `subagent-validate.sh`, `loop-gc.sh`, `lib.sh` and their tests **[V]** — are unrelated to lane coordination and are allowlisted by name; Codex C3-01 correction.)
- Every coordination path is derived from `QUEUE_DIR` (or an explicitly `QUEUE_DIR`-adjacent env override), never from `REPO`.

### Verification

- Static: grep witness above, wired into `tools/test_arc_metrics.py`.
- Unit: two simulated dead-owner takeovers on one claim; exactly one wins the second `publish_exclusive`; the loser yields; the E9 window is exercised by C-HE-04's interleaving (iii)/(vi) (**mutation-probe**: revert C-HE-04 §4's re-publish → the capture is lost).

## C-HE-03 - Arc reservation (three-state, PR-tagged, generation-versioned)

Fixes X4 (duplicate append across PR-merge latency with zero temporal overlap — `committed_arc_ids()`, the per-worktree `local` read, and `append()`'s guard all pass, v1 §4 **[C]**; ADR-HE-1 §2). *Clearance fold G1/G2/G6/G12/G14 (2026-08-18): the state-encoded-filename + `os.replace` design was replaced after Codex C1-01 showed a payload-only `os.replace` can recreate `open` beside `merged`; the `pending`-aged silent reclaim was removed after Codex C1-02 / ADV-F1 showed it contradicted the TTL invariant.*

### Contract

1. **Location and record shape — generation-versioned, no rename, no replace.** One reservation per `arc_id` at `QUEUE_DIR/reservations/<arc_id>/<gen>.json` (`gen` = 1, 2, 3 …; UTF-8 JSON, one object). Each file is an **immutable full snapshot** (never a delta) created by exclusive create (`publish_exclusive`, `arc_metrics.py:516` **[V]**). The current record is the highest `gen`. **Every mutation — state change or payload-only update — is one CAS:** read the current gen `n` and its payload → build the complete new payload → exclusive-create `<n+1>.json`. `FileExistsError` = lost the CAS: the writer MUST re-read the new head, **re-validate that its intended transition is still legal from the head's `state` per §4**, and only then retry (bounded, ≤ 8) — a now-illegal transition (e.g. `open→abandoned` against a head that reads `merged`) MUST RAISE, never re-apply a stale payload. There is no `os.rename`/`os.replace` on reservation records at all. Terminal history is retained by construction; GC prunes gens strictly below the head that are older than terminal + 30 d, and sweeps orphaned `.<gen>.<pid>.tmp` files (a writer that crashed between `publish_exclusive`'s temp-write and its `os.link`, `arc_metrics.py:516-534` **[V]**). Never in `_claim`, whose lifetime ends when `_claim_arc` returns. `reservation_id ≡ arc_id`.
2. **States.** `pending → open → terminal{merged | abandoned}`. `superseded_by: <arc_id>` is MANDATORY on `abandoned`. Chain resolution walks reservation-to-reservation by `arc_id`; readers detect a repeated `arc_id` immediately and RAISE (cycles are representable but invalid); depth cap **5** is a second guard (R-7).
3. **Payload (full snapshot).** `{arc_id, generation, prev_generation, state, lane_id, branch, pr: <int|null>, head_sha: <sha|null>, base_sha: <sha|null>, attested_merge_tree: <oid|null>, arc_type: <inventing|applying|null>, arc_type_declared_at: <open|close|null>, reserved_at, transitioned_at, seq, superseded_by: <arc_id|null>, concurrent_lanes_at_open: <int|null>, phases: {<phase>: {start, end}}}` plus a nested provenance block `{"_provenance": {"pid", "host", "reachable_from_state_machine": false}}`. `pid`/`host` MUST NOT be read by any state-machine decision (D2 — the reservation spans an hours-long handoff; liveness and validity are decoupled), **with one named exception**: §6's dead-claim recovery transfer. `pr`, `head_sha`, `base_sha` are back-filled by ship-pr at PR creation / final gate; `attested_merge_tree` at final-gate time (C-HE-06 step ii); `arc_type` is the **open-time capture point** (C-HE-26) and joins into the arc row via `arc_id`; `phases` accrete here during the open window (C-HE-27) and fold into the arc row at drain. Timestamps ISO-8601 UTC. `lane_id` = `<host-short>-<worktree-basename>-<8-hex-random>` minted at lane init and exported as `HARNESS_LANE_ID`; `lane_id`, `producer`, `reviewer_identity`, `deterministic_check_id` MUST NOT contain `:` (the `finding_id`/`code` delimiter, C-HE-24).
   **`seq` allocation.** Filesystem-derived monotonic counter: `QUEUE_DIR/reservations/.seq/<n>` created by exclusive create; the allocator reads the current max, attempts `n+1`, retries on `FileExistsError` (≤ 64, then RAISE). Never `date`-sourced (`loop_now()` is second-precision, `loop_lib.sh:44` **[V]**; R-14).
4. **Transitions.** `(none)→pending` at **arc open** — the instant a lane selects the roadmap unit (`roadmap-continue`), before any work; a `pending` or `open` reservation for the same unit MUST make a second lane's selection fail (selection-time reservation; duplicate *scheduling* is prevented here, duplicate *append* by §6). This is NOT the existing `arc_metrics.py queue` artifact (which records capture inputs at arc **closure** and already requires `--arc-type` there **[V]**) — the reservation is a new open-time record; the term "queue entry" in this spec always means the closure-time `queue`/`.taken` files. `pending→open` at drain start (C-HE-04 §2: the flip precedes `append()`; holder = the draining lane's `lane_id`) — and, on the merge lane, BEFORE door acquisition (C-HE-06 §1/§7: acquisition verifies an `open` holder, so the landing flow — ship-pr's final gate or the land driver — performs the flip pre-acquire; drain-start remains the opener for the closure-capture/bootstrap path); `open→merged` on **confirmed** merge (`gh pr view <pr> --json state,mergedAt` = MERGED); `open→abandoned` on **confirmed** abandonment (PR CLOSED with a superseding pointer, or an operator `RESOLVED-HIL` row naming the arc). Every transition is a §1 CAS.
5. **Staleness by ground truth — HITL, never TTL.** `open` + `gh` says MERGED → `merged`; CLOSED with pointer → `abandoned`. `open` + stuck (> 24 h since last transition, PR still OPEN or `pr` null) → **`NOTIFY` row + HITL escalation (C-HE-20), state unchanged**. `pending` + aged (> 24 h since `reserved_at`) → **`NOTIFY` + HITL, state unchanged**; `pending→abandoned` occurs only by an operator `RESOLVED-HIL` row or by a superseding arc's reservation naming it in `superseded_by`. A `gh` transient failure MUST fail safe to "still open, not reclaimable". **No tier reclaims on elapsed time** (D8; ADR-HE-1 O3's acceptance test).
6. **Holder rule and release.** Only the lane whose `lane_id` holds the `open` reservation MAY `append()` the arc's row (C-HE-04 §2). A queue entry MUST NOT be released before its ledger row is in committed history on `MERGED_REF` (`arc_metrics.py:79` **[V]**); a lane MUST NOT re-append an `arc_id` whose reservation is `open` (held by another lane) or `merged` — with one carve-out: the merged HOLDER's own FIRST capture is admissible (the §4 door flip precedes the closure drain, so the holder's normal capture arrives at a `merged` head; "re"-append means a second row, and the ledger's committed-history duplicate guard forecloses those) — regardless of its own per-worktree ledger. **Named D2 exception — dead-claim recovery transfer:** `_recover_dead_claims()`'s existing pid+host liveness check (`arc_metrics.py:663-667` **[V]**), on restoring a dead owner's `.taken`, is authorized to transfer the reservation's holder (`lane_id`) to the recovering lane by a §1 CAS in the same recovery step. This is seconds-scale claim liveness — the same fact as the lease's (R-27(a)) — not the hours-scale handoff D2 protects; the mutation-probe for AC#2(a)(ii) asserts the transfer.
7. **Sensor.** `concurrent_lanes_at_open: int` = count of sibling `open` reservations observed at this arc's `pending→open` flip (a best-effort snapshot; `derived`, never `declared` — D7/M8). Optional `concurrent_lanes_min`/`_max` ints MAY be accreted; they are never the cohort key (C-HE-28).
8. **Ordering key.** Every reservation emission carries the filesystem-derived `seq` (§3); `reserved_at`/`transitioned_at` are advisory.

### Invariants

- For every `arc_id`, exactly one head gen exists at any instant; at most one non-terminal head; at most one row for that `arc_id` ever reaches merged history (AC#2).
- No reservation mutation occurs by rename, replace, or read-modify-write of an existing file; only exclusive create of the next gen.
- No path reclaims or transitions a reservation on TTL expiry — any tier (verified: no TTL-reclaim path exists at HEAD **[V]** — only `capture-failure.sh`'s 10 s lock and `loop-gc.sh`'s 7-day row prune, neither touching reservations).
- `superseded_by` cycles are detected on first repeat and RAISE.

### Verification

- **AC#2(b) cross-latency** (**mutation-probe**, sequential): A drains and restores pending merge; B drains the same `QUEUE_DIR` while A's row is unmerged; B MUST NOT re-append; reservation → `merged` on confirmed merge, → `abandoned` on confirmed abandonment. RED against unfixed HEAD with no fault injection (fresh `tmp_path` has no `origin/main`, so `committed_arc_ids()` returns `set()` through the real path — v1 §6).
- CAS unit: two writers read gen n with different intended transitions (`open→merged`, `open→abandoned`); the loser re-validates and RAISES; head stays `merged` (**mutation-probe**: revert re-validation → head becomes `abandoned`).
- Chain-walk unit: 5-hop resolves; 6-hop raises; 2-node cycle raises on first repeat.
- Ground-truth unit: `gh` mocked to raise → `open`, not reclaimable; MERGED → `merged`, no second append; aged `pending` → `NOTIFY` row emitted, state unchanged (**mutation-probe**: add a reclaim-on-age → red).
- Selection unit: second lane selecting a unit with a `pending`/`open` reservation → refused.
- GC unit: orphaned `.tmp` swept; head never pruned; slow reader holding gen n−1 while n is created still reads a complete snapshot.

## C-HE-04 - Drain fault isolation and capture durability

Fixes X5 as corrected by Codex D1 / R-5 (the failure is an uncaught `FileNotFoundError` that aborts the **whole** `drain()` and abandons every other pending entry — not a false `KEPT QUEUED` print) and the E9/E21 loss path. *Clearance fold G6 (2026-08-18): flip-before-append, holder-only append, dead-claim holder transfer, teardown guard, local-row reconciliation, sixth interleaving.*

### Contract

1. The three check-then-act `os.replace` sites — `_recover_dead_claims()` `:666`, `drain()` `:746` and `:754` (**[V]**) — MUST be guarded with the file's own idiom (`except FileNotFoundError:` … log-and-yield, `arc_metrics.py:633-638` **[V]**). The losing racer logs and yields; it MUST NOT propagate.
2. **Order and holder rule.** At drain, for each claimed entry: (i) flip the reservation `pending→open` with holder = this `lane_id` (C-HE-03 §4, a §1 CAS); (ii) `append()` — which MUST refuse unless this lane is the reservation's `open` holder, or its `merged` holder appending the arc's first row (the door flip precedes the closure drain — C-HE-03 §4/§6); (iii) restore/hold the queue entry. A lane killed after (ii) therefore cannot be silently superseded by a second appender: B sees `open` held by A → not appendable; A's `open` + no PR + dead claim → the recovery path in §4, never auto-abandonment.
3. **Fault isolation.** `drain()` MUST isolate faults per arc: an exception while processing one queue entry — **including inside `_claim_arc`** (`:718-756` **[V]**: today only `append(extract(args))` is isolated) — MUST NOT abandon the remaining pending entries. A **systemic** `OSError` class (queue-dir permission / I/O) MUST be distinguished from a per-arc content fault: on the first systemic fault the invocation aborts the remaining loop with one clear message rather than re-logging the identical failure per entry.
4. **Capture durability (E9/E21) and dead-claim recovery.** A drain that has appended a row to a not-yet-committed per-worktree ledger MUST NOT return with the arc's queue entry absent: if the held entry (`taken` or `path`) has vanished when the drain goes to restore it, the drain MUST re-publish the queue entry from the in-memory capture via `publish_exclusive` before returning (`arc_metrics.py:749-756` intent **[V]**). When `_recover_dead_claims()` restores a dead owner's `.taken`, it MUST in the same step transfer the reservation holder to the recovering lane (C-HE-03 §6 — the named D2 exception), so the recovering lane's `append()` is authorized. A lane dead between the merge-lane §2(i) flip and its first append leaves a `merged` headless capture no peer can transfer (`transfer_holder` is open-only by design): the entry holds loudly to the C-HE-03 §5 HITL escalation — fail-toward-stall, never auto-transfer.
5. **Local-row reconciliation at drain start.** Before processing entries, a lane MUST scan its own per-worktree ledger for uncommitted rows whose `arc_id` reservation is held by another lane or is `merged` by another lane's row. A superseded row whose replacement is in committed history MUST converge to the committed canonical line; a merged-by-other row with NO committed replacement MUST be KEPT LOUDLY pending reconciliation (merged state alone does not prove the replacement row exists — dropping could discard the only capture). The committed-history read is the local `MERGED_REF` snapshot, so its freshness is bounded by the operator's fetch cadence. This closes the "orphaned local row rides along in the next PR" path (ADV-F6) before `SPLIT_BRAIN_LEDGER` would catch it at CI.
6. **Teardown contract.** `tools/hooks/safe-worktree-remove.sh` (the existing mutex-backed wrapper **[V]**) MUST refuse to dispose a worktree whose `.harness/arc-metrics.jsonl` (tracked **[V]**) has uncommitted changes (`hook_worktree_local_state`, `lib.sh:483-497` **[V]**, already catches this) **or** committed-but-unpushed commits (`git -C <wt> rev-list @{u}..HEAD` non-empty — not checked today **[V]**). Worktree disposal MUST NOT be able to lose a capture silently.
7. On the `AbortError` branch (nothing appended), the restore at `:746` MUST succeed or re-publish; `KEPT QUEUED` and the `kept` increment MUST only occur after the entry is durably back in the queue.

### Invariants

- After any drain invocation, for every `arc_id` that was pending at entry, exactly one of: (a) the queue entry is still in `QUEUE_DIR` (row not yet in committed history — including the appended-but-uncommitted case, whose entry MUST remain), or (b) its row is in committed history on `MERGED_REF` and the entry has been released. There is no third state.
- No `FileNotFoundError` escapes `drain()`.
- At most one lane holds an `open` reservation for an `arc_id`; only that lane's `append()` succeeds.

### Verification

- **AC#2(a) same-instant** (**mutation-probe**): `subprocess.Popen` per lane, each with its own git-inited `tmp_path` worktree and its own `ARC_METRICS_REPO`/`ARC_METRICS_LEDGER` (C-HE-05), shared `QUEUE_DIR`, filesystem rendezvous barrier (a `.go` file both lanes poll for, **bounded 30 s** → explicit "rendezvous timeout — peer leg did not reach the barrier" failure, never a hang); parametrized interleavings: (i) both lanes claim the same fresh entry; (ii) both judge the same dead `.taken` recoverable and take over — assert the reservation holder transfers to the recoverer and exactly one row lands; (iii) A appends while B removes A's `.taken` (E9); (iv) A restores (`:754`) while B claims; (v) A hits `AbortError` and restores (`:746`) while B claims; **(vi) A is killed between `append()` and the restore line** via `ARC_METRICS_TEST_KILL_AFTER=append` (`arc_metrics.py` checks the env var and `os._exit(137)`s immediately after the named step) — assert recovery transfers the holder, B's row lands, and A's resumed drain keeps its orphaned local row LOUDLY until B's canonical row reaches committed history, then converges it to the committed line and releases the entry (§5). Assert over the **union** of lane ledgers: one row per `arc_id`, and the invariant above. **NOT** in-process threads (module-level globals cannot diverge per thread — a false-GREEN certificate, C8) and **NOT** `multiprocessing` fork.
- Fault-isolation unit: entry 1 raises inside `_claim_arc`; entries 2..n still processed; systemic `PermissionError` on `QUEUE_DIR` → one abort message, no per-entry repeats.
- E9 witness (**mutation-probe**): remove the winner's `.taken` between append and restore; assert re-publish; revert the fix → entry absent.
- Teardown unit: `safe-worktree-remove.sh` refuses on uncommitted ledger change; refuses on `rev-list @{u}..HEAD` non-empty (**mutation-probe**: drop the ahead check → committed-unpushed worktree is removed).

## C-HE-05 - Per-process `REPO` / `LEDGER` overrides

### Contract

1. `arc_metrics.py` MUST honor `ARC_METRICS_REPO` and `ARC_METRICS_LEDGER` env overrides mirroring the existing `ARC_METRICS_QUEUE_DIR` (`:59-63`) and `ARC_METRICS_MERGED_REF` (`:79`) pattern **[V]**. Today `REPO`/`LEDGER` are bare module-level assignments (`:44-45` **[V]**).
2. This item MUST land **before** AC#2 probe (a) can go GREEN and before the reviewer-concurrency probe (R-13, R-29 — the dangling prerequisite no build item owned).
3. Env-override is the preferred construction for **both** AC#2 probes (R-24); the `tools/test_arc_metrics.py:174-187` monkeypatch-`run` idiom (**[V]**) remains valid only as a cheaper fallback for single-branch assertions.

### Invariants

- Production defaults are unchanged when the variables are unset.

### Verification

- Unit: two subprocesses with different `ARC_METRICS_REPO` observe different `LEDGER` paths and the same `QUEUE_DIR`.

## C-HE-06 - Merge-door lease

The correctness fence for landing (moved from Phase 2 to Phase 0 by R-10; Codex D3). Closes the **cooperative** TOCTOU; the adversarial one is closed by C-HE-08. *Clearance fold G3/G4/G7/G8 (2026-08-18): lease token + transition marker (Codex C1-03, C9 poison-pill), lease held through post-merge CI and the terminating refresh as a continuation (Codex C1-04, C10/C9 deadlock), bounded waits, `blocked` state + unblock recipe, yield-point / primitive rate limit / gate rows.*

### Contract

1. **Acquire before construct.** ship-pr MUST acquire and verify the lease **before it constructs** the `gh pr merge` command string (R-19's relocation into the calling code) — and, per D8/P1, the ordering is additionally enforced structurally by C-HE-07.
2. **Primitive.** Single global lease at `QUEUE_DIR/merge-door/LEASE` (UTF-8 JSON; inside the shared `QUEUE_DIR`, hence outside `REPO`), acquired by atomic exclusive create (`publish_exclusive`); **fail-fast, one attempt, caller decides retry** (D3, R-9). The primitive additionally refuses more than **K = 5** acquire attempts per `lane_id` per 60 s (`cause_attribution: lease_acquire_rate_exceeded`); such refusals MUST NOT decrement the caller's §8 budget.
3. **Payload.** `{lease_token (128-bit random hex), lane_id, reservation_id (≡ arc_id), pr, head_sha, base_sha, acquired_at, pid, host, merge_attempted_at: <iso|null>, state: <held|blocked>, blocked_at_sha: <sha|null>, blocked_reason: <str|null>}`. `pr` is REQUIRED (reclaim runs in a different process against a single global lease and cannot get `N` from memory — F-R2-03); `head_sha`/`base_sha` are REQUIRED so a reconcile pass can confirm the PR's current head/base still match before any tree comparison or merge (Codex C2-04); `pid`/`host` are load-bearing here (D2/R-27(a): one continuous seconds-long operation); `reservation_id` links the two state machines (P2).
4. **Steps.** (i) acquire; (ii) confirm `gh pr view <pr> --json headRefOid,baseRefOid` equals the recorded `head_sha`/`base_sha` (mismatch → release via §6 and re-gate), then `local-base-cas-check`: `git merge-tree --write-tree origin/main <head_sha>` (git ≥ 2.38; 2.39.5 at HEAD **[V]**) and compare the tree OID with `attested_merge_tree` recorded in the reservation (C-HE-03 §3) — byte-equal or fail the door (R-23); (iii) write `merge_attempted_at` (a payload CAS: temp + `os.link` onto a token-named sidecar `LEASE.<token>.attempted`, so a crash cannot leave the marker half-written) **before** invoking `gh pr merge` (R-28); (iv) invoke the **existing** `gh pr merge <pr> --squash --match-head-commit <head_sha>` with a **bounded 120 s timeout on this call only** (P4; not a global `run()` timeout — `run()` at `:134-146` passes no `timeout=` **[V]**); (v) confirm by `gh pr view <pr> --json state,mergedAt`; (vi) flip the reservation to `merged` (C-HE-03); (vii) **hold the lease** through the merge SHA's own post-merge `main` run — bounded **45 min** — until it is `success` (C-HE-19); (viii) drive the terminating refresh PR **as a continuation under the same held lease — no re-acquire** (the same lane/process lands both merges sequentially; this is the §12.2.1 "merge → terminating refresh → next" door), bounded **45 min** for its run to be `success`; (ix) release via §6. Failure or timeout at (vii)/(viii) → the lease transitions to `state: blocked` (payload CAS) with `blocked_at_sha`/`blocked_reason`, a `NOTIFY` + HITL escalation fires, and the door stays closed until §6's unblock recipe.
   **CI concurrency.** `.github/workflows/ci.yml:43-45` **[V]** keys the concurrency group by `github.ref` with `cancel-in-progress: true`; every push to `main` shares one group, so lane B's landing would cancel lane A's post-merge run and A could never satisfy (vii). The group MUST key by SHA for `main` pushes (`ci-${{ github.workflow }}-${{ github.ref == 'refs/heads/main' && github.sha || github.ref }}`); PR-event semantics are unchanged. **Stated tradeoff:** this disables cancel-in-progress for all `main`-push runs; under an N-lane cadence full runs can queue concurrently — a `NOTIFY` fires when > 2 `main`-push runs are in progress.
5. **Timeout / crash reconciliation.** On timeout or on restart with a lease whose `merge_attempted_at` is set: query ground truth. MERGED → continue from (vi), **never re-issue the merge**; OPEN → GitHub is authoritative that no merge occurred (a PR merges at most once server-side; `--match-head-commit` rejects a stale head), so restart from step (ii) and re-issue step (iv) once per reconcile pass. Never blind-retry, never blind-release (R-27(c), R-28). GitHub's per-PR merge serialization is the sole backstop for the sub-case where two self-resumes of one crashed lane both reach (iv) — §6 fences that path via the marker, and this backstop is stated so it is not assumed absent.
6. **Release, reclaim, self-resume — all through one transition marker.** Every release-or-reclaim of a lease MUST first win the exclusive create of `QUEUE_DIR/merge-door/transition.<lease_token>` (one marker per token, ever); the marker payload carries `{pid, host, target_action ∈ {release, reclaim, unblock}, created_at}`. Only the marker winner may `os.rename(LEASE, released.<token>)` (holder release) or `os.rename(LEASE, reclaimed.<token>)` and create a fresh `LEASE` with a new token (reclaimer). A holder that loses the marker MUST stop driving the merge and reconcile via ground truth. **Reclaim is two-step:** pid dead ⇒ reclaimable in principle; step 2 (mandatory) is §5's ground truth (R-27(b)). **Poison-pill guard:** a third party observing a marker whose creator pid is dead MAY complete the declared `target_action` idempotently (`os.rename` on an already-moved source fails closed with `FileNotFoundError` = already done). **Self-resume** (same `lane_id`, new pid, after a crash) MUST go through the reclaim path (win the marker for the old token, mint a new token) — it is neither a bare release nor an unfenced continuation. **Unblock:** `state: blocked` is cleared only by `just merge-door-unblock <pr>` — an operator-confirmed reclaim through this same marker CAS keyed to `blocked_at_sha`, never a path-only unlink. Reclaim transfers merge-driving authority for `pr`; it MUST NOT transfer reservation ownership (P2). Markers and `released.*`/`reclaimed.*` history are GC'd with the lease history (30 d).
7. **Lease-holder invariant (P2).** The lease MAY be ACQUIRED only by an arc whose reservation is `open` and held by the acquiring lane; from step (vi) the reservation legitimately reads `merged` while the lease is held through the (vii)–(ix) continuation (*v1.4 X4a — the pre-v1.4 "held only while open" wording contradicted §4's own lifecycle*). Acquisition MUST verify the reservation state; a mismatch fails the acquire.
8. **Caller policy (reconciles D3 with E43 #13).** *Yield:* acquire-fail MUST yield control to the caller's next natural gate-pass event — a control-flow return, not a sleep-and-retry inside the acquire call. *Numbers:* a lane that must wait waits with bounded exponential backoff + full jitter: base 30 s, factor 2, cap 10 min per wait, at most 12 attempts (≈ 1 h) before routing to the HITL queue as `HITL-recoverable` (`cause_attribution: lease_acquire_budget_exhausted` — an explicit exception to the default `transient-retry → permanent-fail-exit` fallthrough, because a wedged lease is human-actionable). Rate-limit refusals (§2) do not count against the 12. The *primitive* stays fail-fast; arbitration never moves into it. Worst-case legitimate hold (§4: 120 s + 45 min + 45 min ≈ 92 min) exceeds the 12-attempt budget by design: a sibling that exhausts its budget while the holder is legitimately in (vii)/(viii) receives a `NOTIFY` naming the holder's stage, not a fault.
9. **Gate contracts (R-22, extended).**

| gate | kind | input | output | fail-class | cause_attribution |
|---|---|---|---|---|---|
| `merge-door-lease-acquire` | deterministic filesystem CAS | lease path | pass (create won) / fail (held) | `transient-retry` | `lease_contended` |
| `merge-door-lease-acquire` (rate refusal) | deterministic | attempt log | fail | `transient-retry` | `lease_acquire_rate_exceeded` |
| §8 budget exhaustion | deterministic | attempt count | HITL | `HITL-recoverable` | `lease_acquire_budget_exhausted` |
| `merge-door-reconcile` | hybrid (ground-truth query + one bounded re-invocation) | lease payload + `pr` | MERGED / re-issue-then-recheck / exhausted | `permanent-fail-exit` on exhaustion | `merge_reissue_exhausted` |
| `merge-door-post-merge-ci` | deterministic (poll, bounded) | merge SHA | success / blocked | `HITL-recoverable` | `post_merge_ci_not_green` |

10. **Pending-attestation tiering (R-21, Phase 1 item 13b).** Each lease acquire/release during the ≥ 3 pilot merges and the first **N = 3** production multi-lane merges emits a **`NOTIFY`** row (C-HE-09) — non-blocking; graduate to silent after **3 clean cycles**, where a clean cycle = acquire → MERGED confirmed → post-merge green → refresh green → release with no HITL escalation and no reconcile pass. **Cross-carrier notice (G5):** if `git worktree list` shows a `.codex-worktrees/`-rooted worktree at acquire time, a `NOTIFY` names the C-HE-01 §1 residual (a Codex-exec lane may reach `gh pr merge` unfenced).

### Invariants

- Once ground truth has returned MERGED for a `pr`, `gh pr merge` is never invoked again for it (negative assertion; **mutation-probe** target). The only permitted re-issue is §5's OPEN branch, at most once per reconcile pass.
- No lease exists without `pr`, `head_sha`, `reservation_id`, `lease_token`; no lease is ACQUIRED whose reservation is not `open` and held by the acquiring lane (§7 P2 — enforced at acquisition; from step (vi) the reservation legitimately reads `merged` while the lease is held through the (vii)–(ix) continuation).
- `merge_attempted_at` is set before the first byte of the merge request leaves the process.
- No release, reclaim, unblock, or self-resume touches `LEASE` without first winning `transition.<token>`; no path-only unlink of `LEASE` exists.
- The lease is never released while the merge SHA's own `main` run or the terminating refresh is unconfirmed.

### Verification

- **AC#2(c) crash-resume** (**mutation-probe**; `subprocess.Popen` + env plumbing; `MERGE_DOOR_TEST_KILL_AFTER=<step>` makes `merge_door.py` `os._exit(137)` immediately after the named step): kill after `merge_attempted_at` write and before merge → restart (self-resume via marker) sees OPEN → exactly one merge call; kill after merge success and before release → restart sees MERGED → continues to (vii), merge mock call-log length == 1; kill after release, before the refresh PR → refresh proceeds under a fresh cycle. Plus: kill after (vi) and before (vii)/(viii) → lease held, restart resumes the CI wait.
- Marker unit: holder release vs reclaimer race → exactly one wins the marker; the loser observes and yields; a marker whose creator pid is dead is completed by a third party (**mutation-probe**: remove third-party completion → door permanently locked after a reclaimer crash).
- Timeout unit: `gh pr merge` mock hangs past 120 s (clock injected) → reconcile; ground truth MERGED → call log 1; OPEN → exactly one re-issue (2) then MERGED.
- In-flight unit (`test_merge_door.py::test_inflight_first_attempt_then_reissue`): mock models a delayed first landing; assert exactly one MERGED outcome and no error path proceeds past (v).
- Continuation unit: refresh PR merge under the same lease — no second acquire call recorded (**mutation-probe**: force a re-acquire → deadlock/timeout observed).
- Post-merge CI unit: mocked run `cancelled`/`failure`/timeout at (vii) → `state: blocked`, `NOTIFY` emitted, `merge-door-unblock` clears via marker; a raw unlink attempt is not offered by any recipe.
- Rate-limit unit: 6 acquires in 60 s from one `lane_id` → 6th refused with `lease_acquire_rate_exceeded`; caller budget counter unchanged.
- Lease-holder unit: reservation `pending` → acquire fails; `open` → succeeds. Contention unit: two acquirers, one succeeds, the other returns fail immediately (no sleep in the primitive).

## C-HE-07 - Merge-door enforcement site (P1, supersedes R-19) [R: D8]

### Contract

1. Lease-before-merge ordering MUST be enforced by an **allowlisted wrapper**, not by prose: `tools/hooks/safe-merge.sh` performs C-HE-06 steps (i)–(ix) and is the only merge verb the guard auto-allows in loop mode. **Exact arity (C10-F1):** the guard's matcher MUST accept exactly `bash tools/hooks/safe-merge.sh <pr-number>` (PR number all-digits, no other token — mirroring `_safe_worktree_remove_wrapper`'s `$# -eq 2` check `:184-191` **[V]**), and `safe-merge.sh` MUST NOT accept or forward any flag beyond the PR number; its internal invocation is exactly the fixed string in C-HE-06 §4(iv). Reference matcher (C10, folded verbatim):
   ```bash
   _safe_merge_wrapper() {
     local cmd="$1"
     printf '%s' "$cmd" | grep -q '[;&|<>`\\()]' && return 1
     [[ "$cmd" == *$'\n'* ]] && return 1
     printf '%s' "$cmd" | grep -Eq '(~|\.\.|\$\{?[A-Za-z_])' && return 1
     set -f; set -- $cmd; set +f
     if [ "${1:-}" = "bash" ]; then shift; fi
     [ "$#" -eq 2 ] && [ "$1" = "tools/hooks/safe-merge.sh" ] || return 1
     case "$2" in ''|*[!0-9]*) return 1 ;; esac
     return 0
   }
   ```
2. `tools/hooks/permission-guard.sh` MUST deny raw `gh pr merge` in the loop-mode deny block (`:314-340` **[V]**, which precedes the `:427` allow alternation **[V]**) as an explicit `emit_deny` (`(^|[[:space:]])gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$)` → `emit_deny "raw gh pr merge — must go through tools/hooks/safe-merge.sh"`), and MUST allow only the wrapper, alongside the existing `_safe_worktree_remove_wrapper` allow at `:288-290` **[V]** (wrapper allow → `emit_allow` exits before the deny block; the deny block exits before `:427` — composition verified by C10). This copies the in-repo idiom already used for the safe-worktree-removal path (raw verb denied `:57-65`, wrapper-only allowed `:184-191` **[V]**).
3. `tools/hooks/test_permission_guard.sh:167-169` and `:328-329` (**[V]**, currently asserting `gh pr merge → allow`) MUST be inverted to assert deny-raw / allow-wrapper.
4. Autonomous merging is preserved: the wrapper is auto-allowed, so R-19's real concern (bare removal "would break the entire autonomous-merge arc loop mode exists to enable") is met.

**Supersession note.** R-19 rejected *removing `gh pr merge` from the allowlist* and relocated the obligation into ship-pr's calling code. Its premise — that permission-guard "is not a workflow-ordering engine" — is false at HEAD: the guard already performs deny-raw-verb / allow-only-wrapper ordering for worktree removal. C-HE-07 keeps R-19's relocation (C-HE-06 §1) **and** adds the structural fence. The convened council (D4) adjudicates this supersession; if rejected, C-HE-06 §1 stands alone and this contract is struck in v1.1.

### Invariants

- In loop mode, no path other than `tools/hooks/safe-merge.sh` can reach `gh pr merge` without an operator prompt.
- `--admin` merges stay denied (`permission-guard.sh:397` **[V]**).

### Verification

- Guard tests: raw `gh pr merge N --squash` → deny (loop mode); `bash tools/hooks/safe-merge.sh N` → allow; wrapper with shell metacharacters → not matched (falls to ask), mirroring `_safe_worktree_remove_wrapper`'s hardening (`:186-189` **[V]**).

## C-HE-08 - Unfenced direct-push path (X9) [R: D5]

X9 is live at N=1 today: `main` is `protected: false` with rulesets `[]` **[V, re-probed 2026-08-18]**; the `:427` allow alternation contains bare `push` with no destination-branch predicate **[V]**; the deny block catches only `--force`/`-f`/`--mirror`/`--prune`/`--delete`/`:`-refspec deletes (`:321-329` **[V]**); no executable `pre-push` hook exists **[C]**.

### Contract

1. **Client-side.** Any push whose refspec or upstream targets `main` (`main`, `HEAD:main`, `refs/heads/main`, or a bare `git push` while `main` is checked out) MUST be denied in loop mode — implemented as **explicit `emit_deny` entries in the §2 deny-list block** (`:314-340`), alongside the sibling force-push/mirror/branch-delete denies (`:321-329` **[V]**), **not** as a removal from the `:427` allow regex: `emit_deny` calls `loop_log DENY` (`:271-272` **[V]**) whereas the allow-regex fall-through is the silent, unaudited "ask" path (`:431-432` **[V]**) — X9's audit trail must not be weaker than force-push's (C10-F2). Reference predicates (C10, folded verbatim): `^[[:space:]]*git[[:space:]]+push([[:space:]]+[^[:space:]]+)?[[:space:]]+([^[:space:]]*:)?(refs/heads/)?main([[:space:]]|$)` → deny; and a bare `git push` (`^[[:space:]]*git[[:space:]]+push([[:space:]]+[^[:space:]-][^[:space:]]*)?[[:space:]]*$`) while `git symbolic-ref --short -q HEAD` = `main` → deny. Pushes to topic branches fall through both and remain auto-allowed at `:427`.
2. **Server-side.** `main` MUST be branch-protected with exactly: `required_pull_request_reviews: null` (the loop is autonomous — review authority is the gate chain, not GitHub approvals), `required_status_checks: {strict: true, contexts: [<the CI job names marked "— blocking" in .github/workflows/ci.yml, workflow "CI">]}` (at HEAD: `pytest (all axis packages) — blocking`, `ruff (lint + format) — blocking`, `pyright (strict) — blocking`, `substitution ledger (tally gate) — blocking`, `CLAUDE.md citations (I-1 resolution gate) — blocking`, `arc ledger (tally gate) — blocking`, `semantic overlay (drift gate) — blocking`, `tools/ test coverage guard + codex-loop tests — blocking`, `Q1 review gate (structured artifact) — blocking`, `Q3 evidence + closure gate — blocking`, `Codex context guard (anti-rot gate) — blocking`, `clearance corpus (frontmatter gate) — blocking` **[V]**; the plan re-derives the list from the workflow at build time), `enforce_admins: true`, `allow_force_pushes: false`, `allow_deletions: false`, `required_linear_history: false` (squash merges keep it linear anyway). **Recipes (C11-F1; `CLAUDE.md` §12.4.1 — the operator executes nothing manually):** `just main-protection-{show,apply,rollback,tiebreaker,verify}`. `apply` embeds the JSON payload, re-derives the "— blocking" context list from `ci.yml`, prints one before/after diff, and is run by Claude **outside loop mode** (the guard denies `gh api -X` in loop mode, `permission-guard.sh:396` **[V]**); the operator's role is one AskUserQuestion — "Apply branch protection to `main` now? [diff shown]". `rollback` = `gh api -X DELETE …/protection` with the pre-change `show` output (404 today) recorded in the plan's evidence log. `enforce_admins:true` does not block the loop's terminating-refresh merge (it goes through `gh pr merge` under the held lease, C-HE-06 §4(viii)).
3. The settings change is outward-facing and lands as an operator-gated build item (the plan owns the recipes; the operator answers the gate). Nothing legitimate is blocked: every real landing path already goes through `gh pr merge` and ship-pr hard-aborts unless `state=MERGED` (`ship-pr/SKILL.md:190-191` **[V]**).
4. **Tiebreaker before enforcing (HE-1 O4; C10-T8).** `just main-protection-tiebreaker` runs one `gh pr merge --squash --match-head-commit` against a scratch PR under `strict: true` **and** asserts that a refresh PR branched from a since-superseded `main` either fast-forwards cleanly or is caught pre-merge — the load-bearing parameter — not merely that some refresh run succeeds once.
5. **`main-protection-verify` (Codex C1-07, ADV-F5)** is a **read-only phase0 manifest row** (§8.1): it queries `gh api repos/{owner}/{repo}/branches/main/protection` and exact-compares every required setting and status context against §2; 404/unprotected/mismatch → RED. **Runs in: local** (session `gh` auth) — CI's default `GITHUB_TOKEN` is `contents: read` (`ci.yml:47-48` **[V]**) and lacks the scope; auth-absent/insufficient routes to the §8.1 skip reason `gh-auth-absent`, which `lanes-phase0-check` counts as RED (C-HE-13 §1). This is what makes the server fence observable by the mechanical pilot gate rather than an implicit precondition.

### Invariants

- No auto-approved tool call in loop mode can place content on `main` without a PR.
- Protection is independent of any bug in C-HE-06/C-HE-07 (R-20).

### Verification

- Guard tests: `git push origin HEAD:main` → deny; `git push origin feature` → allow; `git push` on `main` checkout → deny.
- Live probe (operator-gated): the scratch-PR tiebreaker in §4, recorded in the plan's evidence log.

## C-HE-09 - `loop_status.md` venue, row shape, reduction, and marker scoping (P3, X6) [R: D8]

*Clearance fold G13 (2026-08-18): option (b) for ACTIVATE, structured column BEFORE detail (C7 verified the trailing-column rejoin defect), pointer sweep, `NOTIFY` and `COALESCE-DELIVERED` row kinds.*

### Contract

1. `loop_status.md` remains a **single file** (P3). A `loop_status.d/<lane-id>-<seq>.md` fragment split is REJECTED: `loop_log()` writes one line via a single `>>` (`loop_lib.sh:77-85` **[V]**, an atomic `O_APPEND` under `PIPE_BUF`) and the AWK reducers key on `$3` (kind) and the detail's leading token only, never the `$2` timestamp (`:149-156` **[V]**) — so concurrent writers are already correctly serialized by physical append order; a split would forfeit that and manufacture the ordering hazard a monotonic `seq` would then be needed to repair (R-16).
2. **Venue determinism (X6, E10).** The file that carries `DEFERRED-HIL` / `RESOLVED-HIL` / `NOTIFY` / `COALESCE-DELIVERED` rows MUST resolve to one path for every lane and every caller (raw shell and hook alike). Today `loop_status_path()` (`loop_lib.sh:24` **[V]** — it already exists and is dual-sourced) resolves through `hook_project_dir()` = `${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}` (`lib.sh:18-22` **[V]**), i.e. per-worktree. Its body MUST return the shared venue `QUEUE_DIR/../loop_status.md` (default `~/.gstack/projects/arhugula-v2/loop_status.md`, overridable by `HARNESS_LOOP_STATUS_PATH`); **control markers** (`ACTIVATE`, `DEACTIVATE`, `.loop-active`, run-scoped state) stay per-lane under `hook_project_dir()`. **Pointer sweep (acceptance):** every literal `.harness/loop_status.md` citation MUST be updated — enumerated at HEAD: `loop_lib.sh:6,231`, `.claude/skills/loop-start/SKILL.md:16,34`, `.claude/skills/loop-stop/SKILL.md:23`, `.claude/skills/resolve/SKILL.md:15`, `.claude/skills/ship-pr/SKILL.md:309` **[V]** — a grep for the literal with zero hits outside test fixtures is the check.
3. **Row shape.** Rows a lane emits to the shared venue carry a **structured column inserted BEFORE detail**: `| ts | kind | lane=<lane_id>;cause=<cause_signature|-> | <detail…> |` (the structured token contains no `|` and no whitespace). Legacy 3-column rows are detected by `$4` not matching `^lane=`. Rationale (C7, verified by `awk` repro): `_loop_pending_hil_rows()` (`loop_lib.sh:175-186` **[V]**) rejoins `s=$4; for(i=5;i<NF;i++) s=s"|"$i` to restore escaped-pipe splits, so any column appended AFTER detail is glued into the rendered reason text — this supersedes C-HE-10's earlier "fifth column" wording. Reducers key the item token as the first whitespace token of detail (`$5` for structured rows, `$4` for legacy). `loop_pending_hil_summary()` and `loop_cap_list()` MUST render `[<lane_id>]` in every emitted item.
4. **ACTIVATE scoping — option (b).** `ACTIVATE` stays a per-lane control marker and **MUST NOT reset globally-visible HIL rows**; the "SINCE the last ACTIVATE" reduction (`loop_lib.sh:127-129,151` **[V]**) is struck for HIL rows. Skip-set = all pending HIL rows across lanes (over-skipping is safe; under-skipping re-loops). `RESOLVED-HIL` remains the only way a deferral leaves the skip-set.
5. **New row kinds.** `NOTIFY` — append-only informational (structured column + detail); rendered at SessionStart **beside**, never merged into, the DEFERRED-HIL summary; **excluded** from `loop_skip_set()` (`:134-157` **[V]**); used by C-HE-06 §10 tiering, C-HE-03 §5 aged reservations, C-HE-11 RAM shortfall, C-HE-31 §4 demotion, C-HE-06 §4 CI queue depth. `COALESCE-DELIVERED` — append-only delivery record `| ts | COALESCE-DELIVERED | lane=<lane_id>;cause=<cause_signature> | <generation-id> |` (C-HE-10). Existing kinds (`ACTIVATE / DEACTIVATE / DEFERRED-HIL / RESOLVED-HIL / COMPLETED / DENY / RESOLVE-SPLIT / RESUME`, `loop_lib.sh:73-74` **[V]**) are unchanged.
6. Aggregation of per-lane rows is not needed under this design (E28 moot); if any cross-lane reduction step is ever added it MUST piggyback on the already-serial merge lane, never be independently schedulable.

### Invariants

- Two lanes deferring the same item in the same second produce a well-defined order (physical append order); the reducer's result is order-correct, never wrong (R-16).
- A lane's `ACTIVATE` never hides another lane's open deferral.
- A `NOTIFY` row never enters the skip-set.

### Verification

- Reducer unit: rows `[L1 DEFERRED x] [L2 ACTIVATE] …` → `x` still pending (**mutation-probe**: restore the ACTIVATE reset → `x` dropped).
- Row-shape unit: structured row with `cause=merge-door-lease-acquire:transient-retry:lease_contended` renders detail without a stray `|`; legacy row still parses (**mutation-probe**: move the structured column after detail → rendered detail corrupted).
- Venue unit: raw-shell and hook contexts in two worktrees resolve the HIL file to one path; pointer-sweep grep → 0 hits outside tests.
- `NOTIFY` unit: a `NOTIFY` row is rendered and absent from `loop_skip_set()`.

## C-HE-10 - Gate coalescing across lanes (v2 item 8, E25)

### Contract

1. `loop_pending_hil_summary()` / `loop_cap_list()` (`loop_lib.sh:165, 191-225` **[V]**) MUST gain a `cause_signature` second reduction key so that when ≥ 2 lanes need the operator in one window, the operator receives **one batched prompt** grouped by cause, never N sequential ones (`CLAUDE.md` §12.4.1's batched-not-drip-fed rule applied at N ≥ 2). `cause_signature` = `<gate_id>:<fail_class>:<cause_attribution>` — the same namespaced triple C-HE-24 §3 uses for `Finding.code` — carried in the **structured column before detail** defined at C-HE-09 §3 (`lane=<lane_id>;cause=<cause_signature>`; a trailing column would be glued into the rendered detail by `_loop_pending_hil_rows()`'s rejoin — C7 verified); legacy rows without it reduce as their own singleton group.
2. Coalescing is additive group-by, not arbitration: nothing wins, everything is kept; a same-second collision yields an oddly-ordered-but-correct prompt. **Delivery is pull-based (Codex C2-05):** lanes only append `DEFERRED-HIL` rows and never prompt; the SessionStart / merge-lane path emits a group only once `first_seen + window` has elapsed, appends a `COALESCE-DELIVERED` row (C-HE-09 §5) naming `(cause_signature, generation-id)`, and treats rows already covered by a `COALESCE-DELIVERED` row at/after their `first_seen` as delivered — so two SessionStart paths cannot both prompt for one group.
3. Window: minutes-scale, **default 10 min** (configurable in the 5–15 min band via `HARNESS_HIL_COALESCE_WINDOW_S`), bounded above by the 24h TTL (C-HE-20). A 1 s or 10 s window would systematically under-collapse (R-16 window ruling).
4. Item 14 (reviewer-concurrency probe, C-HE-22) and coalescing are complementary, not substitutive; both land before pilots; their mutual order is not load-bearing.

### Verification

- Unit: two deferrals with equal `cause_signature` within the window → one group; differing signatures → two groups; same signature outside the window → two groups.

## C-HE-11 - Environment isolation per lane (X7, R-17, R-18)

### Contract

1. **Docker.** Every lane that brings up `deploy/self-hosted-local/compose.yaml` MUST pass a per-lane `-p <project>` and MUST remap the **full** host collision set: ports **{3000, 3200, 4317, 4318}** (`compose.yaml:12,24-25,41-42` **[V]**) **and** the fixed project name (`compose.yaml:1` = `arhugula-r420-self-hosted-local` **[V]**), which governs the container/network/**volume** namespace. `justfile:471,475,479` currently pass no `-p` **[V]** and MUST be parameterized: project name `arhugula-r420-self-hosted-local-lane<k>`; host ports for lane `k ≥ 1` = **`30000 + 100·k + {0,1,2,3}`** (grafana, tempo, otel-grpc, otel-http), lane 0 keeps today's ports, `k` validated `< 350` (Codex C1-05: the earlier `base + 100·k` formula collided at k=2 — 3000+200 = lane 0's 3200). `k` comes from `HARNESS_LANE_INDEX`, allocated at lane init by exclusive create of `QUEUE_DIR/lanes/<k>` (released at lane teardown). Codex-exec legs have no `HARNESS_LANE_INDEX` — same residual and forward row as C-HE-01 §1.
2. **git gc.** `gc.auto 0` MUST be set **repo-wide, once, idempotently** by whichever lane-init runs first. Per-lane framing is dropped: `extensions.worktreeConfig` is UNSET **[V, re-probed]**, so there is no per-lane `git config` write (R-17). Detached `gc` is live on git 2.39.5 **[V]** (`gc.autoDetach` predates 2.47).
3. **git ref-lock contention.** Local ref/index lock collisions MUST be retried with bounded backoff + full jitter: `{base 100 ms, factor 2, cap 5 s, max_attempts 8}`; exhaustion fails the git operation and emits a `NOTIFY` (never routes to the merge-door budget). This is a local-git retry, distinct from the merge-door lease (C-HE-06 §2 stays fail-fast) — E43/B4 reconciled.
4. Per-lane `UV_CACHE_DIR` is NOT required (uv documents cache concurrency safety — v1 §10).
5. **Reference-machine headroom (C11-F6).** The operator's machine is an Intel i5 / 16 GB Mac; each stack is three containers (`compose.yaml:1-49` **[V]**). Lane-init MUST probe available memory / Docker-VM headroom before bringing up a stack at `HARNESS_LANE_INDEX ≥ 2` on a machine below an operator-configured RAM floor (default 32 GB); on shortfall it MUST emit a `NOTIFY` naming the constraint and skip the stack (the lane still builds; observability rows mark `stack=absent`) rather than let `docker compose up` fail opaquely mid-pilot. Such a failure MUST NOT be recorded under a `merge-door-`/`reservation-` cause_signature (it is environmental, not coordination-caused — C-HE-13 §3).

### Verification

- justfile recipe test: two lanes bring the stack up with distinct `-p`; `docker compose ps` shows disjoint container/network/volume names and no port bind conflict (Docker-daemon-gated; skip-marked otherwise).
- Config unit: lane-init run twice → one `gc.auto=0` write, second is a no-op.

## C-HE-12 - Detections that emit, not just gate (v2 item 9, E43, R-2, R-3)

### Contract

1. Every Phase-0 fix in this Part MUST pair with a **finding-row emission** on the C-HE-24 record, not only a pass/fail gate. Detection count today: **1 of the 19 named hazards** (`ROADMAP_STATUS_DRIFT`, `codex_context_guard.py:774-781` **[V]**, JSON-emitted `:928-960` **[V]**); the target after this item is ≥ 4/19 (R-2) — concretely hazards #1 split-brain, #4 stale reservation, #6 refresh collision, #7 base TOCTOU of the §9 table each have an emitting code.
2. New codes: `SPLIT_BRAIN_LEDGER` (CI backstop on every merge to `main`: over `record_kind=arc` rows only — `jq -r 'select(.record_kind=="arc") | .arc_id' .harness/arc-metrics.jsonl | sort | uniq -d` MUST be empty; the ledger carries only arc rows, one per `arc_id`, C-HE-25), `ORPHANED_RESERVATION` (an `open` head gen whose PR is MERGED/CLOSED without a terminal transition, or a `blocked` lease older than its bound), `BASE_TOCTOU` (after `gh pr merge`, the merge commit's **first parent** MUST equal the base SHA the merge door verified — a mismatch is positive proof the race window was hit and MUST trigger re-validation, never silent acceptance), plus a **lane-discriminating field** so new codes do not inherit the drift check's lane-attribution gap (R-3).
3. Emission target follows C-HE-24: the 8-field record with the `Finding` 3-field projection for the CI surface.

### Verification

- CI job: split-brain check runs on every push to `main`; injected duplicate `arc_id` fixture → job red, finding emitted with `lane_id`.
- Unit: first-parent mismatch fixture → `BASE_TOCTOU` finding.

## C-HE-13 - Pilot gate, probes, and scope enforcement (Phase 1)

### Contract

1. **Mechanical pilot gate.** The pilot runner MUST refuse to start until Phase 0 (§6 S1–S4) is verifiably closed — a deterministic check, not prose ordering ("an implicit precondition is not a gate", C10): `just lanes-phase0-check` runs the §8.1 manifest rows tagged `phase0` and exits 0 only if every one passes at the current HEAD (skip-marked rows count as **not passed** for this gate); the runner invokes it and aborts on non-zero. A pilot against unfixed state produces contaminated friction signal.
2. **Order inside Phase 1** (R-10, R-11, C-HE-22): item 14 reviewer-concurrency probe → coalescing (C-HE-10) → item 13 pilots. O1 (the instrumented 4-worktree `hook_project_dir()` probe) runs **after** the X6 fix (C-HE-09), on a Phase-0-fixed substrate — probing pre-fix measures a known-broken baseline (R-11).
3. **≥ 3 manual pilot runs at 3–4 lanes** with zero new **Phase-2 automation** machinery (not "zero new machinery" — Phase 0 is real work, v2 §4.1). Two distinct gates, stated to avoid the AC#1 ambiguity: **Phase 0 (S1–S4) gates running N ≥ 2 lanes at all** — the pilots are simply the *first* N-lane runs and therefore also sit behind it (§1 above); the **≥ 3 pilots gate only follow-on orchestration** (`two-lane/SKILL.md:140-142`), never the right to keep running N lanes manually (v2 §1) — resolving v1 §9 decision 3 and STAGE7 F2-04. **A pilot run counts as successful** iff every lane's arc lands through the merge door (reservation `merged`, first-parent detection clean), the union ledger satisfies the C-HE-03/04 invariants, and no HITL escalation carries a `cause_signature` prefixed `merge-door-` or `reservation-` (coordination-caused); `just lanes-pilot-report <pilot-run-id>` computes this iff-clause across the three stores and prints PASS/FAIL plus the friction rows (C11-F5). "Recurring" friction (the organic-pain bar) = a `cause_signature` appearing in ≥ 2 of the ≥ 3 pilots, OR one occurrence the operator rates independently severe (C8-F8; at n=3 a 40%-incidence source registers twice with P ≈ 0.35, so the single-severe clause is load-bearing).
4. **O3 + prospective check (R-12).** Keep O3 (`git merge-tree --write-tree` over the 172 historical colliding pairs → real textual-conflict rate vs the 38.7% upper bound; report semantic-conflict rate as **unmeasured, not zero**) as a Phase-1 base-rate prior, **and** add the prospective merge-tree check on the actual chosen lane set — `tools/arc_disjoint_check.py` (U-WT-07), named in `two-lane/SKILL.md:19` **[V]** as deliberately unbuilt and absent at HEAD **[V]**.
5. **Scope is a hint, not a gate (E17).** `two-lane/SKILL.md` instructs picking arcs whose `scope.files` do not overlap, but the forward register carries **zero** such keys across 186 rows **[V]**. Declared scope MUST be treated as a non-authoritative scheduling hint; enforcement MUST be actual-write based: before a lane opens an arc, `arc_disjoint_check.py` computes `git merge-tree --write-tree` of the candidate head against every other lane's current head (from the `open` reservations' `branch`) and refuses selection on a non-empty conflict set; at landing, the `BASE_TOCTOU` first-parent detection in C-HE-12 catches what selection-time could not.

### Verification

- Pilot-runner unit: any Phase-0 verification RED → runner exits non-zero with the failing item named.
- `arc_disjoint_check.py` unit: two lane heads with a textual conflict → non-empty conflict set; disjoint → empty.

## C-HE-14 - Rejected and blocked mechanisms (normative "do not build")

| Mechanism | Disposition | Reason |
|---|---|---|
| Full-lifetime `flock` across drain | **Rejected** (R-6) | Two remote calls inside the proposed window (`gh_pr` `:284`, `ci_metrics` `:376` **[C]**); auto-releases on death; mechanism-family change |
| Daemon / coordinator / spawner / merge-queue lock | **Foreclosed** (L-2) | D3 fail-fast exists so no one builds daemon-shaped arbitration unnamed |
| Local base CAS via raw `PATCH /git/refs` (item 20) | **Blocked, stays blocked** | Squash/ancestry: auto-close never fires and ship-pr aborts on non-`MERGED`; **and** trust boundary: a raw ref PATCH is content-blind (C10). Only the read-only `local-base-cas-check` survives (C-HE-06 step ii) |
| Integration-lens gate (item 21) | **Blocked** until its contract survives review; when built it MUST route through `just codex-review` on the **merge-tree diff**, not another Claude subagent (v1 AC#6) |
| `loop_status.d/` fragment split | **Rejected** (P3, R-16) | C-HE-09 |
| Post-hoc first-parent assertion **instead of** the lease | **Rejected** as a fence (R-8); **kept as a detection** (C-HE-12) | Detect-after-landing |
| A third durable store for landing state | **Rejected** (L-5, D-B) | `merge_attempted_at` folds into the lease |
| sqlite as the durable record | **Rejected** (L-5) | New DB+WAL surface, no correctness gain, loses git-diffability |
| `merge=union` | **Rejected** | git concedes arbitrary line order; `.gitattributes` ties LF forcing to hash-chain determinism |
| Optimistic stale-base merge (D1(c)) | **Rejected** by every reviewer | Abandons combination testing |
| Removing `gh pr merge` from the allowlist **without** a wrapper | **Rejected** (R-19) | Superseded by C-HE-07 |

---

# Part B — Review gate and completion semantics (ADR-HE-2; BUILD-PLAN Arc 1)

## C-HE-15 - Verdict validity

Closes X1 / loop-D1 (an absent verdict reads as clean: zero-byte output ~3× in one session; PR #1386's log frozen at 313 bytes for 130 s after process exit with the real verdict — 4 findings, 1 P1 — only in `~/.codex/sessions/`; recurred live during the review pipeline that catalogued it **[C]**).

### Contract

1. A verdict COUNTS only if the channel's output parses to that channel's **declared schema**. **Exit code is never a completion signal** (both CLIs exit 0 on total failure — measured **[C]**).
2. Missing, empty, truncated, malformed, or ambiguous output MUST resolve to `REVIEWER_UNAVAILABLE` (C-HE-16 §3) — BLOCK-equivalent, never APPROVE-able. Re-reading the log is NOT a substitute for a positive parse (PR #1386 disproof).
3. Every verdict MUST be bound to immutable code state: `{head_sha, base_sha, diff_digest, reviewer_identity, prompt_version, config_hash}` (STAGE3 P5; feeds C-HE-25). A verdict for a different `head_sha` MUST NOT be reused (R1 #4/#8/#13: three fresh final lens reviews on the exact bound head; merge pinned `--match-head-commit`; a re-attestation is never counted as an execution).
4. Every channel in the mandatory chain (`codex-review`, `merge-gate` lenses, `gemini-review` on failover) MUST declare its output schema as a JSON Schema file at `tools/review_schemas/<channel>.schema.json` — required: `verdict ∈ {APPROVE, BLOCK}`, `findings: [{severity ∈ {P1, P2, P3}, location, message}]` with `additionalProperties: false` on items (the merge-gate finding convention — distinct from `codex_context_guard.Finding.severity`'s `{hard, warn, info}`, a comment-only annotation at `:115` gated by `== "hard"` at `:1050` **[V]**, which is the C-HE-24 §3 projection layer), and **all six binding fields of §3** (`head_sha, base_sha, diff_digest, reviewer_identity, prompt_version, config_hash` — Codex C1-06: a schema requiring only `head_sha` accepts a verdict reusable after `main` advances). The wrapper MUST independently compute the expected value of each binding field for the invocation and byte-compare before accepting; schema validity alone is insufficient. The parse MUST be performed by the fail-closed wrapper (C-HE-18), not by the calling skill's prose; an out-of-enum `severity` → `REVIEWER_UNAVAILABLE`. For channels whose CLI emits prose, the wrapper extracts the fenced JSON block the channel prompt requires and validates it against the schema; no fenced block → `REVIEWER_UNAVAILABLE`.

### Invariants

- No path maps "no output" or "exit 0" to APPROVE (`merge-gate/SKILL.md:127` *"Parsing — fail closed"* **[V]**; `ship-pr/SKILL.md:199` **[V]** — invariant #5 is live-carried).
- A verdict row without `head_sha` is unrepresentable.

### Verification

- Wrapper unit per channel: empty stdout + exit 0 → `REVIEWER_UNAVAILABLE`; truncated JSON → `REVIEWER_UNAVAILABLE`; auth-error text + exit 0 → `REVIEWER_UNAVAILABLE(permanent)`; well-formed → parsed verdict (**mutation-probe**: revert to exit-code keying → empty output reads APPROVE).

## C-HE-16 - Failure classification and terminal states

### Contract

1. Reviewer failures MUST be classified **permanent** (auth/login/subscription errors, missing binary, unsupported version) vs **transient** (timeout, rate-limit, network, empty output on a first attempt).
2. Permanent failures MUST skip the retry budget entirely (retrying an auth failure burns budget on a certainty — G2). Transient failures consume the bounded budget.
3. Terminal states of a review invocation are exactly `{APPROVE, BLOCK, REVIEWER_UNAVAILABLE}`. `REVIEWER_UNAVAILABLE` is its own state (G3), BLOCK-equivalent for merge purposes, and MUST record `{permanent|transient, reason, channel}`; for any C-HE-24 row it produces, `permanent` → `fail_class: permanent-fail-exit`, `transient` → `fail_class: transient-retry` (C5-F6).
   **Retry parameters (C9-F4; C5 falsified the "reuse `remaining_review_timeout`" premise — `agy_review.py:461-463,508,556` **[V]** is a single-pass budget decrementer with no retry loop):** `{per_attempt_timeout: cap 1200 s, max_attempts: 2, backoff_base_ms: 0, backoff_cap_ms: 0, total_budget_s: 1260}` — `total_budget_s` reuses `TOTAL_REVIEW_TIMEOUT_SECONDS` (`agy_review.py:22` **[V]**) as a shared deadline; every attempt's actual timeout is `min(1200, remaining − margin)` computed dynamically (margin 0 s on attempt 1, 30 s on attempt 2 — a static 600 s × 2 left ~5% margin on a shared clock — `[[wall-clock-budget-assertions-breach-under-load]]`) — *v1.2 X2 correction: v1/v1.1 read `per_attempt_timeout: 550 s` and `min(550, remaining − 30 s)` on attempt 2, a budget-arithmetic figure the codex channel measurably exceeds (both S1 live attempts killed mid-review at 550 s; U-HE-01 rounds ≈590 s); the cap is now the 1200 s the gemini channel already applied per invocation, so a retry exists only after a FAST transient failure; see the v1.2 change-note.*; no inter-attempt backoff (a retry is one bounded re-invocation on `transient`, not a polling loop); exhaustion → `HITL-recoverable`, not `permanent-fail-exit` (a wedged reviewer login is human-fixable). The loop lives in `tools/review_wrapper_common.py`.
4. The transient/permanent classifier is per CLI and MUST be maintained as an explicit table in code — a module-level mapping in the shared wrapper module `tools/review_wrapper_common.py`, one entry per `(channel, regex, class)`, unit-tested row by row (it will drift with vendor error text — HE-2 §5 accepts this as the likeliest future defect surface). Initial table: `codex`: `/requires a newer version of Codex/` → permanent; `/not logged in|login|unauthorized|401|403/i` → permanent; `/command not found/` → permanent; `/rate limit|429|timed out|ETIMEDOUT|ECONNRESET/i` → transient; empty stdout on first attempt → transient, on second → `REVIEWER_UNAVAILABLE(transient)`. `gemini` (`agy_review.py`): `/antigravity .* not (installed|logged in)|unauthorized/i` → permanent; `/RESOURCE_EXHAUSTED|429|deadline/i` → transient. Unknown text → transient (fail-safe toward retry-then-block, never toward APPROVE).

### Invariants

- No terminal state is inferred from absence.
- A `REVIEWER_UNAVAILABLE(permanent)` never triggers a retry of the same channel in the same arc; it triggers failover (C-HE-17) or block.

### Verification

- Classifier table test: each known error string → class; unknown string → transient (fail-safe toward retry-then-block, never toward APPROVE).

## C-HE-17 - Failover per D-C [R: D-C, D6]

### Contract

1. On primary channel failure (`codex-review` → `REVIEWER_UNAVAILABLE`), the loop MUST invoke the second cross-vendor reviewer — **`just gemini-review`** (`justfile:607-608` → `tools/agy_review.py --base <ref>` **[V]**) — under the **identical** validity check (C-HE-15/16), no relaxed bar; then BLOCK if it also fails.
2. The failover channel's verdict is **blocking** when it runs as failover (D-C's "block if it also fails" makes the fallback the gate; D6).
3. **Applies to Claude-authored diffs.** R1 invariant **#3** ("Codex-authored work receives OAuth out-of-family (Gemini/Antigravity) review") is prose, not code — `agy_review.py` accepts only `--base` (`:612` **[V]**) and has no authorship logic **[V]**. #3 is **restated**, not silently outgrown: *out-of-family review covers Codex-authored work as before, AND serves as the D-C failover for Claude-authored diffs at the identical bar.*
4. Because a failover is only as good as its wrapper, `gemini-review` MUST already satisfy C-HE-18's fail-closed contract (it is the hardened reference implementation) and its silent-death modes (`REVIEW-gemini-FAILED-first-attempt.log` **[C]**) MUST be covered by the same schema parse.
5. AC#6 (decorrelation not weakened) closes when both channels carry gate contracts (v2 AC#6 was `[O]` because `codex-review` had none).

### Invariants

- No relaxed path exists: the fallback verdict is parsed by the same wrapper family and the same schema-shape rule.
- Decorrelation is strengthened, not traded (`merge-gate/SKILL.md:12-17` **[V]**: lenses are lens-decorrelated, not vendor-decorrelated; the cross-vendor check is what D-C hardens).

### Verification

- Integration: primary mocked `REVIEWER_UNAVAILABLE(permanent)` → failover invoked once → its BLOCK blocks; its `REVIEWER_UNAVAILABLE` → arc blocked with both reasons logged; its APPROVE → proceeds (with both rows in the record).

## C-HE-18 - Fail-closed wrapper for `codex-review` (X8; G7)

### Contract

1. `tools/codex_review.py` MUST exist (absent at HEAD **[V]**) and MUST mirror `tools/agy_review.py`'s hardening: bounded timeout, exit-code-independent output capture, declared schema parse, permanent/transient classification, and a `REVIEWER_UNAVAILABLE` terminal on any parse failure. `just codex-review` MUST route through it.
2. The wrapper MUST read the channel's own session artifact when the CLI's stdout/log is inconclusive (the PR #1386 mode): discovery = the newest file under `~/.codex/sessions/` modified after the wrapper's own start timestamp whose content contains the invocation's `head_sha`; if none within 130 s of process exit (the measured PR #1386 lag) → `REVIEWER_UNAVAILABLE(transient)`. The wrapper MUST still require a positive schema parse from whichever source it uses.
3. Zero-byte or auth-only output MUST surface as a finding row (C-HE-24, `producer=codex_review_wrapper`) so the silent-death mode becomes measurable.

### Verification

- Same wrapper unit battery as C-HE-15; plus a "log frozen, session artifact has verdict" fixture → verdict parsed from the artifact.

## C-HE-19 - CI terminal states

### Contract

1. CI outcomes are exactly `{SUCCESS, FAILURE, CANCELLED}`. **CANCELLED is INCOMPLETE, never green** (G5; R1 #14).
2. The merge door and ship-pr MUST require the merge commit's **own** post-merge run on `main` to be an exact `success` (`ship-pr/SKILL.md:199-204` **[V]**), and MUST name `CANCELLED` explicitly in the accepted-set logic rather than by whitelist omission (`CANCELLED` has zero occurrences in `ship-pr/SKILL.md` and appears in `arc_metrics.py` only as the green-timing exclusion comment at `:270-271` — never in accepted-set logic **[V, corrected]**). Under C-HE-06 §4(vii) the door itself now waits on the merge SHA's own `main` run, so a CANCELLED post-merge run blocks the door (durable `blocked` state), not merely the next ship-pr.
3. Honest framing (R-1 vs loop-D2): CI intentionally cancels superseded runs (`ci.yml:43-45` `cancel-in-progress: true` **[V]**); cancellation clusters on superseded pushes; two consumers already fail closed. G5 is a robustness improvement against a future edit that broadens the accepted set — **not** the remediation of an observed defect. `arc_metrics.py:270-277` already excludes non-`success` from green timing **[C]**.

### Verification

- Unit: conclusion `cancelled` → INCOMPLETE → merge door blocks; `success` → proceeds; empty/pending → blocks.

## C-HE-20 - Escalation and TTL

### Contract

1. A `REVIEWER_UNAVAILABLE`, a CI-INCOMPLETE on a final head, a `blocked` lease (C-HE-06 §4), or a stuck/aged reservation (`open` or `pending`, C-HE-03 §5) MUST route to the existing durable HITL queue (`DEFERRED-HIL` row via `loop_log`, C-HE-09 venue) — no new escalation store; informational-only events use the `NOTIFY` kind (C-HE-09 §5).
2. Default TTL **24 h** for a CI-blocking gate (operator may override; not separately ratified). The TTL is a **notification** threshold: on expiry the item is re-surfaced/escalated. **The TTL MUST NOT trigger reclaim, release, or any state change on a reservation (any tier) or lease** (D8; C-HE-03 §5 — the earlier `pending`-aged silent reclaim was removed in the clearance fold, G2). Verified: no TTL-reclaim path exists at HEAD **[V]**; this contract keeps it that way.

### Invariants

- The value of the TTL cannot cause data loss (it can only change when a human is pinged).

### Verification

- Unit: `open` reservation aged past TTL → HITL row emitted; reservation state unchanged (**mutation-probe**: add a reclaim-on-TTL → test red).

## C-HE-21 - Standing constraints and the live-carrier rule

### Contract

1. **No flat round cap anywhere.** Mechanization removes defect classes; it never licenses shortening review (R1 #11/#17/#20; PR #1034 produced genuine findings through round 48 of 49; round-2 P1-rate 75% > round-1 62% **[C]**).
2. Invariants are binding **by independent live carriage, not by source**: #5 binds (live at `merge-gate/SKILL.md:127`, `ship-pr/SKILL.md:199` **[V]**); #14 binds (C-HE-19); **#16 is void** (`U-WT-09` 0 matches **[V]**; no concurrent-reviewer cap carrier in `.claude/`, `tools/`, `justfile`, `CLAUDE.md` — only a lens name at `merge-gate/SKILL.md:81` and a council co-primary cap at `c2-context-engineering/SKILL.md:218` **[C]**). Any future appeal to a numbered invariant MUST cite its live carrier.
3. #19: no workflow optimization becomes permanent merely because an evaluator emits GO. #4/#8/#13 as C-HE-15 §3.
4. Standing workspace refusal: no eval-harness / model-judge **as a governance gate**.

## C-HE-22 - Reviewer concurrency at N lanes

### Contract

1. Four lanes each running reviewers is **unconstrained by #16** (void). Whether single-identity subscription logins throttle at 2 and 4 simultaneous calls is unknown and MUST be probed (v1 item 14) **before** pilots (R-10), because throttling would surface as gate failures indistinguishable from lane-coordination pain.
2. A GREEN probe retires exactly one hypothesized cause; a shared vendor outage still trips the identical contamination — hence coalescing (C-HE-10) stays required (R-16).

### Verification

- The probe itself (C8-F7): **≥ 5 repetitions** at each of {1 (baseline), 2, 4} concurrent `codex-review`/`gemini-review` invocations against a fixed diff — the workspace's own instrument documents ~5× round-to-round wall-clock variance (`arc_metrics.py:780-793` `fmt_span` **[V]**), so one trial cannot separate throttling from noise; record verdict validity (C-HE-15) and wall-clock per call as C-HE-24 rows. **GREEN iff** the median per-call wall-clock at N ≤ 2× the N=1 median **and** zero validity failures across all trials; either violation ⇒ RED, throttling assumed present, pilots do not start.

---

# Part C — Record and measurement substrate (ADR-HE-3; BUILD-PLAN Arcs 2, 3, 7)

## C-HE-23 - Extend, do not replace [R: D-B]

### Contract

1. No new **authority**: no new hash-chained findings ledger (the dropped L0.2 artifact). The two live records — `.harness/arc-metrics.jsonl` (18 rows **[V]**) and `.harness/merge-gate-log.md` (≥ 121 entries **[V]**) — are extended in place; JSONL stays the durable format (L-5).
2. `merge-gate-log.md` gains a **structured sibling** `.harness/merge-gate-log.jsonl` emitting the same field set (C-HE-24), so gate verdicts become machine-readable; the markdown log remains the human view. The sibling is a **machine projection of the same fact written by the same producer in the same step** (the `merge-gate` skill's log-row emission), not a second authority — which is why it does not violate D-B. **Write order and failure semantics:** the JSONL row is written first (append: one `write` syscall per row on an `O_APPEND` descriptor, writers serialized by an exclusive lock on the log's own descriptor, a short write rolled back to the pre-write offset before the failure surfaces — *v1.1 X1 correction: v1 read "single `write` under `PIPE_BUF`", which a C-HE-24 row cannot satisfy (≈700 B against macOS `PC_PIPE_BUF` = 512) and which is a pipe/FIFO guarantee, not a regular-file one; see the v1.1 change-note*); the markdown row second. A failed markdown write logs a `warn` finding and leaves the JSONL row standing (the machine record is the one downstream reads); a failed JSONL write fails the gate step (BLOCK-equivalent — a verdict that cannot be recorded does not count, C-HE-15 §1). Consistency check: `just lanes-verify` includes a reducer that asserts every markdown row has a JSONL row with the same `(pr, head_sha, verdict)`, and flags a JSONL row with **neither** a markdown sibling **nor** a matching `warn` finding as its own class (a crash between the two writes — C7-F9); such orphans are reconciled by re-emitting the markdown row on the next gate run.
3. Hash-chain tamper-evidence is **dropped** with the ledger; the accepted mitigation is append-only adjudication (C-HE-24 §5).

### Invariants

- Store count grows by at most one (the structured sibling); §7's audit lists every store and its authority.

## C-HE-24 - Common finding record and its projection [R: BUILD-PLAN L0.2′ (D-A × D-B reconciliation); resolves HE-3 §6]

*Clearance fold G11 (2026-08-18): `record_kind` union across two files, envelope fields (`base_sha`, `diff_digest`, `cause_attribution`, `disposition_actor`), `:`-free identifiers, projection wording; ratified 8-field core untouched.*

### Contract

1. **Core.** Every finding-class row carries the ratified **8-field finding core**:
   `{finding_id, location, observed_evidence, expected_contract, severity, finding_type, lineage_claim, producer}` where `producer ∈ {deterministic_check_id, reviewer_identity}`. This shape is **load-bearing** (without it N6 — defined at C-HE-27 §4 — is uncomputable without a re-parsing pass) and is operator-ratified (BUILD-PLAN L0.2′) — ratification outranks the later council ruling R-25 on this corpus's authority chain. "8-field" throughout this spec names this core; the envelope below is not a schema extension of the ratified shape.
2. **Row envelope.** `{record_kind, ts, arc_id, lane_id, head_sha, base_sha, diff_digest, round_n, cause_attribution: <str|null>, disposition: <null|accepted|rejected|suppressed>, disposition_actor: <null|actor_id>, unique_catch: <null|bool>}`. `record_kind ∈ {finding, finding_adjudication, no_finding, equivalence_proof, gate_demotion, reviewer_unavailable}` for rows in `.harness/merge-gate-log.jsonl` (C-HE-23 §2); `.harness/arc-metrics.jsonl` carries **only** `record_kind=arc` rows (one per `arc_id`; C-HE-25). `disposition_actor` is populated only on adjudication rows and MUST differ from the finding's `producer` (the emitter rejects a row where they match); it is the single field for both the general self-disposition ban and C-HE-29's adjudicator identity. `producer`, `reviewer_identity`, `deterministic_check_id`, `lane_id` MUST NOT contain `:`.
3. **Projection.** `codex_context_guard.Finding` (`severity, code, message`, `codex_context_guard.py:113-117` **[V]**) is a projection of the record for the CI surface that already consumes it: `severity` ← from `finding_type`/fail-class (`terminal-`/`permanent-fail-exit` → `hard`; `transient-retry`/`Reflexion-`/`HITL-recoverable` → `warn`, R-25 mapping); `code` ← `<check>:<fail_class>:<cause_attribution>` read from the core/envelope (e.g. `merge-door-lease-acquire:transient-retry:lease_contended`); `message` ← `observed_evidence`. **Tiebreaker run:** no consumer at HEAD splits or positionally parses `code` on `:` — consumers are exact-equality (`tools/test_codex_context_guard.py:110-308`), one prefix `startswith` (`:634`), and a string render (`codex_context_guard.py:894`) **[V]** — so the namespaced extension is additive; existing codes MUST remain byte-identical.
4. **`finding_id`** (zero matches across `.py` at HEAD **[V]**) = `<producer>:<head_sha>:<location-hash>:<n>`. It is deliberately **not** stable across `head_sha` for the same underlying defect — acceptable for every consumer this spec defines (same-`head_sha` `unique_catch`, `(pr, head_sha, verdict)` join, within-`head_sha` disposition lineage); cross-`head_sha` same-defect tracking is out of scope for v1 (§11).
5. **Adjudication is append-only.** A finding row is never overwritten; a later disposition appends a `finding_adjudication` row with the same `finding_id`, a later `ts`, `disposition`, and `disposition_actor`. Readers reduce by `finding_id` → last row. The reviewer is never authoritative for `disposition` (STAGE7 L0.2 carried): disposition is set by a decorrelated lens, a deterministic rule, or a logged operator override — enforced by the `disposition_actor ≠ producer` write-time check, not by prose.
6. Every finding-class row carries `lane_id` and `arc_id` — the lane-attribution gap the drift check has today (R-2/R-3).

### Invariants

- The 8-field core is the store of truth; the 3-field projection is derived, never authored independently.
- Two rows with one `finding_id` differ only by `ts`/`record_kind`/`disposition`/`disposition_actor`/`unique_catch`, never by `location`/`observed_evidence`/`producer`.
- No adjudication row exists whose `disposition_actor` equals the finding's `producer`.

### Verification

- Schema test: both emitters validate against one JSON schema (core + envelope, `additionalProperties: false`); projection round-trip: record → `Finding` → `_json_report` unchanged for pre-existing codes (**mutation-probe**: rename an existing code → CI test red).
- Reducer unit: three rows for one `finding_id` → last-row disposition; self-disposition row (actor == producer) → rejected at write (**mutation-probe**: drop the check → accepted).
- Charset unit: a `producer` containing `:` → rejected at write.

## C-HE-25 - Ledger field extension

### Contract

`.harness/arc-metrics.jsonl` carries **only `record_kind=arc` rows, one per `arc_id`** (finding-class rows live in `.harness/merge-gate-log.jsonl`, C-HE-24 §2). Arc rows MUST gain: `record_kind`, `reviewer_identity`, `prompt_version`, `config_hash`, `arc_type_open`, `arc_type_close`, `arc_type_declared_at ∈ {open, close}` (a close-time relabel updates `arc_type_close` on the single arc row — never a second arc row, which would trip `SPLIT_BRAIN_LEDGER`, Codex C2-01), per-round terminal outcome (`{round_n: {channel, terminal ∈ {APPROVE, BLOCK, REVIEWER_UNAVAILABLE}, finding_count}}`), `head_sha`, `base_sha`, `lane_id` (zero occurrences repo-wide today **[V]**; M6 — one field now versus a migration later, on exactly the two files X3/X4 implicate), `concurrent_lanes_at_open: int` (`derived`, C-HE-03 §7; optional `concurrent_lanes_min/max`), and `phases` (C-HE-27). Absent fields on historical rows read as `null` (`read_ledger()` is bare `json.loads` with `dict.get()` consumers, `arc_metrics.py:765-775,810-832` **[V]** — additive-safe); every historical row is an implicit N=1 baseline (v2 AC#10). At HEAD `arc_type` is already populated on 6/18 rows (`inventing`), null on 12, `applying` on 0 **[V]**.

### Verification

- Schema test on the ledger; cohort split (`arc_metrics.py:812-832` **[V]**) groups by `concurrent_lanes_at_open` without error on `null`.

## C-HE-26 - Pre-register `arc_type` at arc open (Arc 2; M5)

### Contract

1. `arc_type` MUST be declared when the arc is **opened** — i.e. at the C-HE-03 §4 `pending` reservation creation by `roadmap-continue`, **not** at the existing `arc_metrics.py queue` step (which records capture inputs at arc *closure* and already requires `--arc-type` there **[V]** — C7-F2: reusing "queue entry" for the open-time artifact would wire the requirement onto the close-time verb and reproduce today's bug). The reservation payload's `arc_type` (C-HE-03 §3) is the open-time capture point; `arc_type_declared_at` records `open`. Declaring only at close (today's behavior; **zero** arcs are labeled `applying` **[V]**) is outcome-contaminated and cannot support the "discriminator is arc type, not round number" claim (E12).
2. A close-time change MUST update `arc_type_close` on the single arc row (both labels visible; never a second arc row — C-HE-25).
3. **K7 prerequisites — two gates (C8-F4).** BUILD gate: no routing-by-arc-type rule (HE-4 K7 / P8) may be prototyped until this contract has produced uncontaminated open-time labels **and** the round-log→arc mapping exceeds 3 of 18 arcs. EVALUATE gate: no routing-accuracy/precision claim may be reported until ≥ 20 uncontaminated open-labeled arcs exist with non-zero cells in both `arc_type` categories.

### Verification

- Unit: reservation created without `arc_type` → rejected at open; close-time relabel → one arc row with `arc_type_open ≠ arc_type_close`, no duplicate `arc_id`.

## C-HE-27 - Phase timing as explicit spans (Arc 3; M7)

### Contract

1. Phases `queue / execute / capture / absorb / edit / verify` MUST each be recorded as an explicit `{start, end}` pair. `result_capture` MUST record process-exit and log-write-completion **separately** (they diverge — PR #1386).
2. **Hard rule: never derive a phase duration from the gap between two records.** An intervening record can be dropped, reordered, or written by another lane; a delta silently becomes a different quantity indistinguishable from a real measurement.
3. **v1 decision:** spans are **durable**. Because the arc row is built at/after closure (no "open" event exists in `arc_metrics.py` today **[V]** — C7-F6), early-phase spans **accrete on the reservation record's `phases` map** (C-HE-03 §3, via the generation CAS) during the open window and **fold into the arc row at drain** (`append()`, after the C-HE-04 §2 flip). OTel emission is optional and derived. BUILD-PLAN listed durable-vs-telemetry as known-open; this spec closes it for v1 with the durable default. Whether a `result_capture` divergence is itself audit-worthy stays open (§10).
4. **N6 defined (C7-F8, C8-F5).** N6 "problems prevented per hour" = COUNT(DISTINCT `finding_id` whose last row has `disposition = accepted`) within the measurement window ÷ Σ(`phases.verify` + `phases.edit`) hours across the window's arcs, read from the durable `phases` map — never an inter-row delta (§2). `phases.verify` spans whose round terminated `REVIEWER_UNAVAILABLE` are excluded from the denominator (bucketed as `phases.verify_unavailable_s`) so reviewer downtime cannot deflate N6. The denominator is deliberately the same review/gate wall-clock class Part D's P1 finding measured, so N6 reads as the ROI complement to P1's cost number.

### Verification

- Static test: no reader computes `end_of_row_n − start_of_row_{n−1}` for a duration (grep witness on the metrics readers); unit: out-of-order rows still yield correct per-phase spans.

## C-HE-28 - Cohort comparison and the value AC (AC#10)

### Contract

1. Lane-count as a lever MUST be evaluated by cohort: **`concurrent_lanes_at_open` (integer)** is the cohort key (v2 §9 item 4 — not `lane_id`, not `declared`; C7-F5/Codex C2-03: the existing split keys on a hashable string, `arc_metrics.py:812-832` **[V]**, so a `{min,max}` object has no canonical key), using the existing exact-lever-set discipline (do not collapse every non-empty `levers_active` into one TREATED cohort). Once `arc_type` labels are uncontaminated (C-HE-26) the split MUST be **joint on `(concurrent_lanes_at_open, arc_type)`** — assignment to N is operator-chosen (simpler `applying` arcs are plausibly batched), the second and more likely confound (C8-F6).
2. Refresh-collision incidence (`ROADMAP_STATUS_DRIFT` findings, now lane-attributed) MUST be correlated against `concurrent_lanes_at_open` (R-15).
3. **Selection, stated as mechanism, not gesture.** `concurrent_lanes_at_open` is not randomized; a cohort delta may reflect which arcs get batched rather than a lane-count effect. AC#10 results are **correlational** unless a forward-register item adds randomized/quasi-randomized lane assignment on a controlled arc subset (§11). Behavioral endogeneity and comprehension debt further cap what any measurement can establish; a measured GO is evidence, not authorization (#19). **Honest first-months claim:** at HEAD the only populated joint cells are `(N=1, inventing)` n=6 and `(N=1, null)` n=12 **[V]**; every N ≥ 2 cell and every `applying` cell starts at 0 — descriptive counts only, no effect estimate.

### Verification

- Report unit: synthetic rows at N=1/2/4 × `arc_type` → joint cohorts, correct medians; drift-finding join by `lane_id`; the report header carries the "correlational" statement.

## C-HE-29 - Shadow trial, wired live [R: D-D; Arc 7]

*Clearance fold G15 (2026-08-18): per-round marker row, operational `unique_catch`, corrected operating characteristics with the v1 default moved to n=30 / kill-if-<2, HITL delivery for the kill/keep decision, `disposition_actor` as adjudicator identity.*

### Contract

1. The second reviewer's shadow lens runs **live, off the blocking path**, from the first Arc-7 deploy (D-D overrides "offline corpus analysis first").
2. **Rows.** Every scored round emits at least one row with `producer=<second_reviewer_identity>`: finding rows for what it caught, or exactly one `record_kind=no_finding` marker row when it caught nothing — so the scored-round denominator is `COUNT(DISTINCT round_n WHERE producer=<lens>)` from `merge-gate-log.jsonl` alone. **`unique_catch=true`** iff (a) the finding's `location`+`finding_type` appears in no row from the blocking reviewers for the same `head_sha` AND (b) its last-row `disposition = accepted`; a `unique_catch=true` row later disposed `rejected` MUST NOT count. The adjudicator's identity is `disposition_actor` (C-HE-24 §2), named as `operator` or a specific third-party reviewer identity of **neither model family** — never a placeholder.
3. **Kill rule, pre-committed, with its operating characteristics stated.** v1 default: **n = 30 scored rounds; kill if fewer than 2 unique catches.** P(kill | true per-round unique-catch rate p) for this rule: p=0 → 1.000 · 0.05 → 0.554 · 0.10 → 0.184 · 0.15 → 0.048 · 0.20 → 0.011 · 0.25 → 0.002 (direct binomial; the earlier "n=15, < 2" rule would kill a p=0.10 lens ≈ 55% of the time and is rejected; "n=30, < 3" would kill it ≈ 41% of the time — C7/C8 correction). The threshold and n are recorded in the trial's config row so a later amendment is auditable; BUILD-PLAN leaves the kill condition "operator to accept or amend" — C8's SPRT alternative (H0 p≈0.02 vs H1 p≈0.15, stated α/β) is recorded at §11 as the plan's permitted alternative. **Wall-clock is NOT a kill criterion** for a lens off the critical path.
4. **Decision delivery.** At round n the kill/keep evaluation fires as an escalation-kind HITL request presenting the n rounds' `unique_catch` dispositions and the threshold; responses ∈ {approve-kill, reject-keep, amend-threshold}; if the operator is the per-round adjudicator, sessions persist as HITL rows with `kind='shadow-trial-adjudicate'`.
5. Adoption of the lens into the blocking chain is not self-authorizing (#19).

### Invariants

- The kill/keep decision is reproducible from `merge-gate-log.jsonl` rows alone.
- No `unique_catch=true` counts unless its last disposition is `accepted`.

### Verification

- Reducer unit over 30 synthetic rounds (marker rows included) → decision reproducible; fixture with a `unique_catch=true` row later `rejected` → excluded from the count (**mutation-probe**: count it → decision flips).
- OC unit: the printed table is recomputed by the test from the binomial and must match the spec's numbers.

## C-HE-30 - Durable store audit (owed before C-HE-03 / C-HE-06 are built)

### Contract

The store set after this spec is **eight** authorities for the facts HE-1 §5 enumerates (seven from HE-1 §5 plus the gate sibling) **plus the coordination-state carriers the clearance fold adds** (enumerated and classified by the audit document — *v1.3 X3; v1–v1.2 read "The store set after this spec is eight"*). Before D1/D4-shaped code lands, the plan MUST produce a one-page audit confirming exactly one authority per fact:

| Store | Venue | Authority for |
|---|---|---|
| Queue entries (`*.json` / `*.taken`) | `QUEUE_DIR` | "capture exists and is not yet in committed history" |
| Reservation files | `QUEUE_DIR` | arc landing state (`pending/open/terminal`, generation-versioned), `concurrent_lanes_at_open` sensor, `arc_type` at open, accreted `phases` |
| Merge-door lease | `QUEUE_DIR`-adjacent | who is landing now; `merge_attempted_at` |
| `.harness/arc-metrics.jsonl` (per-worktree until committed) | `REPO` | arc rows, per-round outcomes, phases |
| `.harness/merge-gate-log.md` + structured sibling | `REPO` | gate verdicts (human + machine views of one fact — the sibling is derived from the same producer step, not a second authority) |
| `loop_status.md` (HIL rows at shared venue; control markers per-lane) | shared / per-lane | operator-attention state; run-scoped skip-set |
| Finding emission (`Finding` projection) | CI/stdout | derived from the 8-field record — never authored independently |
| Committed history on `MERGED_REF` | git | the only proof that a row is durable |

Any fact found with two authorities MUST be resolved by demoting one to a derived copy before the corresponding contract is implemented.

*(Clearance fold G1/G3/G21: the reservation is now a generation-versioned directory per arc; the lease adds a `transition.<token>` marker family and `released.*/reclaimed.*` history under `QUEUE_DIR/merge-door/`; the lane index registry lives at `QUEUE_DIR/lanes/<k>`; mechanized-check state at `.harness/mechanized-checks-state.json` — each either derived from an authority above or the sole carrier of a new coordination fact this spec introduces — never a second authority for an existing fact; the audit document classifies every family as one or the other. *v1.3 X3 correction: v1–v1.2 read "all derived from the authorities above, none a new authority for an existing fact"; the first clause was false for the transition marker, attempt window, tiering counter, lane index, HIL delivery claims and mechanized-check state — see the v1.3 change-note.*)*

### Invariants

- Exactly one authority per fact; the audit document enumerates every durable store this spec creates or extends and names its authority.
- No runtime path creates a store the audit does not list.

### Verification

- Static (`tools/test_store_audit.py`, **phase0**): `.harness/spec/store-audit-he-loop-lanes.md` exists, enumerates exactly the eight stores of the table above plus the families named in the note (each classified `derived` / part of a store / sole carrier of a new fact — *v1.3 X3*), and assigns each fact to one authority; the test greps every `QUEUE_DIR`/`.harness` path literal in `tools/arc_metrics.py`, `tools/merge_door.py`, `tools/reservations.py`, `tools/hooks/loop_lib.sh` and asserts each is listed.

---

# Part D — Defect mechanization and grounding (ADR-HE-4; D-A Layer 2 = BUILD-PLAN Arcs 4–6)

The diagnosis this Part rests on (STAGE7 §3.1 **[C]**): P1 wall-clock CONFIRMED (68% of Bash wall-clock is gate/test/review machinery; median arc 109.9 min over a median 5 rounds); P2 "rounds are redundant" REJECTED (round 2 out-yields round 1; a flat cap is unsafe); P3 "the agent under-grounds" CONFIRMED and causal (6 of 8 findings on one arc self-inflicted and mechanically catchable; rounds 6–19 of a 19-round arc were the agent re-breaking its own fixes; syntactic/runtime errors fix at > 80% within 1–2 rounds, logical at < 35% even with 10). Cost is attacked **upstream of review**.

**O1 resolution (HE-1 §6).** D-A's "Layer 2" is STAGE7's Layer 2 — *"P1 mechanization … P2 with a decorrelated equivalence proof … P3 at the corrected ~58s"* (`STAGE7-FINAL-opus-grounded-findings.md:135-137` **[V]**) — i.e. C-HE-31/32/33. It does not name lease-widening or the shadow trial: the merge-door lease is Phase-0 correctness (R-10, C-HE-06) needing no Layer-2 authorization, and the shadow trial is authorized separately by D-D (C-HE-29). Nothing remains "behind the pilot bar" except follow-on lane orchestration, which no contract here builds.

## C-HE-31 - Mechanize the self-inflicted defect classes (K1; Arc 4)

*Clearance fold G16 (2026-08-18): promotion/demotion window semantics, two-strikes hysteresis, stated operating characteristics, runtime state file (never the spec's own §8.1), demotion audit row + `NOTIFY`.*

### Contract

1. Each class below MUST be delivered as a deterministic pre-check tagged `kind ∈ {deterministic, hybrid, model-judge}`, emitting C-HE-24 rows with `producer=<check_id>`:

| Class | Freq (corpus) | Cheapest check | Wired today | kind |
|---|---|---|---|---|
| stale-carry text / counts | ≥ 11 | numeric + placeholder-token repo sweep | partial (one surface) | deterministic |
| weak / false test witnesses | 9+ | **mechanically re-verify every `# mutation-probe:` annotation's named mutation** (3 of 40 annotations were themselves false on one arc) — never re-read the annotation | partial (tool exists, applied by hand) | hybrid (mutation-probe-backed, **not sub-second**) |
| unswept consumers | ≥ 5 | `graft callers <sym> --depth all` before "complete" | no general tool | deterministic |
| unrun-CLI claims | 4 | assert exit code **and** positive content before "clean" | no | deterministic |
| cited symbol does not exist | 1 | one-line grep, near-zero false positives | no | deterministic |
| delta-chain version drift | 1 + named pattern | sweep later versions for the cited § | no | deterministic |
| wrong-fidelity test doubles | 1 | `issubclass()` assertion in a shared fixture helper | no | hybrid (mutation-probe-backed) |

2. The two mutation-probe-backed classes MUST NOT ship under a "low-risk" label; the ~32 min → ~1 s precedent does not transfer to them.
3. **Siting rule (P9(c), D7).** Blocking mechanized checks run only at a **stable boundary** — pre-commit / pre-review / pre-PR — and only when **fast, deterministic, and low-false-positive**. They MUST NOT run as a blocking `PostToolUse` on every intermediate edit ("never every intermediate edit", STAGE3 P9(c)); the existing advisory `postedit-lint.sh` may add advisory findings per edit but MUST NOT block per edit. A false-positive blocking check is worse than none (it trains routing-around).
4. **Promotion / demotion — semantics stated, state stored outside the spec.** (a) A check ships **advisory** and is promoted to **blocking** after **zero `rejected` findings across a fixed replay of the last 20 merged arcs' diffs** evaluated once at promotion time — a bar whose operating characteristic is stated honestly: P(pass | true per-arc FP rate p=0.05) = 0.95²⁰ ≈ 0.36, so it excludes p ≳ 0.15, not less. (b) Demotion uses a **rolling** 20-arc window evaluated at a named recurring site (`just lanes-verify` and CI) with **two-strikes hysteresis**: a blocking check is demoted only when ≥ 2 `rejected` findings occur in **each of two consecutive, non-overlapping** 20-arc windows (a single window at p=0.03 flaps with P ≈ 0.12). (c) Every demotion emits a `record_kind=gate_demotion` row (`producer=lanes_verify`, `severity=warn`, naming the check and the triggering counts) **and** a `NOTIFY` row (C-HE-09) at the moment it fires. (d) The live `kind`/window state is stored in `.harness/mechanized-checks-state.json` (runtime state, plan-owned); §8.1 documents only the policy and each check's initial `kind` — a runtime event never edits this specification.
5. A mechanized class MUST be measured (rows with that `producer`) before any claim that it "removed" findings of that class.

### Invariants

- No mechanized check is ever cited as grounds for a round cap (K4; #20).
- No runtime path writes to `.harness/spec/`.

### Verification

- Per class: a fixture exhibiting the defect → finding row; clean fixture → none; for the two hybrid classes, an intentionally-false annotation → detected as false.
- `tools/test_mechanized_checks.py::test_promotion_demotion_state_machine`: synthetic 20-arc replay with 0 rejections → promote; ≥2 rejected in one window → no demotion; ≥2 in two consecutive windows → demote + `gate_demotion` row + `NOTIFY` (mechanism-correctness only — not evidence the thresholds are calibrated).

## C-HE-32 - Remove duplicated executions (K2; Arc 5)

### Contract

1. A duplicated execution MAY be removed only when equivalence (command, environment, inputs, SHA) is proved by a party **decorrelated from the agent whose diff benefits** (Codex/out-of-family, or a fresh reviewer with no transcript) **or** by a deterministic execution-context diff. The proof MUST be logged as a C-HE-24 row (`finding_type=equivalence_proof`).
2. Two within-CI double-runs already identified as pure waste (same file, same SHA, same runner) **[C]** are the first candidates; `codex-check` re-run after CI-green on the same SHA is byte-identical to the CI job and yields zero new information (HE-4 §7 **[C]**).
3. Removing a run on the beneficiary's own say-so is prohibited.

### Verification

- Log witness: every removed run has a proof row naming the decorrelated party or the context-diff.

## C-HE-33 - Close the local/CI gap (K3; Arc 6)

### Contract

1. Target: the ~58 s measured aggregate (not the ~90 s previously claimed; individual gate timings were wrong by 5×, 12×, 30× until measured **[C]** — hence Part C's instrument items sequence ahead of any efficiency claim here).
2. Environment-irreproducible checks are excluded from the local equivalent and named as such.
3. **`codex_context_guard` — corrected claim.** It **is** CI-wired (`ci.yml:536-542` **[V]**) and **has** a local recipe (`just codex-context-check`, `justfile:84-87` **[V]**). The gap is **flag/ref parity**: CI runs `check --base-ref <pr-base|before> --head-ref <pr-head|sha> --allow-roadmap-drift`; local runs `checkpoint --label local-check --include-branch-diff` then `check --require-fresh-checkpoint --include-branch-diff`. The plan MUST either (a) prove the two compute the same findings for the same tree (a C-HE-32 equivalence proof) or (b) add a local recipe that mirrors CI's explicit-ref invocation. K3 MUST NOT be recorded as "no local equivalent".
4. Outcome measure: "converge locally, push once" — the share of branches burning ≥ 6 CI runs (20% today **[C]**) and CANCELLED-run share are the tracked cohorts (C-HE-28).

### Verification

- Parity test: same SHA, CI-shaped and local-shaped invocations → identical finding sets (or the documented, named exclusion).

## C-HE-34 - Non-goals of Part D (normative)

- No flat round cap; no shortening of review generically (#11/#17/#20; PR #1034, #1338 **[C]**).
- No best-of-N / parallel variant generation as a speed fix (measured null result at this model's temperature **[C]**).
- No fast mode for throughput (6× price for 2.5× throughput fails the token-economics constraint; 98.0% cache-read must not be touched **[C]**).
- No agent framework for mechanization (framework-pull discipline; candidates fail on `import litellm` / LangGraph-CrewAI-LlamaIndex dependence).
- No collapsing of review layers to cut the 68% (93.4% of 679 findings across 146 PRs were single-tool catches; merge-gate BLOCKed 46% of 141 gated PRs **[C]**).

## C-HE-35 - Grounding-gate family disposition (K5–K8) [R: D7]

The corpus adjudicated these before ADR-HE-4 recorded them as "Proposed" (`STAGE3-opus-reconciliation-of-debate.md:30-58`, `STAGE5-opus-integrated-reconciliation.md:165-177`, `STAGE7-FINAL-opus-grounded-findings.md:145` **[V]**). The spec carries those dispositions:

| ADR item | Corpus item | Disposition | Carried as |
|---|---|---|---|
| K5 — structured feedback with **mandatory** admissible alternatives | P6 | **Restructured**: location / observed evidence / expected contract / reproduction basis are required (already the C-HE-24 shape); admissible alternatives **optional/trialed, not mandated** — the +42–44pp evidence was measured on *repair* feedback and mandating alternatives "destroys the independence of the two agents" | Out of v1 as a mandate; the required fields are C-HE-24 |
| K6 — a finding must self-classify `task_relevance / scope_relation / introduced_by_current_task` before it may block | P7 | **Dropped unanimously** (both reviewers + C4/C5/C10/C11): a reviewer must never acquire authority to suppress its own finding through self-classification (scope-laundering / unreliable meta-classification). Structured scope metadata MAY be recorded; suppression authority sits only with a second decorrelated lens, a deterministic rule, or a logged operator override; every suppression emits an audit row; ambiguous scope blocks | Out; C-HE-24 §5 already carries "reviewer never authoritative for disposition" |
| K7 — route by arc type and finding class | P8 | **Deferred** until work-type and finding-class predictiveness is measured; shadow mode only if run at all | Out; prerequisites recorded at C-HE-26 §3 |
| K8 — structural grounding gate + same-turn blocking hook | P9 | **Restructured**: (a) prewritten testable done-condition → proceed; (b) "externally written" is insufficient evidence — authorship matters less than independent validation; (c) blocking post-edit hook only for fast deterministic low-FP checks at a stable boundary, never every intermediate edit | (c) IN as C-HE-31 §3; (a) → forward-register item (§11); the same-turn `preventContinuation` framing is rejected |

---

# Part E — Cross-cutting

## 5. Files reference — which files own each contract

New files are marked **NEW**; everything else exists at HEAD **[V]**. The plan decomposes from this table; a contract with no row here is a spec defect.

| Contract | Files (create / change) |
|---|---|
| C-HE-01 | `.claude/skills/two-lane/SKILL.md`, `.claude/skills/roadmap-continue/SKILL.md` (N ≥ 2 wording) |
| C-HE-02 | `tools/arc_metrics.py` (`_claim_arc` takeover `:624-626` → token compare); `tools/test_arc_metrics.py` |
| C-HE-03 | **NEW** `tools/reservations.py` (generation-CAS record: `reserve()`, `transition()`, `update_payload()`, `walk_terminal()`, `alloc_seq()`, `gc()`); `tools/arc_metrics.py` (drain-time flip + holder-gated append); `tools/test_reservations.py` **NEW**; `.claude/skills/roadmap-continue/SKILL.md` (open-time `pending` + `arc_type`); `.claude/skills/ship-pr/SKILL.md` (`pr`/`head_sha`/`base_sha`/`attested_merge_tree` back-fill) |
| C-HE-04 | `tools/arc_metrics.py` (`_recover_dead_claims` `:663-667` + holder transfer, `drain` `:718-756` fault isolation + local-row reconciliation + `ARC_METRICS_TEST_KILL_AFTER`); `tools/hooks/safe-worktree-remove.sh` + `tools/hooks/lib.sh:483-497` (ahead-of-`@{u}` refusal); **NEW** `tools/test_arc_metrics_lanes.py` (AC#2 a/b/c subprocess harness, 6 interleavings) |
| C-HE-05 | `tools/arc_metrics.py:44-45` (env overrides); `tools/test_arc_metrics.py` |
| C-HE-06 | **NEW** `tools/merge_door.py` (lease token, transition marker, acquire/verify/reconcile/release/unblock, `local-base-cas-check`, post-merge-CI wait, `MERGE_DOOR_TEST_KILL_AFTER`); `.claude/skills/ship-pr/SKILL.md` (acquire-before-construct, steps i–ix incl. refresh as continuation); `.github/workflows/ci.yml:43-45` (SHA-keyed concurrency for `main` pushes); **NEW** `justfile` recipe `merge-door-unblock`; `tools/test_merge_door.py` **NEW** |
| C-HE-07 | **NEW** `tools/hooks/safe-merge.sh`; `tools/hooks/permission-guard.sh` (`:288-290` allow, `:314-340` deny); `tools/hooks/test_permission_guard.sh:167-169,328-329` |
| C-HE-08 | `tools/hooks/permission-guard.sh:314-340` (explicit push-to-main `emit_deny` entries) + `test_permission_guard.sh`; **NEW** `justfile` recipes `main-protection-{show,apply,rollback,tiebreaker,verify}` (`verify` is the phase0 row; `apply` operator-gated) |
| C-HE-09 | `tools/hooks/loop_lib.sh` (`loop_status_path()` `:24` body, structured column + reducers `:149-186`, `NOTIFY`/`COALESCE-DELIVERED` kinds, rendered `lane_id`); pointer sweep: `loop_lib.sh:6,231`, `.claude/skills/{loop-start,loop-stop,resolve,ship-pr}/SKILL.md`; `tools/hooks/test_loop_lib.sh` |
| C-HE-10 | `tools/hooks/loop_lib.sh:165,191-225` (`cause_signature` key + window); `tools/hooks/test_loop_lib.sh` |
| C-HE-11 | `justfile:469-480` (`-p`, port blocks); **NEW** `tools/hooks/lane-init.sh` (`gc.auto 0` once; `HARNESS_LANE_ID`; `HARNESS_LANE_INDEX` via `QUEUE_DIR/lanes/<k>` exclusive create; RAM probe → `NOTIFY`); `deploy/self-hosted-local/compose.yaml` (port variables) |
| C-HE-12 | `tools/codex_context_guard.py` (new codes + lane field, `_json_report`); `.github/workflows/ci.yml` (**NEW** split-brain job); `tools/test_codex_context_guard.py` |
| C-HE-13 | **NEW** `tools/arc_disjoint_check.py` (U-WT-07) + tests; **NEW** `justfile` recipes `lanes-phase0-check`, `lanes-pilot`; `.claude/skills/two-lane/SKILL.md` (scope-hint wording) |
| C-HE-14 | `.claude/skills/two-lane/SKILL.md` (blocked list) — doc only |
| C-HE-15 / 16 / 18 | **NEW** `tools/review_wrapper_common.py` (schema parse, classifier table, terminal states); **NEW** `tools/codex_review.py`; `tools/agy_review.py` (adopt common module); **NEW** `tools/review_schemas/{codex,gemini,merge-gate}.schema.json`; `justfile` (`codex-review` → wrapper); tests **NEW** `tools/test_review_wrapper.py` |
| C-HE-17 | `.claude/skills/ship-pr/SKILL.md` + `.claude/skills/roadmap-continue/SKILL.md` (failover step + the invariant-#3 restatement, in-scope carriers); `justfile:607-608`. (`AGENTS.md:56-57` carries the same #3 prose **[V]** but is the Codex-projection tree, out of scope per §10 — its restatement is a companion Codex-posture item on the same §11 forward row; ADV-F3.) |
| C-HE-19 | `.claude/skills/ship-pr/SKILL.md:199-204` (explicit `CANCELLED`); `tools/arc_metrics.py` CI-state enum |
| C-HE-20 | `tools/hooks/loop_lib.sh` (TTL re-surface); `tools/arc_metrics.py` (reservation stuck → HITL row) |
| C-HE-21 / 22 | `.claude/skills/merge-gate/SKILL.md`, `ship-pr/SKILL.md` (live-carrier cites, no round cap) — doc; **NEW** `tools/reviewer_concurrency_probe.py` |
| C-HE-23 / 24 / 25 | `tools/arc_metrics.py` (row schema); `.claude/skills/merge-gate/SKILL.md` (emit `.harness/merge-gate-log.jsonl` **NEW** file); **NEW** `tools/finding_record.py` (8-field core + envelope + `Finding` projection); `tools/codex_context_guard.py` (consume projection); tests |
| C-HE-26 | `tools/arc_metrics.py` (`arc_type` required at open; `arc_type_declared_at`); `.claude/skills/roadmap-continue/SKILL.md` |
| C-HE-27 | `tools/arc_metrics.py` (`phases` map); emitters in `.claude/skills/{roadmap-continue,ship-pr}/SKILL.md` and `tools/hooks/*` |
| C-HE-28 | `tools/arc_metrics.py:812-832` (cohort by `concurrent_lanes_at_open` joint with `arc_type`; drift-finding join) |
| C-HE-29 | **NEW** `tools/shadow_trial.py` (scoring reducer, config row); `.claude/skills/ship-pr/SKILL.md` (off-path invocation) |
| C-HE-30 | **NEW** `.harness/spec/store-audit-he-loop-lanes.md` (plan S3 deliverable) |
| C-HE-31 | `tools/hooks/postedit-lint.sh` (advisory stays advisory); **NEW** `tools/mechanized_checks/<class>.py` ×7 + `just mech-check` recipe (pre-commit/pre-review boundary); **NEW** `.harness/mechanized-checks-state.json` (runtime `kind`/window state); tests incl. `test_promotion_demotion_state_machine` |
| C-HE-32 | `.github/workflows/ci.yml` (remove proven double-runs); `justfile`; proof rows via `tools/finding_record.py` |
| C-HE-33 | `justfile:84-87` (CI-parity recipe or equivalence proof); `.github/workflows/ci.yml:536-540` |
| C-HE-34 / 35 | doc only (this spec; `.claude/skills/*` non-goals) |

## 6. Unified build order

Three sequencings coexist in the corpus and are not interchangeable (Arc 1–7 ratified · Phase 0/1/2 lanes · Layer 0–4 STAGE7). This section is the **single order the plan decomposes from**. Two gate columns make the "0a/0b" substance explicit without a fourth numbering scheme (HE-3 §5): an item gates **lane safety** (must land before N ≥ 2 runs) and/or **measurement** (must land before any efficiency claim or before Arc 4+).

| Step | Contracts | Corpus refs | Gates lane safety | Gates measurement | Depends on |
|---|---|---|---|---|---|
| **S1** Verdict validity + terminal states + failover + wrapper | C-HE-15, 16, 17, 18, 19, 20 | Arc 1 · Phase 0 items 1, 3 | yes (live at N=1) | — | — |
| **S2** Record extension + finding record + `arc_type` at open + env overrides | C-HE-23, 24, 25, 26, 05 | Arc 2 · Phase 0 item 2, P0-12 | partly (C-HE-05 is a prerequisite of AC#2(a)) | **yes** | — |
| **S2 hand-off contract** (C1-F2 / C7-T10 / C8) | — | — | — | — | Consumers MUST treat S2-GREEN as **schema-present only**; each consumer (S3, S4a, S4d, S5, S6) performs its own semantic-resolution check — the `arc_type` open-time join, the phase-span accretion point, the `concurrent_lanes_at_open` key shape — before relying on the field; S6 additionally requires the joint `(concurrent_lanes_at_open, arc_type)` stratification before any AC#10 value claim |
| **S3** Store audit | C-HE-30 | HE-1 §5 | yes (before S4b/S4d) — observable via the C-HE-30 phase0 row | — | S2 |
| **S4a** Primitive + drain guards + capture durability | C-HE-02, 04 | Phase 0 items 5, 6 (as amended) · R-4/R-5/R-6 · E9 | yes | — | S2 (C-HE-05 for the probe) |
| **S4b** Reservation | C-HE-03 | Phase 0 item 4 · R-7/R-14 | yes | — | S3, S4a |
| **S4c** Merge-door lease + wrapper + X9 fences | C-HE-06, 07, 08 | Phase 0 items 9b, 10 · R-19…R-28 · P1/P2/P4 · D5/D8 | yes | — | S4b (`reservation_id`) |
| **S4d** `loop_status` venue + coalescing + env isolation + emitting detections | C-HE-09, 10, 11, 12 | Phase 0 items 7, 8, 9, 11 · R-16/R-17/R-18 · P3 | yes | C-HE-12 also measurement | S2 (record) |
| **S5** Phase timing spans | C-HE-27 | Arc 3 · Phase 1 item 10 | — | **yes** | S2 |
| **S6** Reviewer-concurrency probe → coalescing live → pilot gate + pilots + O1 + O3/`arc_disjoint_check` + attestation tiering | C-HE-22, 13, C-HE-06 §10, 28 | Phase 1 items 14, 13, 13b, 11, 12 · R-10/R-11/R-12/R-21 | — (pilots do not gate N) | **yes** (AC#10 baseline) | **all of S1–S5 GREEN** (mechanical pilot gate) |
| **S7** Mechanize classes → dedupe executions → local/CI gap | C-HE-31, 32, 33 | Arcs 4–6 · Phase 2 items 15–17 · Layer 2 | — | consumes S2/S5 | S2, S5 (instrument before claim) |
| **S8** Shadow trial live | C-HE-29 | Arc 7 · Phase 2 item 19 | — | consumes S2 | S1 (wrapper), S2 |
| **Blocked** | C-HE-14 | items 20, 21 | — | — | — |

```
S1 ─┐
S2 ─┼─► S3 ─► S4b ─► S4c
    │            ▲
    ├─► S4a ─────┘
    ├─► S4d
    ├─► S5 ─────────────┐
    │                   ▼
    └───────────► S6 (gate: S1..S5 GREEN) ─► pilots / O1 / O3
S2 + S5 ────────► S7 ─► S8
```

**Sequencing rationale.** S1 first because it is live at N=1 and everything downstream keys verdicts on it. S2 before the lanes floor because the finding record and `lane_id` are what make S4d's detections *emit* and what AC#2(a) needs (`ARC_METRICS_REPO/LEDGER`). S3 before S4b/S4c so no second authority is created while building D1/D4. S4c after S4b because the lease carries `reservation_id`. S6's mechanical gate is the whole point of the pilot bar — a pilot on unfixed state produces contaminated signal. S7/S8 after S2/S5 because every efficiency number in Part D was wrong until instrumented.

**Honest aggregate.** Phase 0 (S1–S4) is roughly **double** v1's Phase 0 (v2 §4.1); it is a real body of work, not a quick fix, and it is unconditional (not deferral).

## 7. Durable store audit

Carried at C-HE-30 (eight stores, one authority per fact). Owed as the first plan deliverable of S3.

## 8. Acceptance criteria (v1/v2 AC#1–10, mapped)

| AC | Statement | Contracts | Witness |
|---|---|---|---|
| 1 | Four lanes safe and durable | Part A | `just lanes-phase0-check` GREEN (S1–S4) + AC#2 — this, not the pilots, is the safety gate for N ≥ 2 |
| **2** | For every `arc_id`, across any number of lanes and any elapsed time between drains, exactly one row reaches merged history, and no queue entry is released before its row is durably committed | C-HE-03, 04, 05, 06 | **(a)** same-instant subprocess sweep · **(b)** cross-latency sequential · **(c)** crash-resume three kill points — each **mutation-probe**, RED first |
| 3 | No data loss in shared `.harness/` artifacts | C-HE-02, 04, 09 | E9 witness; reducer scoping test |
| 4 | §12.2.1 refresh fixed point preserved | C-HE-01 | one-file refresh shape unchanged |
| 5 | Invariant #16 adjudicated | C-HE-21 | void (live-carrier rule) |
| 6 | Decorrelation not weakened | C-HE-15, 17, 18 | both cross-vendor channels carry gate contracts |
| 7 | No flat round cap | C-HE-21, 34 | grep witness: no numeric round cap in loop skills |
| 8 | Rebase tax addressed or priced | C-HE-01 §4 | priced as "well under N×", measured by AC#10 |
| 9 | Failure-mode inventory with detections | C-HE-12, §9 | ≥ 4/19 emitting after S4d |
| 10 | Value: cohort comparison of lane count | C-HE-25, 28 | `concurrent_lanes_at_open` × `arc_type` cohorts from the historical N=1 baseline (descriptive only until N≥2 cells populate) |

### 8.1 Verification manifest and skip policy

One umbrella recipe, `just lanes-verify`, runs every row; `just lanes-phase0-check` runs the rows tagged **phase0** and treats a skip as a failure (C-HE-13 §1). Rows are pytest node IDs or shell test scripts; each is tagged with its gate and its dependency, so an unfamiliar implementer knows what runs where.

| Contract | Test artifact | Tag | Runs in | mutation-probe | Depends on / skip policy |
|---|---|---|---|---|---|
| C-HE-02 | `tools/test_arc_metrics.py::test_takeover_token_compare` | phase0 | local + CI | yes | none |
| C-HE-03 | `tools/test_arc_metrics.py::test_reservation_*` (transitions, chain cap, ground-truth) | phase0 | local + CI | — | `gh` mocked |
| C-HE-03/04 | `tools/test_arc_metrics_lanes.py::test_ac2_a_same_instant[*]` (6 interleavings) · `::test_ac2_b_cross_latency` | phase0 | local + CI | yes | needs C-HE-05; real subprocesses; **no skip** |
| C-HE-04 | `tools/test_arc_metrics.py::test_drain_fault_isolation` · `::test_e9_capture_republish` | phase0 | local + CI | yes | none |
| C-HE-05 | `tools/test_arc_metrics.py::test_env_overrides` | phase0 | local + CI | — | none |
| C-HE-06 | `tools/test_merge_door.py::test_ac2_c_crash_resume[kill1,kill2,kill3]` · `::test_timeout_reconcile` · `::test_lease_holder_invariant` · `::test_contention_fail_fast` | phase0 | local + CI | yes | `gh` mocked with call log; **no skip** |
| C-HE-07 | `tools/hooks/test_permission_guard.sh` (raw merge deny / wrapper allow) | phase0 | local + CI | — | none |
| C-HE-08 | `tools/hooks/test_permission_guard.sh` (push-to-main `emit_deny` predicates, wrapper arity) | phase0 | local + CI | yes | none |
| C-HE-08 | `just main-protection-verify` (read-only exact-compare of every required setting + context) | phase0 | **local** (session `gh` auth) | — | `gh-auth-absent` → skip → counts as RED for `lanes-phase0-check`; CI's `GITHUB_TOKEN` lacks the scope |
| C-HE-08 | `just main-protection-tiebreaker` (scratch PR under `strict:true` + stale-refresh-branch fast-forward) · `apply` | operator-gated live | loop, live — operator answers one decision | — | recorded in the plan's evidence log, not a pytest row |
| C-HE-09/10 | `tools/hooks/test_loop_lib.sh` (reducer scoping, venue, coalescing groups) | phase0 | local + CI | yes | none |
| C-HE-11 | `tools/hooks/test_lane_init.sh` (`gc.auto` once) | phase0 | local + CI | — | none |
| C-HE-11 | `tools/test_compose_lanes.py` (distinct `-p`, ports, no bind conflict) | **env** (not phase0) | local | — | `skipif(no docker daemon)`, reason `docker-daemon-absent`; the recipe/port-formula unit `::test_lane_port_formula` is phase0 and needs no daemon |
| C-HE-12 | `tools/test_codex_context_guard.py::test_split_brain_*` · `::test_base_toctou` · CI job `split-brain` | phase0 | local + CI | — | none |
| C-HE-13 | `tools/test_arc_disjoint_check.py` · `tools/test_lanes_pilot_gate.py` | phase1 | local + CI | — | none |
| C-HE-15/16/18 | `tools/test_review_wrapper.py` (per-channel battery: empty/truncated/auth/valid/session-artifact) | phase0 | local + CI | yes | CLIs mocked; **no skip** |
| C-HE-17 | `tools/test_review_wrapper.py::test_failover_*` | phase0 | local + CI | — | mocked |
| C-HE-19/20 | `tools/test_arc_metrics.py::test_ci_state_cancelled_incomplete` · `::test_ttl_never_reclaims` | phase0 | local + CI | yes | none |
| C-HE-22 | `tools/reviewer_concurrency_probe.py` (live) | phase1 | operator/loop, live | — | provider-login-gated; result row required before pilots |
| C-HE-23–26 | `tools/test_finding_record.py` (schema, projection round-trip, reducer) · `tools/test_arc_metrics.py::test_arc_type_at_open` | phase0 | local + CI | yes | none |
| C-HE-27/28 | `tools/test_arc_metrics.py::test_phase_spans_no_deltas` · `::test_cohort_by_concurrent_lanes_at_open_and_arc_type` | measurement | local + CI | — | none |
| C-HE-29 | `tools/test_shadow_trial.py::test_kill_rule` | measurement | local + CI | — | none |
| C-HE-31 | `tools/test_mechanized_checks.py[<class>]` (defect fixture / clean fixture / false-annotation) | layer2 | local + CI | yes | mutation-probe rows may take minutes; not phase0 |
| C-HE-32/33 | proof rows present (`tools/test_finding_record.py::test_equivalence_proof_rows`) · CI-parity test | layer2 | CI | — | none |

| C-HE-30 | `tools/test_store_audit.py` (audit doc exists, 8 stores + derived families, one authority each, path literals covered) | phase0 | local + CI | — | none |
| C-HE-06 | `tools/test_merge_door.py::test_marker_race` · `::test_continuation_no_reacquire` · `::test_post_merge_ci_blocked_and_unblock` · `::test_rate_limit` | phase0 | local + CI | yes | `gh` mocked |
| C-HE-27 | `tools/test_arc_metrics.py::test_n6_formula` (accepted-count ÷ verify+edit hours; unavailable spans excluded) | measurement | local + CI | — | none |
| C-HE-13 | `just lanes-pilot-report <run-id>` (computes the §3 iff-clause) | phase1 | local | — | none |
| C-HE-31 §4 | `tools/test_mechanized_checks.py::test_promotion_demotion_state_machine` (mechanism only) | layer2 | local + CI | — | none |
| §0.3 | `just mutation-probe-coverage-check` — every row with `mutation-probe: yes` has been run through `just mutation-probe` and passed before its contract closes | phase0 (meta) | local + CI | — | none |

The `mutation-probe` column is populated from every inline `(**mutation-probe**: …)` annotation in Parts A–D (C8-F9); `just mutation-probe-coverage-check` asserts coverage. Skip policy: only environment-gated rows may skip (`docker-daemon-absent`, `provider-login-absent`, `gh-auth-absent`), each with a named reason; a skipped **phase0** row fails `lanes-phase0-check`. No row may skip on "slow".

## 9. Failure modes (19) → detection / contract

| # | Failure mode | Detection today | After this spec |
|---|---|---|---|
| 1 | Split-brain ledger | none | `SPLIT_BRAIN_LEDGER` CI backstop (C-HE-12) |
| 2 | Claim race | none (crash) | C-HE-02 token takeover + C-HE-04 guards; AC#2(a) |
| 3 | Orphaned worktree | none | pilot hygiene line + `safe-worktree-remove` (existing) |
| 4 | Stale lock / lease | none | C-HE-06 two-step reclaim; `ORPHANED_RESERVATION` |
| 5 | Partial merge | none | `merge_attempted_at` + ground-truth reconcile (C-HE-06) |
| 6 | Refresh collision | `ROADMAP_STATUS_DRIFT` **[V]** | lane-attributed (C-HE-24 §6) |
| 7 | Base TOCTOU | none | `local-base-cas-check` (C-HE-06 ii) + `BASE_TOCTOU` first-parent detection (C-HE-12) + branch protection (C-HE-08) |
| 8 | Duplicate scheduling | none | selection-time `pending` reservation (C-HE-03 §4) |
| 9 | Stale evidence reuse | prose | verdict bound to `head_sha` (C-HE-15 §3) |
| 10 | Semantic conflict across disjoint files | none | reported as unmeasured; O3 prior + prospective `arc_disjoint_check` (C-HE-13) |
| 11 | Fragment double-apply / loss | n/a | fragment split rejected (C-HE-09) |
| 12 | Remote merge succeeded, response lost | none | reconcile by `gh pr view`, never blind retry (C-HE-06 §5) |
| 13 | Merge-queue starvation | none | fail-fast primitive + caller backoff+jitter (C-HE-06 §8); attestation tiering surfaces waits |
| 14 | Cross-lane loop-marker interference | none | venue determinism + ACTIVATE scoping (C-HE-09) |
| 15 | Shared runtime resources | none | Docker `-p` + full port set (C-HE-11) |
| 16 | Orphaned descendant processes | `loop-gc.sh` (existing) | unchanged; noted |
| 17 | Journal partial write | none | atomic rename for every transition (C-HE-02) |
| 18 | Same register unit changed by two lanes | none | scope hint + prospective check + first-parent detection (C-HE-13 §5) |
| 19 | Detached `git gc` | none | `gc.auto 0` repo-wide once (C-HE-11) |

## 10. Explicitly out of scope

- **STAGE7 Layers 3–4** (D-A stops at Layer 2): N1 repair protocol with per-sub-step checkpointing; P8 routing (see C-HE-35 K7); P11 batch-size experiment (3/5/10); N3, N4; the corpus-stratification variant of the shadow trial (superseded by D-D live).
- **BUILD-PLAN "known-open, not blocking"** (phase-span durability is **closed** for v1 by C-HE-27 §3 — durable): whether a `result_capture` divergence is itself audit-worthy; the false-block-rate monitor and suppression-rate breaker (C10); the per-role model table (C6); the operator comprehension digest (C11).
- **Follow-on lane orchestration** (automated lane spawning) — behind `two-lane/SKILL.md:140-142`'s organic-pain bar after ≥ 3 pilots.
- H_T design surface; anything requiring a framework; the Codex-projection tree (`AGENTS.md`/`.agents/`) — carrier drift there is a separate class (`[[agents-md-is-the-codex-projection-not-claude-side]]`).
- v1 §10's not-being-built list, carried at C-HE-14.

## 11. Open items carried to the plan / forward register

| # | Item | Owner | Where |
|---|---|---|---|
| 1 | Store audit one-pager (C-HE-30) | plan S3 | first plan deliverable |
| 2 | Scratch-PR tiebreaker for branch protection (C-HE-08 §4) | plan S4c, operator-gated live step | plan evidence log |
| 3 | P9(a) prewritten testable done-condition before implementation | forward register (`B-*` row) | not in v1 |
| 4 | K7 stop rule for `applying` arcs — after C-HE-26 labels + > 3/18 mapping | forward register | not in v1 |
| 5 | Whether a `result_capture` divergence (process-exit vs log-write) is itself audit-worthy | plan S5 decides | C-HE-27 §1 |
| 6 | Council adjudication of P1–P4 (C-HE-06 §3/§7, C-HE-07, C-HE-09, C-HE-06 §4 timeout) | D4 council pass | v1.1 amendment if any is rejected |
| 7 | Reviewer-concurrency probe result (C-HE-22) | plan S6 | record row |
| 8 | Whether the transient/permanent classifier table lives in code or a data file | plan S1 | C-HE-16 §4 |
| 9 | **Cross-carrier merge-door fencing** — a Claude lane and a Codex-exec lane running concurrently can both reach `gh pr merge` (`.agents/skills/ship-pr/SKILL.md:96`; `permission-guard.sh` has no jurisdiction over `codex exec`). Requires a Codex-side hook-equivalent or rewiring that skill to `tools/hooks/safe-merge.sh` under Codex posture; also the invariant-#3 restatement in `AGENTS.md:56-57`; also Docker port isolation for Codex legs (no `HARNESS_LANE_INDEX`) | forward register, joint Claude/Codex arc | C-HE-01 §1, C-HE-11 §1, C-HE-06 §10 `NOTIFY` (council G5; **operator may reverse the v1 scoping**) |
| 10 | Shadow-trial kill rule alternative — SPRT (H0 p≈0.02 vs H1 p≈0.15, stated α/β) instead of the fixed n=30/<2 rule | plan S8 may adopt; operator may amend | C-HE-29 §3 |
| 11 | Cross-`head_sha` same-defect tracking for `finding_id` (content hash over `location`+`finding_type`) | forward register | C-HE-24 §4 |
| 12 | Randomized / quasi-randomized lane assignment on a controlled arc subset, if a causal AC#10 claim is ever wanted | forward register | C-HE-28 §3 |
| 13 | Whether the `strict:true`/SHA-keyed `main` concurrency change should be paired with a queue-depth cap once N-lane cadence data exists | plan S4c | C-HE-06 §4 |

## 12. Decision register

| ID | Decision | Status | Carried at |
|---|---|---|---|
| D-A | Build through Layer 2 | ratified 2026-08-17 | §0.5, Part D preamble |
| D-B | Extend records; no new ledger | ratified | C-HE-23 |
| D-C | Second cross-vendor reviewer as automatic failover | ratified | C-HE-17 |
| D-D | Shadow trial live | ratified | C-HE-29 |
| D5 | X9: both fences MUST | operator 2026-08-18 | C-HE-08 |
| D6 | `gemini-review` = failover, blocking under identical bar; #3 restated | operator 2026-08-18 | C-HE-17 |
| D7 | K5–K8 corpus dispositions; P9(c) in; P9(a) forward | operator 2026-08-18 | C-HE-31 §3, C-HE-35 |
| D8 | P1–P4 normative; council adjudicates; P1 supersedes R-19 | operator 2026-08-18 | C-HE-06, 07, 09 |
| HE-1 O1 | D-A "Layer 2" = STAGE7 Layer 2 (mechanize/dedupe/gap); lease is Phase-0; shadow trial is D-D | **resolved by tiebreaker** (`STAGE7:135-137` **[V]**) | Part D preamble |
| HE-1 O2 | withdrawn (contradicted D-C) | closed | C-HE-17 |
| HE-1 O3 | 24h TTL adopted as notification threshold; never reclaims — **at any tier** (the draft's `pending`-aged silent reclaim over-read D8, which covers only the `open` tier; removed in the clearance fold, G2) | **resolved by tiebreaker** (no TTL-reclaim path **[V]**) + fold | C-HE-03 §5, C-HE-20 |
| L0.2′ | Ratified 8-field finding core (BUILD-PLAN D-A × D-B reconciliation) | ratified 2026-08-17 (cited as `[R: BUILD-PLAN L0.2′]`) | C-HE-24 §1 |
| Council G5 | Codex-exec lanes OUT of v1 scope for C-HE-06/07 (C1 ruling; C10 concurrence) | council 2026-08-18 — **operator may reverse** | C-HE-01 §1, §11 #9 |
| Council G4 | Lease held through post-merge CI + terminating refresh as a continuation; `main` CI concurrency keyed by SHA | council 2026-08-18 (C10/C9 deadlock fix; Codex C1-04) | C-HE-06 §4 |
| Council G15 | Shadow-trial rule n=30 / kill-if-<2 with stated OC | council 2026-08-18 (C8/C7); operator may amend per BUILD-PLAN | C-HE-29 §3 |
| HE-1 O4 | Branch protection adopted | resolved by D5 | C-HE-08 |
| HE-2 §6 | Failover channel for Claude-authored diffs | resolved by D6 (authorship gate is prose **[V]**) | C-HE-17 |
| HE-3 §6 | 8-field record vs 3-field `Finding` | **resolved by tiebreaker** (no positional parse **[V]**) + ratification-outranks-council | C-HE-24 |
| HE-4 §6.1 | K5–K8 under D-A? | resolved by corpus dispositions + D7 | C-HE-35 |
| HE-4 §6.2 | K7 stop rule | deferred; prerequisites recorded | C-HE-26 §3, §11 |
| v1 §9 #3 | Does the ≥3-pilot gate apply to a top-down N=4 mandate? | resolved: pilots gate follow-on orchestration only (v2 §1) | C-HE-13 §3 |
| v1 §9 #4 | Gate-coalescing shape | resolved: one batched prompt by `cause_signature` (v2 item 8) | C-HE-10 |
| E43 #13 vs D3 | Backoff for waiting lanes vs fail-fast lease | resolved: primitive fail-fast, caller policy no-tight-poll/backoff+jitter | C-HE-06 §8, C-HE-11 §3 |
| E17 | Scope declaration | resolved: hint + actual-write enforcement | C-HE-13 §5 |
| E9/E21 | Capture loss on worktree disposal | resolved: re-publish on vanished entry | C-HE-04 §3 |

## 13. References

**Verified at HEAD `17011f89c` in this authoring session (2026-08-18) — `[V]` means exactly this.**

- `tools/arc_metrics.py` — `REPO`/`LEDGER` `:44-45` · `QUEUE_DIR` `:59-63` · `MERGED_REF` `:79` · `run()` `:134-146` (no `timeout=`) · `publish_exclusive` `:516-534` (temp-write + `os.link`) · `_process_is_alive` `:541-548` · unknown-ownership rule `:586-588` · `_claim_arc` doctrine `:602-610` · takeover-by-path `:624-626` · FNF idiom `:633-638` · `os.replace` `:666`, `:746`, `:754` · `drain()` loop `:718-756` · queue-hold intent `:749-756` · `read_ledger()` `:765-775` · `fmt_span` ~5× variance `:780-793` · cohort split `:812-832` · `cancelled` only at `:270-271` (timing-exclusion comment) · `flock`/`fcntl` 0 **in this file** (7 unrelated `tools/hooks/**` users exist — C-HE-02 scope) · `lane_id`/`concurrent_lanes`/`reservation` 0 · `finding_id` 0 across `.py` · ledger 18 rows (`arc_type`: 6 `inventing`, 12 null, 0 `applying`)
- `tools/hooks/lib.sh:18-22` (`hook_project_dir`), `:483-497` (`hook_worktree_local_state`, no ahead-of-upstream check) · `tools/hooks/safe-worktree-remove.sh` (exists; mutex-backed) · `tools/hooks/loop_lib.sh:73-74` (kind vocabulary), `:24` (`loop_status_path`), `:175-186` (rejoin loop) · `tools/agy_review.py:22,449-463,476,508,556` (budget decrementer, no retry loop) · `tools/test_codex_context_guard.py:634` (one `startswith` prefix consumer) · `tools/codex_context_guard.py:1050` (`== "hard"`) · `.github/workflows/ci.yml:39-40` (`push: branches: [main]`), `:47-48` (`permissions: contents: read`) · `.agents/skills/ship-pr/SKILL.md:96` (literal `gh pr merge … --match-head-commit`), `.agents/skills/two-lane/SKILL.md:13`, `AGENTS.md:32` (cap 2), `AGENTS.md:56-57` (invariant #3 prose) · literal `.harness/loop_status.md` pointers: `loop_lib.sh:6,231`, `loop-start/SKILL.md:16,34`, `loop-stop/SKILL.md:23`, `resolve/SKILL.md:15`, `ship-pr/SKILL.md:309` · `justfile`: no `main-protection` recipe · `tools/mutation_probe.py:1-60` + `justfile:259-260` (RED-first mechanism genuine)
- `tools/hooks/permission-guard.sh` — loop gate `:76` · `_bash_args_safe` `:122-144` · raw worktree-removal deny `:57-65` · `_safe_worktree_remove_wrapper` `:184-191` · wrapper allow `:288-290` · deny block `:314-340` (push predicates `:321-329`) · `--admin` merge deny `:397` · allow alternation `:427` (bare `push`, `gh pr merge`)
- `tools/hooks/test_permission_guard.sh` — `gh pr merge → allow` `:167-169`, `:328-329`
- `tools/hooks/loop_lib.sh` — `loop_now()` `:44` · `loop_log` `:77-85` · skip-set / ACTIVATE `:127-129`, reducer `:149-156` · `_loop_pending_hil_rows` `:165` · cap list `:191-225`
- `tools/hooks/capture-failure.sh:101` (10 s lock reclaim) · `tools/hooks/loop-gc.sh:132,161` (7-day prune) — the only reclaim/TTL paths at HEAD
- `tools/codex_context_guard.py` — `Finding` `:113-117` · `ROADMAP_STATUS_DRIFT` `:774-781` · `ROADMAP_STATUS_BRANCH_DIVERGED` `:806-810` · render `:894` · `_json_report` `:928` · consumers exact-equality `tools/test_codex_context_guard.py:110-308`
- `.github/workflows/ci.yml` — `cancel-in-progress: true` `:43-45` · guard `check` `:536-540` · guard tests `:542`
- `justfile` — `codex-context-check` `:84-87` (+ `:71-91` siblings) · `gemini-review` `:607-608` · compose recipes `:469-480` (no `-p`)
- `tools/agy_review.py` — only `--base` `:612`; no authorship logic · `tools/codex_review.py` absent · `tools/arc_disjoint_check.py` absent
- `deploy/self-hosted-local/compose.yaml` — `name:` `:1` · ports `:12,24-25,41-42`
- `.claude/skills/merge-gate/SKILL.md` `:12-17`, `:127`, `:150-153` · `.claude/skills/ship-pr/SKILL.md` `:188-204` · `.claude/skills/two-lane/SKILL.md` `:8`, `:19`, `:78-81`, `:140-142`
- `tools/test_arc_metrics.py:174-187` (mock-`run` fixture idiom)
- `.harness/forward-register.yaml` — 186 `id:` rows, 0 `scope.files`/`files:` keys
- GitHub — `main` `protected: false`, rulesets `[]` (re-probed) · git config `extensions.worktreeConfig` UNSET, `gc.auto` UNSET · git 2.39.5
- Corpus text — `STAGE7-FINAL-opus-grounded-findings.md:135-137,145` (loop-eng) · `STAGE3-opus-reconciliation-of-debate.md:30-58` · `STAGE5-opus-integrated-reconciliation.md:165-177` · `ERROR-LEDGER.md:15,32,38,47,51,68,70` (parallel-lanes)

**Ratified / council-recorded, not independently re-verified here — `[C]`.** BUILD-PLAN decisions D-A…D-D and Arcs 1–7 · rulings R-1…R-29 and E4 rounds (`HARNESS-LOOP-AND-LANES-DESIGN-v2.md` §10a) · L-1…L-5, X1–X8, AC#1–10, the 19 failure modes (`…-v1.md`) · CI/arc statistics (68%, 109.9 min, 13.7%→180/1,390, 93.4%, 46%, 20% ≥6-run branches, ~58 s, 5×/12×/30×) · PR #1386/#1034/#1338/#1349 forensics · `arc_metrics.py:270-277` green-timing exclusion · `ci.yml` cancellation semantics beyond `:43-45` · `R1-uwt09-prior-art.md` §7 checklist · `two-lane/SKILL.md:17` scope instruction wording

**Governing artifacts.** `CLAUDE.md` §11.2, §12.2.1, §12.4.1, X-AL-1, CP-AL-1 · `.harness/adr/README.md` + `.harness/adr/ADR-HE-{1,2,3,4}_*.md` (repo) · council charter `.harness/council/loop-lanes-design-v1/00-CHARTER.md` (repo).

**Design corpus — outside the repo, under the operator's gstack research tree** (`$GSTACK_HOME`, default `~/.gstack`; base `~/.gstack/projects/arhugula-v2/research/`): `BUILD-PLAN`: `loop-eng-2026-08-16/BUILD-PLAN-operator-ratified-2026-08-17.md` · design v1/v2/review: `HARNESS-LOOP-AND-LANES-DESIGN-v1.md`, `HARNESS-LOOP-AND-LANES-DESIGN-v2.md`, `HARNESS-LOOP-AND-LANES-DESIGN-v2-ARCHITECTURE-REVIEW.md` · loop-eng: `loop-eng-2026-08-16/{STAGE3-opus-reconciliation-of-debate.md, STAGE5-opus-integrated-reconciliation.md, STAGE7-FINAL-opus-grounded-findings.md, SYNTHESIS-loop-v2-reconciliation.md, R1-uwt09-prior-art.md}` · lanes: `parallel-lanes-2026-08-17/{STAGE5-opus-integrated-reconciliation.md, STAGE7-FINAL-opus-grounded-findings.md, ERROR-LEDGER.md}`. PR forensics (#1386, #1034, #1338, #1349) are GitHub PRs of this repo; the reviewer session artifact for #1386 is under `~/.codex/sessions/`. The corpus is evidence, not a build input: the plan MUST cite this spec's `C-HE-NN`, not the corpus.

**Council-dependent status, stated plainly.** Every contract is buildable as written. Three carry a **v1.1-if-rejected** flag from the D4 council pass — C-HE-07 (P1 wrapper), C-HE-06 §7 (P2 lease-holder invariant) and §4-timeout (P4), C-HE-09 §1 (P3 single file). If the council rejects any, the plan builds the remainder unchanged and that contract is struck by change-note; nothing else depends on them except as noted in §6.

## 14. Filing footer

This specification is H_E tooling only; it does not extend the H_T design (`.harness/adr/README.md` namespace rule). Contracts marked `[R]` rest on operator ratification (BUILD-PLAN 2026-08-17; D5–D8 2026-08-18). Contracts derived from HE-1 §3.2 P1–P4 (C-HE-06 §3/§7/§4-timeout, C-HE-07, C-HE-09 §1) are normative in v1 **subject to the D4 council pass**; a rejection yields a dated v1.1 change-note, never an in-place rewrite. Clearance = adversarial review + `just codex-review` + convened harness council, then a marker at `.harness/clearance/spec-he-loop-lanes-v1-cleared-<date>.md`; the implementation plan MUST cite this file's `C-HE-NN` identifiers and MUST NOT consume it before the marker exists.

