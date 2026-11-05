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
reviewer session. The reviewer may use the author's model family. Neither the
author nor any material correction author may approve their own changes. Retain
normal permissions, authentication and fail-closed verdict parsing; no paid API
fallback. Gemini/Antigravity, vendor diversity, automatic fallback and shadow
review are not required. Preserve actual denials; a policy change does not retry
a rejected disclosure.

Use the verified registered native reviewer when available. Record every material
author session, including predecessor and correction authors, in the existing
claim. Attest the frozen preflight through the existing gate. With the actual
reviewer's native transcript and that author list, run:

```bash
uv run python tools/native_review.py binding --transcript <native-transcript> --authors <author-session> <correction-author-session> --base origin/main
```

Give the reviewer those six immutable binding values, the exact frozen candidate,
and the existing review request. The reviewer inspects the diff and surrounding
code read-only, records its evidence in LIT, and ends its native turn with ONE
fenced JSON verdict matching `tools/review_schemas/codex.schema.json` and the six
binding values. Do not write a verdict for the reviewer or substitute tool output
for its final answer. After that native turn actually completes, import it:

```bash
HARNESS_ARC_ID=<arc-id> HARNESS_LANE_ID=<lane-id> HARNESS_CYCLE_PASS=initial uv run python tools/native_review.py record --transcript <native-transcript> --authors <author-session> <correction-author-session> --base origin/main
```

The adapter derives the reviewer UUID and final answer from the actual completed
native transcript, binds the author list, and uses the existing schema, cycle
admission, canonical finding log and round accounting. Keep the actual Codex
producer provenance; do not label it Gemini to pass a family test. Correction
review uses `HARNESS_CYCLE_PASS=correction` and the previous reviewed head as
`--base`; add new material authors without dropping previous ones.

If unrelated later activity has started in that session, `record` accepts
`--turn-id <native-turn-uuid>` to select the actual completed review turn. The
adapter reports that turn's own model, checks the same six bindings and author
independence, and refuses a later verdict on the same candidate. Without the
option the latest completed turn remains the only eligible final. Keep the native
transcript and selected turn ID in the existing review evidence.

An unreserved arc that no trial unit enrolls has no cycle to tag. Import its
reviewer's final with the pass unset and the arc named explicitly:

```bash
HARNESS_ARC_ID=<arc-id> HARNESS_LANE_ID=<lane-id> uv run python tools/native_review.py record --transcript <native-transcript> --authors <author-session> <correction-author-session> --base origin/main
```

The adapter refuses this route unless all of these hold:
- the arc has no reservation;
- the reviewed head's committed policy selects this delivery setting and does not
  enroll the arc;
- the gate log holds no tagged row for the arc;
- this reviewer's verdict on this head and digest is not already recorded.

It appends one untagged row bound to the six values, the reviewer and every
material author, under the log lock. That row is the record of the independent
review and nothing more: it completes no cycle pass, reserves nothing and does
not authorize landing. Landing still needs the merge gate, required CI and the
safe wrapper. A reserved arc, or one with cycle history, keeps its tagged passes.

A separately launched subscription wrapper remains an optional independent
review route where that launch is authorized: `just review-cycle-pass initial
<round-log> origin/main`, with the existing arc/lane IDs. Initial/correction passes
do not invoke Gemini fallback when the selected reviewer is unavailable. Untagged
reviews do not complete the cycle. Recorded legacy verdicts, findings and spent
passes remain evidence; they do not require a future Gemini launch.

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

For an existing stacked PR, complete the normal final-head checks first, then
use `uv run python tools/stacked_pr_publish.py <pr> --old-head <remote-sha>
--final-head <checked-sha>` to retarget to main before publishing the final
fast-forward head. The tool checks the live PR and refuses a changed head or a
non-fast-forward update. A changed base still requires an exact matching CI
binding; confirm the final synchronize run and required PR checks actually appear.
The ordering does not establish GitHub's internal check-association behavior.

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
