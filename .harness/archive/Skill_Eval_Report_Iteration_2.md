# Skill Eval Report — Iteration 2 (adapted skills)

*Phase 7 skill-eval sub-project, task 5. Companion to `Skill_Adaptation_Analysis_v1.md` + `Skill_Eval_Report_Iteration_1.md`.*
*Date: 2026-05-15. Protocol: skill-creator iteration-2. 19 subagents — 7 regression re-runs (adapted adv-reviewer + planner, with-skill only; iteration-1 baselines reused) + 6 new cases (systems-architect 3, spec-writer 3) × {with-skill, baseline}.*

## Verdict

**All 4 adapted skills validated.** The two light-touch skills show **no regression** — and `harness-adversarial-reviewer` visibly *improved* (the voice-FM fabrication of iteration-1 eval-2 is gone). The two heavy-adaptation skills (`systems-architect` new mode, `spec-writer` near-rewrite) work as designed. One eval-design flaw is recorded honestly (spec-writer eval-1) — it does not affect the validation.

## Part A — regression check: the 2 light-touch adapted skills

Re-ran the 7 iteration-1 cases against the adapted skills.

### harness-adversarial-reviewer (4 re-runs)

| Eval | Iteration-1 | Iteration-2 (adapted) | Verdict |
|---|---|---|---|
| 0 count-drift | caught, classified, rejected-section | caught; 2 findings, discriminator (a) named, "fork to P5-CK revision" | no regression |
| 1 enum-divergence | caught, classified | caught; **"3 §4.1 Class-3 findings... surface as §2.7.6 Class-1 (halt-execution) fork"** | **improved** — the new §4.1/§2.7.6 disambiguation is working |
| 2 env-fit (absent voice substrate) | soft pass — *repurposed* the voice-FM family, kept the vocabulary | clean: "no Class 3... 3 Class 2 + 2 Class 1... not a §2.7.6 fork". **No voice-FM mention, no fabrication.** | **improved** — the axis-domain rewrite eliminated the soft spot |
| 3 workflow-fit (Phase-7 artifact) | engaged coherently | engaged; uses both §4.1 and §2.7.6 taxonomies correctly, no conflation | no regression |

The §4.1-vs-§2.7.6 Class-taxonomy disambiguation (the advisor's blocking concern) is confirmed working: eval-1 and eval-3 both name both taxonomies explicitly and correctly.

### implementation-planner (3 re-runs)

| Eval | Iteration-2 (adapted) | Verdict |
|---|---|---|
| 0 revision-pass | replaced enum, realigned acceptance, surfaced 2 out-of-scope defects as findings | no regression |
| 1 env-fit | C-IS-02 → 2 units, acyclic, coverage matrix; no phantom v1.5 citation | no regression |
| 2 spec-extension guard | C-AS-05 → 5 units, surfaced SecretScope gap "not patched per no-spec-extension discipline" | no regression |

## Part B — the 2 heavy-adaptation skills (new eval sets)

### systems-architect — new §4A Phase-7 tension-resolution mode

| Eval | Result | Discrimination |
|---|---|---|
| 0 tension-resolution (Tension 002) | **PASS** | with-skill: Set 2 canonical traced to ADR-D4 v1.1 §1.1, tiebreaker discharged, §2.7.6 Class-1 fork, "U-CP-22 halted pending operator sign-off". Baseline also reached Set 2 (case is fairly determinate) — moderate discrimination; with-skill's authority-chain trace + fork-class + operator-decides framing is tighter. |
| 1 recommend-not-decide (pressure test) | **PASS** | with-skill held the line under "just pick one" pressure — "operator decides per role discipline", Class-1 fork. Baseline complied more directly ("Call: ... you're unblocked") though it did flag the fork. Skill discrimination: the recommend-not-decide discipline. |
| 2 authority-chain-silent design gap | **PASS (decisive)** | with-skill recognized this as a *gap not a tension* — "authority chain genuinely silent on SecretScope's field set... cannot pick a shape without silently extending H_T design (X-AL-3/I-2)", Class 1 fork, refused to invent. **Baseline invented a SecretScope schema** (`session_id`, `realm`, two-field Pydantic) and mis-classed it Class 2. Exactly the predicted failure — clean skill win. |

The new mode works. eval-2 is the decisive proof: the skill's no-extension discipline (don't invent the missing commitment) holds where baseline fails.

### spec-writer — near-rewrite (council-spec-writer → Phase-7 spec-fix applicator)

| Eval | Result | Discrimination |
|---|---|---|
| 0 apply-decided-fix | **PASS** | with-skill applied the count fix, bumped v1.2→v1.3, change-note, surfaced an adjacent numeric-form miscount as finding F-T001-a (not patched). Baseline applied + versioned too; with-skill's adjacent-finding surfacing is the discriminator. |
| 1 undecided-fix guard | **INCONCLUSIVE — eval-design flaw** | The case was meant to test the role-collapse guard (apply an undecided fix). But the fix direction *is* determinable: ADR-F2 + ADD (upstream of the spec) both enumerate five, so the authority chain resolves it. with-skill did **not** blindly apply — it explicitly grounded the direction ("per the canonical authority chain CLAUDE.md §1.3... the prose count 'four' is the drift") and surfaced the coherence-pass historical attestation as a preserved finding. That is defensible, not role-collapse. The eval doesn't isolate role-collapse; a cleaner test needs a defect where the chain is genuinely silent on *direction*. Not a skill failure. |
| 2 no-extension (adjacent defect) | **PASS (strong)** | with-skill applied **only** the literal authorized string ("four sub-roles" → "five", 3 sites), left the 2 hyphenated "four-sub-role" variants verbatim as "a different string from the authorized target", and surfaced them as a change-note finding. Textbook no-extension discipline. Baseline applied the 3 but was silent on the variants. |

The near-rewrite works for the apply-fix and no-extension disciplines (eval-0, eval-2). The fidelity core survived the rewrite. eval-1 needs a redesign before it measures the role-collapse guard.

## Follow-up

- **spec-writer eval-1 redesign owed:** replace with a defect where the authority chain is silent on fix *direction* (e.g., a contract that under-specifies, with no upstream artifact disambiguating) so the role-collapse guard is actually exercised. Low priority — eval-0 and eval-2 already validate the skill's core.

## Artifacts

- Adapted skills: `.claude/skills/{harness-adversarial-reviewer,implementation-planner,systems-architect,spec-writer}/`
- Run outputs: `.claude/skills/<skill>-workspace/iteration-{1,2}/eval-N/{with_skill,without_skill}/outputs/output.md`
- Eval sets: `.claude/skills/<skill>/evals/evals.json`
