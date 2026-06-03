---
name: self-heal
description: Drive the test suite to a verified green fixed point — clear caches, run the full suite, root-cause each failure as environment-artifact vs genuine logic defect, fix the logic, re-run until stable. Use when the operator says "/self-heal", "get the suite green", "tests are flaky", "fix the build", or after a merge/rebase leaves failures. Surfaces only real logic defects (with a repro), not env noise. Do NOT use to add features — only to restore/verify green.
---

# self-heal — test-anchored self-healing (U-HK-24)

Loop the workspace to a *verified* green, distinguishing real defects from environment
artifacts so the operator only sees genuine bugs.

## The loop

1. **Clear environment artifacts FIRST (§14.3).** Stale bytecode/build caches are the #1
   cause of phantom failures (the `.pyc` that once nearly drove a wrong fork conclusion).
   ```bash
   find . -path ./.git -prune -o \( -name '__pycache__' -o -name '*.pyc' \) -print0 2>/dev/null | xargs -0 rm -rf
   ```
   (The Wave-1 `precmd-clear-cache.sh` hook does this per-Bash; do it explicitly here too.)
2. **Run the suite.** `just check` (lint + typecheck + `uv run pytest`, mechanism-α only —
   β/γ skip without credentials, by design). For a targeted area, `just test-one <path>`.
   The hook test suites: `for t in tools/hooks/test_*.sh; do bash "$t"; done`.
3. **Triage each failure — env-artifact vs logic:**
   - **Env-artifact** (re-run cleanly after cache-clear / is timing-flaky / needs a cred the
     suite is meant to skip / stale lockfile): NOT a logic defect. Re-run once after
     clearing; if it passes, it was an artifact — note it, don't "fix" it. Known flaky:
     `[[ci-flaky-flush-to-sqlite-perf-test]]` (timing). A test that requires a paid
     credential is a *skip*, not a failure — never fire a paid call to make it pass
     (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`).
   - **Genuine logic defect** (fails deterministically across clean re-runs; the assertion
     encodes a real contract): this is the one to fix.
4. **Fix the logic** (posture-correct per §11; design-substrate is out of scope — a failing
   test against a spec contract may be a Class 1 fork, route per §4.3, do not silently edit
   the spec). Call `advisor()` before a non-trivial fix (§13.1).
5. **Re-run to a fixed point.** Repeat 1–4 until two consecutive clean runs agree (green, or
   the only reds are documented env-artifacts/credential-skips). Bound the loop — if it will
   not converge after a few passes, STOP and surface the sticking failure with its repro;
   do not thrash.

## What to surface

- **Real logic defect found + fixed:** report it with the repro + the fix + the green re-run.
- **Real defect found, fix is non-trivial / cross-axis / spec-implicating:** STOP, surface it
  with the repro + the routing recommendation (Class 1 fork? §4.3). Don't force a fix.
- **All reds were env-artifacts/skips:** report "green after cache-clear; N credential-skips,
  M known-flaky" — honest, not "all tests pass" when some merely skipped (§ report faithfully).

## Notes

- The discriminator is **deterministic-across-clean-runs**: env artifacts wash out after a
  cache-clear + re-run; logic defects survive it. Verify the observation layer before
  concluding a defect (`[[feedback-verify-observation-layer-before-concluding-defect]]`).
- Pairs with the Wave-1 cache-clear hook (U-HK-03) + the Stop test/lint gate (U-HK-10).
