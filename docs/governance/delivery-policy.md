# Approved delivery procedure

The user's 2026-11-04 delivery correction is implemented by
`.harness/workflow-policy.json` → `review_rules.delivery` =
`single-independent-milestone-status-v1`. This is a tracked delivery setting,
not activation of an experimental trial unit. The setting replaces the default
review stack, duplicate local full-suite requirement and separate status PR cycle.

Use this procedure for an arc with no delivered legacy cycle. An arc whose
canonical review rows already contain pass `1`, `2`, `esc` or `3` retains that
cycle, its findings and spent passes; use the legacy procedure for its review.
The merge door also retains an already recorded refresh intent. A policy change
must not erase in-flight obligations.

## Build and verify

Keep the existing claim, isolated worktree, lane and reservation. Record the
owned paths, exact base, behavior, independent reviewer and next consuming gate.
Build runnable behavior and discriminating tests together. Ratified witness or
prose corrections go directly between author and reviewer; a changed normative
contract still needs its applicable ratification. Do not send unchanged behavior
through another Buford approval round.

Storage gates implementation acceptance and resume exposure at Runtime B7 item 4.
Explicitly claimed inactive source/tests and independent review may proceed with
provisional inputs while storage is established. Temporary-root tests establish
behavior, not installed storage or acceptance.

Run focused local behavioral tests and static checks for changed inputs, plus
required deterministic closeout checks. Reuse qualifying unchanged evidence with
an explicit input/impact disposition. Required remote CI on the actual candidate
remains mandatory; an equivalent full local suite followed by remote CI is not a
mandatory sequence. A failure needs resolution or an accepted disposition.

## One independent review

Freeze the candidate and evidence before review. The default is ONE independent
reviewer: Claude-authored code uses the Codex wrapper; Codex-authored code uses
`just gemini-review` through the authorized Antigravity subscription. Retain normal
permissions, authentication and fail-closed verdict parsing; no paid API fallback.
A reviewer must not approve its own authored correction.

Attest the existing preflight once, then launch with the existing arc/lane IDs:

- Claude author: `just review-cycle-pass initial <round-log> origin/main`.
- Codex author: `HARNESS_CYCLE_PASS=initial just gemini-review origin/main`.

Set `HARNESS_ARC_ID` and `HARNESS_LANE_ID` for either command. The wrappers emit
`initial`/`correction` tags into the same canonical finding log. Untagged reviews
are not cycle completion. Record independent verdicts and evidence in existing
LIT records; wrapper rows and LIT serve their existing distinct purposes.

Return findings together. Adjudicate each through the existing append-only
mechanism; fix accepted P1/P2 findings together and commit before correction
review. Review the correction and affected regressions with pass `correction`
against the previous reviewed head. Use a full-diff correction only when changed
scope or behavior warrants it; state that impact in the review request. Retain
qualifying unchanged proof, all original findings and spent passes. The original
budget and repeated-P1 stop remain; a context refresh grants no extra passes.

A clean initial review completes review. No automatic second artifact reviewer,
three-lens pass, final lens, or shadow experiment is owed. Add specialty review
only for a named unresolved risk, with its question and disposition in the same
claim. Do not add a specialist merely because the files are code. A real new
finding is still addressed before accepting the affected behavior.

Freeze the reviewed worktree while a reviewer reads it. Independent isolated
work can continue during review and CI. Reconcile actual overlap at Git gates;
re-establish affected review and CI on the resulting candidate.

## Land and report

Publish the owned feature branch/PR after the applicable frozen review. Preserve
required final-head/base CI, the attested merge tree and the holder-bound safe
merge wrapper. A gate-log-only commit may transfer review only through the
existing landing-delta proof. Do not use raw `gh pr merge` or `--admin`.

The safe wrapper reads the tracked refresh posture. Under this setting it lands
without a separate roadmap refresh PR, waits for the merge SHA's successful
own-main CI, publishes the landing receipt and releases its door. Red or missing
CI still blocks landing/release. CI waiting holds that transition; independently
admitted work in isolated worktrees continues.

Generate current Git/PR state with `just roadmap-status --state`; use canonical
live LIT for claims, ownership, blockers and acceptance. `roadmap_status.md` is a
milestone snapshot. Refresh it at a meaningful milestone in the next substantive
change, using the existing generator and an explicit current next-action pointer.
Do not open a separate status-only PR or require its PR/main CI cycle for every
content landing. The legacy shape checks remain for deliberately requested or
already started refresh continuations.

After actual landing/own-main success, keep source delivery, integration and
installed acceptance separate. Run the existing reflection/context-save-lean and
arc-close/metrics capture once for the completed content arc; do not fabricate
transcript cost data. Queue metrics outside the worktree and drain through the
next content PR. Close the full task only after its installed acceptance,
recovery proof and independent release decision are satisfied. Schedule eligible
cleanup separately after ownership/evidence release; protect dirty work and
local main. No cleanup or local-main synchronization blocks independent delivery.
