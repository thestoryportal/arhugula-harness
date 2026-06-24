# Class 1 Fork — fan-out crash-resume recovery is not cascade-policy-aware

*Filed 2026-06-24 during the R-FS-1 `B-FANOUT-OUTPUT-REPLAY` PR1 build. Back-flow finding (X-AL-3 / `Project_Workflow_v1_8.md` §2.7.6 Class 1): the operator-ratified recovery MECHANISM is under-scoped versus what correct crash-resume requires. This is a design-phase fact, not an impl bug. PR1 fails closed at the boundary; the fix is a registered follow-on.*

## The ratified mechanism

The §25.12-D1 council (#719) + operator ratification (A, #721) approved a fan-out crash-resume recovery that **"reuses the existing B-FANOUT-PAUSE recovery path VERBATIM — only the snapshot SOURCE differs"** (`.harness/r-fs-1-b-fanout-output-replay-impl-design.md` §The seam; CP spec v1.55 §2). The design's load-bearing claim: a crash-resume reconstructs the same `FanOutResumeState` / `PeerFanOutResumeState` the pause path uses, then runs the existing skip-terminal + recover-outputs + re-dispatch-incomplete recovery.

## What the build surfaced (out-of-family Codex, 6 review rounds)

The recovery path is **blind to `cascade_policy`**, but the three policies carry DIFFERENT committed on-failure semantics (C-CP-25 §25.15.1, persona-tier-derived):

| cascade_policy | persona tier | on a branch failure | crash-resume under the cascade-blind recovery |
|---|---|---|---|
| `PROCEED` | SOLO_DEVELOPER | siblings run to completion → PARTIAL (degraded harvest) | **correct** — recover completed, re-dispatch absent, degraded→PARTIAL |
| `PAUSE` | TEAM_BINDING | capture a resumable PauseSnapshot → PAUSED | a crash has no PauseSnapshot; the recovery would resume a fan-out the policy intended to PAUSE |
| `CASCADE_CANCEL` | MULTI_TENANT_COMPLIANCE | cancel siblings → **FAILED** | the recovery would **re-run deliberately-cancelled siblings** and report **PARTIAL where the contract says FAILED** — a wrong, less-safe result on the compliance tier |

"Reuse the pause-resume path verbatim" is therefore **correct only for `PROCEED`**. For PAUSE + CASCADE_CANCEL the cascade-blind recovery produces a semantically-wrong outcome — the root generator behind the round-5/round-6 cascade-policy findings (it is not one bug; it is a missing design dimension).

## The decision

Correct crash-resume requires **per-cascade-policy recovery semantics** — a design surface the ratified "reuse verbatim" mechanism did not contemplate. That is a Class-1 architectural extension, NOT a Phase-7 silent absorption.

- **PR1 (this build) fails CLOSED at the boundary** — crash-resume recovery is gated to `CascadePolicy.PROCEED`; PAUSE + CASCADE_CANCEL return `RunStatus.FAILED` with `fan-out-crash-resume-cascade-policy-unsupported` (the same fail-open→fail-closed move PR1 already makes for synthesis-bearing and timed-out crash-resume). Witnessed at `test_crash_resume_cascade_cancel_fails_closed`. This is the conservative, reversible, in-repo scoping decision the build resolved itself.
- **The follow-on** — cascade-policy-aware fan-out crash-resume recovery (PAUSE: reconstruct a resumable halt or restart-fresh; CASCADE_CANCEL: recover the cancel outcome → FAILED, do NOT re-run cancelled siblings) — is registered alongside the already-planned PR2 (synthesis self-hash + replay) as a forward `B-*` arc. It carries its own design vet (the cascade semantics interact with the §25.15 cascade contract + the sibling-re-dispatch question Codex's review glimpsed) before build.

## Scope boundary (what PR1 DOES deliver, correctly)

The `PROCEED` fan-out crash-resume IS complete + witnessed: disposition recovery (completed-with-output → fold; completed-no-output errored → recover-as-terminal; timed-out → fail-closed), ledger re-materialization, the orchestrator-as-authority + changed-topology + changed-cardinality fail-closed guards, and the synthesis-crash fail-closed (PR2 relaxes it). The at-most-once class is closed for PROCEED; PAUSE + CASCADE_CANCEL are fail-closed pending the registered follow-on.

## Filing

| Field | Value |
|---|---|
| Class | 1 (architectural — ratified mechanism under-scoped) |
| Surfaced at | R-FS-1 `B-FANOUT-OUTPUT-REPLAY` PR1 build, 2026-06-24 (out-of-family Codex rounds 5-6 + advisor) |
| PR1 disposition | fail-closed for PAUSE + CASCADE_CANCEL (gated to PROCEED); witnessed |
| Follow-on | `B-FANOUT-CRASH-RESUME-CASCADE-POLICY` — cascade-policy-aware recovery (register in the SPINE/arc ledger alongside PR2) |
| Anchors | `.harness/r-fs-1-b-fanout-output-replay-impl-design.md`; CP spec v1.55 §2-§3; `[[spine-ledger-forward-arc-registration]]`; `[[grounding-reveals-claude-closeable-slice-close-honestly]]` |
