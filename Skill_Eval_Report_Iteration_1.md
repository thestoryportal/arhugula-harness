# Skill Eval Report — Iteration 1 (eval-as-is)

*Phase 7 skill-eval sub-project, task 3. Companion to `Skill_Adaptation_Analysis_v1.md`.*
*Date: 2026-05-15. Protocol: skill-creator run loop — 7 cases × {with-skill, baseline} = 14 subagents, spawned in one turn.*

## Scope

Eval-as-is run of the 2 operator-provided authoring skills judged "mostly right" in
the adaptation analysis: `harness-adversarial-reviewer` (4 cases) and
`implementation-planner` (3 cases). `systems-architect` and `spec-writer` were
deliberately NOT eval'd as-is (eval-as-is on near-rewrite targets = near-zero info);
they are adapted first, then eval'd in iteration 2.

With-skill mechanism: subagent instructed to Read the SKILL.md as its first action
and follow it as binding executable instructions. Baseline: same prompt, no skill.

## Verdict

**Both skills confirmed "mostly right." Calibration signal is real** — the calibration
evals (adv 0/1) show the skill reliably catches the two hand-found tensions, and the
discrimination vs baseline is rigor-of-output, not detection. Eval-as-is was the
correct call for these two.

## Results — harness-adversarial-reviewer

| Eval | What it tests | Result | Discrimination |
|---|---|---|---|
| 0 calibration-tension-001 | catch C-IS-03 §3 count drift | **PASS** | both caught the drift; with-skill = 3 classified findings + rejected-findings section; baseline = 13 unfiltered findings, **no** rejected section |
| 1 calibration-tension-002 | catch TopologyPattern enum divergence | **PASS** | both caught it; with-skill classified + recommended disposition + rejected section; baseline no rejected section |
| 2 env-fit absent voice substrate | must NOT fabricate voice-FM findings vs absent `/mnt/skills/user/cN-*` | **SOFT PASS** | no fabricated voice citations (not a hard fail). But the skill did not skip or note the absent substrate — it *repurposed* the "Voice FM" attack family into an artifact outcome-check and self-audited the repurposing. The voice-FM machinery is the adaptation target. |
| 3 workflow-fit Phase-7 artifact | engage coherently / not conflate Class taxonomies | **PASS** | engaged the Phase-7 execution artifact coherently; used Workflow §2.7.6 Class-1 fork taxonomy correctly without conflating it with the skill's own Class-1; added 3 strengthening notes |

**Signature discriminator:** every with-skill run produced a "findings considered and
rejected" section (counts 3/3/2/1); zero baseline runs did. That section is the
skill's core rigor contribution — baselines over-generate (13 findings on eval-0)
because nothing filters.

## Results — implementation-planner

| Eval | What it tests | Result | Discrimination |
|---|---|---|---|
| 0 revision-pass tension-002 absorption | change-note discipline; don't extend spec | **PASS (strong)** | with-skill = proper revision-pass: change-note, preserved-vs-revised, surfaced CascadePolicy + admissibility-matrix defects as findings F-1/F-2. Baseline **patched** those defects ("corrected the fabricated enum...") — over-reached past scope, no change-note. |
| 1 env-fit workflow version citation | no phantom Workflow v1.5 / V3-prompt citation | **PASS** | with-skill: zero phantom citations, 5-tier decomposition consistent with landed `harness_is` U-IS-03. Baseline also clean. Weak discrimination — both sound. |
| 2 atomic-decomposition spec-extension guard | surface gaps, never invent | **PASS (strong)** | with-skill: explicit "No spec-extension findings", F-1/F-2 surfaced, keyring binding carried as deferred. Baseline **invented** an enum constant `CONTAINER_ENV_VAR_WITH_KEYRING_HANDLES` not committed by C-AS-05 §5, and "assumed present" dependencies. |

## Adaptation targets carried into task 4

- **harness-adversarial-reviewer — light-touch.** Only the voice-FM attack family
  (`/mnt/skills/user/cN-*/SKILL.md`) has no CLI substrate. Either scope it out or
  formalize the outcome-check form the subagent improvised on eval-2. Everything
  else works well in CLI as-is.
- **implementation-planner — light-touch.** Update the phantom `Workflow v1.5 §7` /
  `V3 system prompt` citations in the skill body to `Project_Workflow_v1_8.md` /
  `CLAUDE.md` framing. No phantom citation leaked into output, but the skill body
  text should be corrected. Otherwise CLI-ready.

Both confirm the adaptation-analysis magnitudes: these two are light-touch;
`systems-architect` and `spec-writer` remain the heavy adaptations (task 4).

## Artifacts

Run outputs: `.claude/skills/{harness-adversarial-reviewer,implementation-planner}-workspace/iteration-1/eval-N/{with_skill,without_skill}/outputs/output.md`
