# Skill Adaptation Analysis v1 — 4 Design-Phase Skills → Phase 7 CLI

*Task #1 output. Catalogs the as-is environment/workflow fit of the 4
authoring skills installed at `.claude/skills/`, the design-phase
assumptions that break in the Claude Code CLI environment, and the
adaptation magnitude per skill. Feeds the eval-harness build (task #2) and
the adaptation pass (task #4).*

---

## §1 Environment deltas common to all 4 skills

| # | Design-phase assumption | CLI reality | Fix |
|---|---|---|---|
| E-1 | "Operates under the **V3 system prompt**" — V3 owns confidence tags, citation discipline, anti-fabrication, scope | No V3 system prompt in CLI. `CLAUDE.md` (root + per-axis) is the framing authority | Re-point "V3" → workspace `CLAUDE.md` conventions |
| E-2 | `Project_Workflow_v1_0.md` / "Workflow v1.5" cited for §-numbers | Workspace canonical is `Project_Workflow_v1_8.md` | Re-cite to v1.8; verify §-numbers |
| E-3 | "project KB" / `project_knowledge_search` for artifact reads | CLI filesystem — `design-substrate/` holds canonical artifacts | Re-point to filesystem reads |
| E-4 | `/mnt/skills/user/cN-*/SKILL.md` voice skills (adversarial-reviewer) | No 11-voice council skills in CLI workspace | Voice-FM substrate unavailable — see §2 |
| E-5 | All 4 scoped to design phases (2 / 3a-3d / 5 / 6 / 4 checkpoints) | Work is **Phase 7 execution-time** tension resolution | Each skill needs a new Phase-7 mode (see per-skill) |
| E-6 | Back-flow to design-phase channels assumed | Back-flow **deprecated** 2026-05-15; fixes happen in-CLI | Re-point "back-flow / fork to Phase N" → in-CLI tension-record + fix |

---

## §2 Per-skill assessment

### harness-adversarial-reviewer — adaptation: MODERATE

- **As-is fit:** Good discipline core (severity discriminator tree, V3 attack vocabulary, finding format, self-audit, FM-list). Reviews *completed* artifacts — CP/OD spec+plan qualify.
- **Breaks:** E-1, E-2 (cites Project_Workflow_v1_0 §4.1 / §2.x), E-4 (voice-FM substrate `/mnt/skills/user/cN-*` absent — the "Voice FM-list substrate" attack family cannot run), E-5 (4 design checkpoints only; no Phase-7 execution-time review mode).
- **Class-label collision:** its Class 1/2/3 = §4.1 *severity* (drift / current-phase / phase-reopen). Phase 7 fork Class 1/2/3 = *halt / operator-decision / informational*. Same labels, different meaning — must disambiguate.
- **Adaptation:** add a Phase-7 pre-implementation review mode (review an axis's spec+plan corpus for the units about to land); drop or substitute the voice-FM attack family; re-cite workflow v1.8; disambiguate the Class taxonomy.

### implementation-planner — adaptation: LOW–MODERATE

- **As-is fit:** Strong. The §8 revision-pass mode already fits Phase-7-triggered plan revision (spec revision → plan absorption). Atomic-decomposition / spec-traceability / dependency-graph discipline transfers directly.
- **Breaks:** E-1, E-2 ("Workflow v1.5" §7), E-5 ("Do NOT activate for post-plan execution" — but Phase 7 IS post-plan; the revision-pass *is* the in-scope use). Output filename `Implementation_Plan_vN+1.md` is generic; real plans are per-axis (`Implementation_Plan_Control_Plane_v2_3.md`).
- **Adaptation:** light — authorize revision-pass mode for Phase-7-originated triggers; re-cite v1.8; per-axis filename convention.

### systems-architect — adaptation: MODERATE (new mode)

- **As-is fit:** §2 cross-mode discipline (five-axis decomposition, probabilistic-deterministic boundary, F/D/I decision ordering, ADR template, cross-axis verification) is exactly the discipline a Tension-002-class decision needs. BUT the skill has only 2 modes — Phase 2 persona-surfacing, Phase 3d ADD-consolidation — and §1 says "neither signal present → stand down." It would refuse Tension 002.
- **Breaks:** E-1, E-5 (no execution-time tension-resolution mode; description explicitly excludes "general architecture questions outside Phase 2/3d").
- **Adaptation:** add a 3rd mode — Phase-7 architectural-tension-resolution — that applies §2 discipline to a surfaced execution-time tension, produces a decision recommendation traced to ADR/spec authority, defers the call to the operator (no decision authority — surfaces, recommends).

### spec-writer — adaptation: HIGH (near-rewrite)

- **As-is fit:** LOW. The skill is "the council's bookkeeper" — its entire machinery ingests council-orchestrator output (Convening Block / CCR / voice contributions / TENSION blocks) and runs a 3-stage authoring pipeline. **That council apparatus does not exist in the CLI workspace.** References `s2`/`s3`/`s4–s14` voice specs, `project_knowledge_search`, 11-voice consistency check — all absent.
- **Transferable core:** fidelity discipline only — verbatim-layer integrity, traceability anchors, tension preservation, "never resolves a tension / never makes architectural decisions unilaterally," change-note + version discipline, audit-before-emit.
- **Adaptation:** near-rewrite. What Phase 7 needs from a "spec-writer" is narrow: apply an operator-approved spec fix to a `design-substrate/` spec file with proper change-note / version-bump / backref-reconciliation discipline. Keep the fidelity core; drop the council pipeline.

---

## §3 Sequencing implication (revises the eval approach)

The operator selected "full eval harness." Reading the artifacts reveals the
4 skills are NOT uniformly off-fit, so a uniform "eval all 4 as-is first"
spends effort poorly:

- **adversarial-reviewer, implementation-planner** — mostly-right. Eval-as-is
  IS informative: calibration against known ground truth (Tension 001 +
  Tension 002) tests whether the discipline works in this environment.
- **systems-architect** — eval-as-is would only confirm it stands down (no
  Phase-7 mode). Near-zero information. Adapt (add mode) → then eval.
- **spec-writer** — eval-as-is is a guaranteed fail (council machinery
  absent). Zero information. Adapt (rewrite) → then eval.

**Recommended:** differentiate. Eval-as-is the 2 mostly-right skills for
calibration signal; adapt-then-eval the 2 that need new modes / rewrite.
The "full eval harness" still gets built — it just runs against the
adapted versions for systems-architect + spec-writer, and twice (as-is +
adapted) for the other two.
