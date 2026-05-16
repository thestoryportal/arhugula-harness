# Class 1 Tension — CP axis-stream scope discrepancy (final-batch brief)

**Filed:** 2026-05-16 — Phase 7 sub-phase 7b, CP axis-stream final batch.
**Defect class:** Class 1 — task-brief / actual-state mismatch surfaced at
execution-time. Routes to operator for re-scoping of the CP residual.

## Defect

The final-batch implementer brief stated: "Land the FINAL CP units — the 9
not-yet-coded CP units: U-CP-32, U-CP-33, U-CP-35, U-CP-36, U-CP-43, U-CP-46,
U-CP-50, U-CP-53, U-CP-55. This is the last batch — landing these completes
the CP axis stream."

That is incorrect. Verified against `git log` (authoritative) at session start:

- **CP units actually landed before this batch: 40** — U-CP-00, 00b, 00c,
  01, 02, 04-26 (except 03/27), 28, 29, 30, 31, 34, 37, 38, 40, 42, 44, 47, 48.
- **CP plan total: 57 units** (`harness-cp/CLAUDE.md` §1.2 / §3.1).
- **Residual at session start: 17 units**, not 9 — the brief's 9 plus a
  silently-dropped set of 8: **U-CP-03, U-CP-27, U-CP-39, U-CP-41, U-CP-45,
  U-CP-49, U-CP-51, U-CP-54** (+ U-CP-52, which the brief listed as landed but
  has no source file — see below). The brief's "State" section claimed
  "U-CP-00..00c, 01..02, 04..31, 34, 37..42, 44..49, 51, 52, 54" were landed;
  git log contradicts this for U-CP-03, 27, 39, 41, 43, 45, 46, 49, 50, 51, 52,
  53, 54, 55.

The pre-existing workspace task list ("Phase C — land 15 deferred consumers +
U-CP-55") reflects the *real* residual shape; the 9-unit brief under-counted.

## Consequence for this batch

Of the 9 brief units, only 4 had all dependencies satisfied by landed units
(+ in-batch units):

| Unit | Status | Blocking dependency |
|---|---|---|
| U-CP-35 | ✅ landed | — (deps 22, 34, U-IS-07/12 all landed) |
| U-CP-43 | ⚠️ partial-landed | — (deps landed; struck floors are spec-silence — separate record) |
| U-CP-36 | ✅ landed | — (deps 31, 34, 35, 42; acc #5 delegates to unlanded U-CP-45) |
| U-CP-53 | ✅ landed | — (deps 06,08,09,16,17,24,25,43, U-AS-14 all landed) |
| U-CP-46 | 🛑 BLOCKED | depends on U-CP-45 (not landed, not in batch) |
| U-CP-32 | 🛑 BLOCKED | depends on U-CP-46 (transitively → U-CP-45) |
| U-CP-33 | 🛑 BLOCKED | depends on U-CP-32 (transitively → U-CP-46 → U-CP-45) |
| U-CP-50 | 🛑 BLOCKED | depends on U-CP-49 (not landed, not in batch) |
| U-CP-55 | 🛑 BLOCKED | terminal exporter; depends on U-CP-27, U-CP-51, U-CP-54 (none landed) |

The 5 blocked units are **whole-unit blocked on missing dependency *units***,
not missing types. This is NOT the halt-route-split-AC pattern (which is for a
bad AC inside an otherwise-materializable unit). Implementing the missing
units to unblock them would be an X-AL-3 silent design extension. They are
left unlanded.

## Residual after this batch

CP units NOT landed (14): **U-CP-03, U-CP-27, U-CP-32, U-CP-33, U-CP-39,
U-CP-41, U-CP-45, U-CP-46, U-CP-49, U-CP-50, U-CP-51, U-CP-52, U-CP-54,
U-CP-55.**

Landed CP units after this batch: 44 of 57 (40 prior + U-CP-35/36/53 +
U-CP-43 partial).

**The CP axis stream is NOT COMPLETE.** No `chore(7b): CP axis-stream
COMPLETE` commit was filed — that would misrepresent the state.

## Dependency-unblock order for the residual

A future batch can land the 14 in this topological order (deps now satisfiable
once the predecessor lands):

1. U-CP-03 (L0 — per-layer time-budget; cross-axis-only deps)
2. U-CP-27, U-CP-39, U-CP-41 (L-mid — deps now landed)
3. U-CP-45 (deps 42, 43, 44, 47 — all landed after this batch)
4. U-CP-46 (deps 37, 38, 42, 43, 44, 45, 47 — clears once 45 lands)
5. U-CP-32 (deps 10, 12, 31, 46, U-AS-17/31 — clears once 46 lands)
6. U-CP-33 (deps 32, U-AS-31, U-IS-01/02 — clears once 32 lands)
7. U-CP-49 (C-CP-21 pause/resume — verify its own dep set)
8. U-CP-50 (deps 30, 49, … — clears once 49 lands)
9. U-CP-51, U-CP-52 (L7 — verify dep sets)
10. U-CP-54 (CP namespace export manifest)
11. U-CP-55 (terminal aggregate exporter — depends on 27, 51, 53, 54; LAST)

## Routing target

Operator — re-scope the CP residual as a follow-on 7b batch covering the 14
unlanded units in the order above. No design-phase artifact revision is
required for the scope discrepancy itself (the plan is correct; the brief
under-counted). The two substantive design-phase items surfaced during the
batch are tracked separately:
  - `class_1_tension_u_cp_43_spec_silent_floors.md` — §19.1 spec-silence on
    the MCP_TRUST / DEPLOYMENT_SURFACE gate-level floors.
  - U-CP-36 acc #5 / U-CP-55 — within-axis forward references to unlanded
    units (resolve when those units land; no design defect).

**Status:** OPEN — CP axis stream incomplete; 14 units deferred to a follow-on
batch.
