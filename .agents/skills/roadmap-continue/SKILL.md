---
name: roadmap-continue
description: Use when the operator says /roadmap-continue, continue, next action, drive the roadmap, or asks Codex to advance the next arhugula-v2 item end to end.
---

# Roadmap Continue

Run the live roadmap loop through a verified fixed point. The canonical authorities are
`AGENTS.md`, live `CLAUDE.md` §12, `.harness/roadmap_status.md`, and the current handoff;
check them rather than trusting remembered or checkpointed remaining work.

## Grounding

1. Verify absolute root, current branch, worktree registration, and status. Run
   `just codex-preflight`; re-run it after a resume, merge, rebase, or compaction.
2. Read `.harness/handoff/README-resume.md` for in-flight cross-runner state, then the
   current roadmap status and relevant register/axis guidance.
3. Treat gstack context-save checkpoints as decision/evidence aids, not current-state
   authority. Reconcile their branch/PR claims against HEAD and GitHub.
4. Take the live `## Next action`. If the automatic queue is empty, apply no-parking:
   choose the highest-value implementable forward slice. A nominally gated item still owes
   grounding and every buildable slice up to the genuine credential/operator boundary.
5. Resolve formal cites with the `overlay-query` skill. Trace runtime premises to shipped
   call sites; a resolving cite proves presence, not reachability or correctness.

## Execute one arc

1. Create or reuse a clean isolated worktree based on current `main`. Never edit the shared
   root checkout. Run `just codex-autonomous-arc <arc-id>` in that worktree.
2. Record a concise plan with owned files, authority, RED witness, verification, and tracking
   surfaces. If code contradicts the arc premise, stop and classify instead of reworking the
   premise to save the arc.
3. Write or preserve the failing witness and record `red` with `status=failed`. Implement
   the smallest posture-correct slice; never mix `design-substrate/**` and implementation
   without an explicit back-flow arc.
4. Recount any stated condition/cardinality set programmatically after every review round.
5. Run narrow verification, then `just codex-check`; add `just overlay-check`, shell tests,
   or live/integration checks when the claim requires them.
6. Grounding pass (U-WT-01) first: re-read every `file:line` cite at HEAD, recompute
   every count/arithmetic claim from source, verify every `#NNN` reference is the PR it
   claims. Then, for a Codex-authored diff, use Antigravity through `just gemini-review` as the
   out-of-family reviewer under the operator's standing all-forward-work authorization; do
   not request per-run approval. This review uses the OAuth-authenticated `agy` CLI only—never
   provider API keys, service-account/Vertex routing, or a direct API call. For a Claude-authored
   diff, use `just codex-review`. Validate
   exit status, non-empty output, and the final verdict before recording the review gate.
7. Run `just codex-closeout`, then hand the complete arc to the `ship-pr` skill.

## Genuine gates only

Ask only for an architectural/product choice that is the operator's, a credential or paid
call, or an irreversible/outward action not already authorized. Build to that boundary and
record the deferral with the repo wrapper. Reversible in-repo choices are resolved and
reported; do not park on them.

## Before the next arc

The current arc is not complete at PR CI. `ship-pr` must finish the fresh three-lens gate,
merge if authorized, wait for the substantive merge's main CI, land the immediate terminating
refresh, wait for refresh main CI, sync main, dispose of the worktree/verified merged branch,
run `just codex-loop-check`, reflect, and run the gstack `context-save` skill. Only then derive
the next live action, create its isolated worktree, and start its new autonomous-arc ledger.

If no forward slice remains after honest grounding, report the exact gate and resume command;
do not invent work or silently stop an authorized loop.
