# optimize-claude-md self-improvement loop — runbook

Run via **skill-creator, in this environment, NO API**. The in-session agent does the
skill-execution and the one-change proposal; promptfoo (deterministic, **zero model calls**) is
the grader. All iterations run in the isolated worktree (`.claude/worktrees/optimize-claude-md-loop`)
so churn never touches main. This is the dev-tool eval of the SKILL — NOT the product's
governance acceptance gate (that stays the human WS-0 drift matrix per architecture.md AD-19/R1/R2).

## Invocation (operator)
Invoke skill-creator with the loop intent, pointed at this harness as the fitness function:
> Use skill-creator to self-improve `.claude/skills/optimize-claude-md/SKILL.md`. The fitness
> function is `evals/promptfoo/` (deterministic, no API). Follow `evals/promptfoo/LOOP.md` each
> cycle. Do NOT stop to ask; loop until I interrupt or the score is perfect.

## Per-iteration procedure (the agent follows this each cycle)
1. **Run the skill on each fixture (in-session, no API).** For each case in `tests/*.yaml`, apply
   the CURRENT `SKILL.md` discipline to `fixtures/<case>.md` and write the result to
   `outputs/<case>.json` per the contract at the top of `assertions.py`
   (`{before, after, new_files, touched_paths}`). When the skill leaves a resolving pointer to a
   relocation home, also write that home file to disk so `pointers_resolve` can resolve it.
2. **Grade (deterministic, no model call):**
   `PROMPTFOO_PYTHON=$(command -v python3) npx promptfoo@latest eval -c promptfooconfig.yaml \
     --no-cache --no-share -o out.json`
3. **Score:** `python3 score.py out.json` → `{hard_gates_all_pass, score, pass_rate, fails}`.
4. **Keep or discard (loop-level anti-Goodhart):**
   - Keep ONLY IF `hard_gates_all_pass` is true AND `score` strictly improved over the last kept
     score → make the ONE `SKILL.md` change durable with `git commit`.
   - Otherwise discard: `git checkout -- ../../SKILL.md` (restore the prior SKILL.md).
   - **NEVER keep a change that fails any hard gate**, regardless of `pass_rate`. A guardrail drop
     is the exact failure this skill exists to prevent.
5. **Propose the next ONE change** (Karpathy §3 surgical, §2 simplicity, §1 state the assumption):
   a single scoped `SKILL.md` edit targeting a failing/low-scoring metric in `fails`.
6. **Log** one line to `outputs/loop-log.jsonl`: `{iter, score, pass_rate, kept, change}`.
7. Repeat until interrupted or `pass_rate == 1.0` with `hard_gates_all_pass`.

## Why this is safe to run unattended
- The grader is deterministic and the hard gates are a veto — a bad change (dropped guardrail,
  broken pointer, out-of-scope write) **cannot** improve the score; it is auto-discarded.
- Commits land on the worktree branch only; the converged result lands as a **reviewable PR**
  (propose-don't-dispose). `outputs/` + `out.json` are gitignored ephemera.
- Zero model API calls: the skill-execution + proposal are in-session; promptfoo only runs the
  python assertions. (The qualitative "is the prose clear?" judgment, if wanted, is the agent's,
  logged outside promptfoo — no metered llm-rubric.)

## Files
- `assertions.py` — the deterministic fitness gates (+ the output contract, at the top).
- `provider.py` — file-reader provider (returns `outputs/<case>.json`; no model call).
- `promptfooconfig.yaml` — the deterministic suite (5 gates; hard gates weight 5).
- `fixtures/` + `tests/` — frozen reproducible inputs (relocation + adversarial-guardrail trap).
- `score.py` — score extractor + the hard-gate veto used by step 4.
