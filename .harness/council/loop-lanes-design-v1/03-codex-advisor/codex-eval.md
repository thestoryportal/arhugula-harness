# Cold review verdict

The design is directionally sound, but it is not safe to implement as written. The high-level order “correctness → evidence → optimization” is right. The concrete order is wrong because enforceable merge serialization is deferred to Phase 2, after the proposed 3–4-lane pilots.

## 1. Build order

Move these before any multi-lane pilot:

1. **Enforce the merge door in Phase 0.** A merge-door lease is correctness machinery, not speed machinery. Raw `gh pr merge` is currently auto-allowed by the permission guard ([permission-guard.sh:427-429](/Users/robertrhu/Projects/arhugula-v2/tools/hooks/permission-guard.sh:427)), and the test explicitly requires that behavior ([test_permission_guard.sh:167-169](/Users/robertrhu/Projects/arhugula-v2/tools/hooks/test_permission_guard.sh:167)). Phase 2 is too late.

2. **Run O1 before “fixing” X6.** The document calls X6 live, then puts the experiment that determines whether it is real after the proposed rewrite ([primer:187-202](/Users/robertrhu/Projects/arhugula-v2/.harness/council/loop-lanes-design-v1/03-codex-advisor/codex-primer.md:187)). Probe first.

3. **Probe reviewer concurrency before the pilots.** It is currently item 14, after the 3–4-lane pilots. Authentication or single-identity throttling could invalidate the pilots.

4. **Instrument before piloting.** Phase timing belongs before the first pilot, as proposed. Otherwise the most valuable baseline runs are lost.

5. **Narrow the queue lock.** “Flock across the full claim lifetime” would hold a global lock across `gh pr view` and `gh run list` calls ([arc_metrics.py:284](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:284), [arc_metrics.py:369-376](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:369)). Moving only `git show` outside the lock does not prevent one network-stalled lane from blocking all four. Lock filesystem transitions; rely on an ownership token while remote capture runs; reacquire and compare before restoring.

Move `arc_type`, the common finding schema, and most efficacy fields into Phase 1. Keep only identity fields needed for safety—`lane_id`, `arc_id`, branch, PR, base SHA—in Phase 0.

## 2. X1–X8

| Claim | Judgment |
|---|---|
| **X1** | **Real exposure; historical recurrence unverified.** `just codex-review` directly executes `codex review`; it checks login but never validates nonempty output or a terminal verdict ([justfile:569-592](/Users/robertrhu/Projects/arhugula-v2/justfile:569)). The Antigravity path validates completeness markers and final verdicts ([agy_review.py:436-446](/Users/robertrhu/Projects/arhugula-v2/tools/agy_review.py:436)). I did not inspect prior review transcripts, so I cannot independently verify that empty-success occurred live. |
| **X2** | **Overstated and not reproduced.** CI intentionally cancels superseded runs on the same ref ([ci.yml:42-45](/Users/robertrhu/Projects/arhugula-v2/.github/workflows/ci.yml:42)). Existing code already excludes non-success runs from green timing ([arc_metrics.py:270-277](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:270)), and `ship-pr` aborts unless post-merge CI equals `success` ([ship-pr/SKILL.md:199-204](/Users/robertrhu/Projects/arhugula-v2/.claude/skills/ship-pr/SKILL.md:199)). A live query returned **180/1,390**, not 190/1,390. A defect would require showing unattended cancellation of a current final head, not counting intentionally superseded runs. |
| **X3** | **Real, but phrased too broadly.** A tracked ledger being worktree-local is normal. The defect is using that local copy as global coordination state while the queue is shared: `LEDGER` derives from the worktree’s `__file__` root ([arc_metrics.py:44-45](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:44)); `QUEUE_DIR` is home-global ([arc_metrics.py:47-63](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:47)). |
| **X4** | **Real and primary.** The committed check sees only merged history ([arc_metrics.py:551-581](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:551)); the local check and duplicate guard see only the current lane’s ledger ([arc_metrics.py:696-712](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:696), [arc_metrics.py:408-415](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:408)); successful drain restores the shared queue entry ([arc_metrics.py:750-757](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:750)). I reproduced sequential A/B drains yielding the same `arc_id` once in each lane ledger, with no overlap. Existing tests cover simultaneous claiming against one ledger, not this cross-latency case ([test_arc_metrics.py:586-604](/Users/robertrhu/Projects/arhugula-v2/tools/test_arc_metrics.py:586)). |
| **X5** | **Race family real; stated outcome wrong.** Stale-claim deletion and retry are unlocked ([arc_metrics.py:617-627](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:617)); recovery’s `os.replace` is also unlocked and uncaught ([arc_metrics.py:659-667](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:659)). But on the cited `AbortError` path, `os.replace(taken, path)` occurs *before* `KEPT QUEUED` and `kept += 1` ([arc_metrics.py:742-748](/Users/robertrhu/Projects/arhugula-v2/tools/arc_metrics.py:742)). If it raises `FileNotFoundError`, the message and increment never happen. If it succeeds, something was written—the queue entry was restored. |
| **X6** | **Conditionally real, not proven live from repository code.** `hook_project_dir()` genuinely chooses either `CLAUDE_PROJECT_DIR` or the current git root ([lib.sh:17-23](/Users/robertrhu/Projects/arhugula-v2/tools/hooks/lib.sh:17)), and every marker/status path inherits that choice ([loop_lib.sh:18-40](/Users/robertrhu/Projects/arhugula-v2/tools/hooks/loop_lib.sh:18)). But repository code cannot prove what Claude injects into every raw-shell venue. O1 is needed before calling it a live defect. |
| **X7** | **Real, and understated.** Compose fixes the project name ([compose.yaml:1](/Users/robertrhu/Projects/arhugula-v2/deploy/self-hosted-local/compose.yaml:1)); host ports include 3200, 4317, 4318, **and 3000** ([compose.yaml:11-25](/Users/robertrhu/Projects/arhugula-v2/deploy/self-hosted-local/compose.yaml:11), [compose.yaml:41-42](/Users/robertrhu/Projects/arhugula-v2/deploy/self-hosted-local/compose.yaml:41)); the recipe supplies no project override ([justfile:468-479](/Users/robertrhu/Projects/arhugula-v2/justfile:468)). |
| **X8** | **Real; same underlying defect as X1.** No wrapper exists, while `agy_review.py` fails closed on missing marker, missing verdict, wrong model, timeout, or blocking verdict ([agy_review.py:521-533](/Users/robertrhu/Projects/arhugula-v2/tools/agy_review.py:521), [agy_review.py:598-607](/Users/robertrhu/Projects/arhugula-v2/tools/agy_review.py:598)). |

## 3. The most dangerous omission

**The merge door is advisory and unfenced.**

Today, any loop lane may execute raw `gh pr merge`; the permission guard auto-approves it. Live checks also confirmed `main` is unprotected and has no rulesets. A local lease therefore does not control the actual mutation boundary at GitHub.

Worse, the design proposes only a post-merge first-parent assertion. That detects a stale-base or double-landing after `main` has already changed. The context guard likewise detects resulting drift after the fact ([codex_context_guard.py:765-811](/Users/robertrhu/Projects/arhugula-v2/tools/codex_context_guard.py:765)).

Before four-lane pilots, Phase 0 needs:

- One fail-closed merge wrapper.
- Removal of raw `gh pr merge` from the allowlist.
- A lease generation/fencing token bound to lane, PR head, and verified base.
- Lease ownership through content merge, terminating refresh, and refresh CI.
- Remote enforcement—branch protection requiring an up-to-date base, or another GitHub-side base fence. A local pre-check alone retains a TOCTOU window.

Without remote enforcement, “safe and durable” is only true if every actor and process voluntarily obeys the same local file.

## 4. Internal inconsistencies

- “No merge-queue lock” conflicts with “one lease for the merge door.” That lease is a mutual-exclusion lock by another name ([primer:123-125](/Users/robertrhu/Projects/arhugula-v2/.harness/council/loop-lanes-design-v1/03-codex-advisor/codex-primer.md:123), [primer:217-218](/Users/robertrhu/Projects/arhugula-v2/.harness/council/loop-lanes-design-v1/03-codex-advisor/codex-primer.md:217), [primer:317-321](/Users/robertrhu/Projects/arhugula-v2/.harness/council/loop-lanes-design-v1/03-codex-advisor/codex-primer.md:317)).

- D-C settles automatic cross-vendor failover, while open decision 1 reopens whether the chain should remain single-vendor ([primer:107-110](/Users/robertrhu/Projects/arhugula-v2/.harness/council/loop-lanes-design-v1/03-codex-advisor/codex-primer.md:107), [primer:305-310](/Users/robertrhu/Projects/arhugula-v2/.harness/council/loop-lanes-design-v1/03-codex-advisor/codex-primer.md:305)).

- Phase 0 states a 24-hour TTL, while §9 says that TTL is unratified.

- Phase 1 mandates three pilots, while §9 says whether that gate applies is still open.

- “Manual pilots with zero new machinery” follows a Phase 0 containing reservations, flock, marker redesign, Docker isolation, and detections.

- “Effectively zero detections” is false for refresh collision: the guard emits a stable `ROADMAP_STATUS_DRIFT` finding and supports machine-readable JSON ([codex_context_guard.py:774-810](/Users/robertrhu/Projects/arhugula-v2/tools/codex_context_guard.py:774), [codex_context_guard.py:928-960](/Users/robertrhu/Projects/arhugula-v2/tools/codex_context_guard.py:928)).

- Global HIL reduction by “max timestamp” is nondeterministic. Current timestamps have only one-second precision ([loop_lib.sh:43-44](/Users/robertrhu/Projects/arhugula-v2/tools/hooks/loop_lib.sh:43)); two lanes can defer/resolve the same item in the same second. Use a CAS generation or explicit event sequence, not timestamp alone.

## 5. Cuts and omissions

Cut or move off the safety path:

- The 172-pair O3 retrospective. It measures textual conflicts in a historical serial workload and cannot measure semantic conflict. Run `merge-tree` prospectively on the actual chosen lane set instead.
- D-D shadow evaluation from this build’s critical path. Keep it as the separately ratified efficiency experiment.
- Common finding-schema work and `arc_type` pre-registration from Phase 0; move them to measurement.
- Full-lifetime flock. Replace it with short critical sections around queue transitions.
- Blanket “`gc.auto 0` per lane” until the exact command scope is specified. This checkout does not have `extensions.worktreeConfig`; ordinary repository config is shared, not lane-local.

Missing entirely:

- An arc-open work reservation preventing duplicate scheduling of the same roadmap unit.
- A durable landing state machine: `LEASED → MERGED → REFRESHED → REFRESH_CI_GREEN → RELEASED`, resumable after process death or lost GitHub responses.
- Fencing against stale lease holders and PID reuse.
- Atomic global HIL event publication and deterministic conflict resolution.
- A distinction between expected superseded CI cancellations and unexpected cancellation of the final head.
- Four-process kill/restart tests covering every queue and landing transition, not only in-process threads.
- A prospective lane-selection/scope-conflict gate. The existing two-lane recipe still relies on manual non-overlap selection ([two-lane/SKILL.md:14-19](/Users/robertrhu/Projects/arhugula-v2/.claude/skills/two-lane/SKILL.md:14)).

Verification: `uv run pytest tools/test_arc_metrics.py tools/test_arc_exit_report.py -q` passed, **133 tests**. I made no edits. `graft` was unavailable, so I used targeted source inspection. I deliberately did not read the prior council contributions or prior Codex evaluation.
