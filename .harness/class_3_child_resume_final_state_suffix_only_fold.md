# Class 3 (informational) — resumed-child `final_state` is suffix-only → corrupts a folded fan-out branch output

**Filed:** 2026-06-25 (surfaced by out-of-family Codex round 2 on the `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` build; verified empirically + advisor-reconciled).
**Class:** 3 (informational — non-blocking observation requiring documentation; routes to a follow-on build, not an operator halt).
**Status:** OPEN — registered as a blocking prerequisite of `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT`.

## The finding

On a crash-resume, `execute_workflow` rebuilds `RunResult.final_state` ONLY from steps executed in the NEW envelope: `accumulated` is initialized empty (`harness-cp/src/harness_cp/workflow_driver.py:3165`) and populated per executed step (`:3851`); `final_state=dict(accumulated)` (`:3886`). The recovered prefix steps (`0..resume_at-1`) are rehydrated into the inter-step output CHANNEL (`_rehydrate_replay_prefix`, `:1145+`, so downstream steps read upstream outputs) but are NEVER seeded into `accumulated`. So **every resumed workflow returns a suffix-only `final_state`** (empty if all steps were committed before the crash).

For a TOP-LEVEL workflow resume this may be tolerable (the operator reads the prefix from the store/ledger). But when a resumed workflow's `final_state` is **folded as a fan-out branch output** — the maybe-ran SUB_AGENT_DISPATCH recovery, AND the existing **B-HIERARCHICAL-PAUSE captured-child-resume** — the parent records/folds incomplete/empty branch output → **corrupted aggregate**. The recovery's at-most-once (effects) holds; the RESULT is corrupted.

## Two consequences

1. **Pre-existing latent defect (cleared code):** the existing B-HIERARCHICAL-PAUSE captured-child-resume fold (`SubAgentChildPausedError` → re-enter child via `child_resume_snapshot` → fold the resumed child's `final_state`) ALSO returns suffix-only output. Not introduced by this arc; surfaced by it. Needs its own assessment/fix.
2. **Blocking prerequisite for `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT`:** the maybe-ran SUB_AGENT recovery cannot close until a resumed child returns its FULL `final_state`.

## The fix (a follow-on arc — own design-first cycle)

**`B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT`** (proposed) — seed `accumulated` from the recovered store outputs (`read_outputs(run_idempotency_key)`, already read by `_rehydrate_replay_prefix`) on auto-resume, so a resumed workflow returns its full `final_state`. An all-workflows crash-resume change → needs: a witness (resumed-linear `final_state` == no-crash run), its own out-of-family Codex round (fresh edges: step_id collisions when seeding `accumulated`; the one-extra-uncommitted store step `_rehydrate` already filters), and advisor confirmation of: (a) no runtime-spec clause specifies suffix-only resume `final_state`; (b) no existing test depends on suffix-only; (c) `read_outputs` holds the recovered prefix for BOTH `WAL_SEGMENT` + `EVENT_SOURCED_REPLAY`.

Once this lands, `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` closes on top (the deterministic-identity + replay-marker + classifier-disjunct + the round-1 resumed-replay-guard, all on branch `feat/b-fanout-maybe-ran-subagent`, become mergeable).

## Decorrelated review trail

- out-of-family Codex round 1 → [P1] double-fire (resumed-manifest replay-capability unchecked) → FIXED on branch (require replay-capable BOTH dispatch + resumed).
- out-of-family Codex round 2 → [P1] result-corruption (this finding) → arc narrowed (does not close; prerequisite registered).
- advisor (full-transcript) → confirmed Option C (document-and-proceed) ships corruption; the empty-`final_state` case is the central scenario; narrow now per "any doubt → narrow, lose nothing real."
