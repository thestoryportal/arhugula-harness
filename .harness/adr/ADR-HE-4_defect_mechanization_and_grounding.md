# ADR-HE-4 — Defect mechanization and grounding-first

**Filed** 2026-08-17 · **Repo at** `17011f89c` · **Axes** operational discipline · control plane ·
**Class** Foundational (F) for where loop cost is actually attacked

**Scope.** The loop's *upstream* half — why arcs are slow, and the one place the corpus says to fix
it. Companion to [ADR-HE-1](ADR-HE-1_loop_lanes_coordination_architecture.md),
[ADR-HE-2](ADR-HE-2_review_gate_and_completion_semantics.md), and
[ADR-HE-3](ADR-HE-3_record_and_measurement_substrate.md). Corpus and authority chain: **HE-1 §0**.

---

## 1. Status

**ACCEPTED** for §3.1 — authorized by **D-A** (*"build through Layer 2 — safety + measurement + speed
work; full scope"*) and BUILD-PLAN Arcs 4–6.
**PROPOSED** for §3.2 — the grounding-gate family (T6–T9), which is reconciliation-stage work that
D-A's Layer-2 scope does not clearly reach.

---

## 2. Context — the diagnosis, which is the whole reason this record exists

The operator's presenting complaint was wall-clock. The corpus **confirmed the symptom, rejected the
proposed cause, and located a different one.**

| Claim | Verdict |
|---|---|
| **P1 — wall-clock too high** | **CONFIRMED.** 68% of Bash wall-clock is gate/test/review machinery (`codex_review` 27.0% + other codex 15.1% + pytest 15.1% + local gate 10.8%, n=22,063 calls). Median arc **109.9 min** across a median **5 rounds** at 17.7 min/round |
| **P2 — review rounds are redundant** | **REJECTED as stated.** No reliable yield decay exists. Round 2 out-yields round 1. A flat cap is unsafe |
| **P3 — the agent under-grounds** | **CONFIRMED, and it is the causal driver** |

**The causal chain is P3 → P2 → P1.** The coding agent introduces self-inflicted, mechanically
catchable defects; the review layer correctly finds them; the loop churns re-finding what the agent
keeps re-breaking. On the arc where this was traced (19 rounds), **rounds 6–19 were the agent
re-breaking its own fixes.**

**First-party evidence — the agent's own contemporaneous retrospective on one arc: 6 of 8 findings
(75%) were self-inflicted and mechanically catchable.** Only 2 needed a reasoning reviewer. Of the
six: a placeholder token left in a register, stale docstring counts, a cite to a section never
opened, an assertion about CLI behavior never run, a claim about a gate whose own prompts were never
read, and a contradiction against governance never grepped.

**External corroboration makes the causality explicit:** syntactic/runtime errors fix at **>80%
within 1–2 rounds**; logical/algorithmic errors at **<35% even with 10 rounds available**. More
rounds cannot substitute for correct grounding. The long tail is not slow reviewers — it is the wrong
*class* of defect fed into a mechanism that does not fix that class.

**Measured mitigation precedent:** `leg-selfcheck` already cut self-inflicted findings from ~60% to
**~29% of rounds**; the residual is **~85 min per arc** at the measured round median.

---

## 3. Decision

> **Attack loop cost by removing defect classes upstream of review — never by shortening review.
> Mechanization converts a finding class into a deterministic pre-check; it does not license a cap.**

### 3.1 Committed (D-A Layer 2; Arcs 4–6)

| # | Commitment |
|---|---|
| K1 | **Mechanize the self-inflicted defect classes**, each tagged `kind ∈ {deterministic, hybrid, model-judge}`. **2 of ~7 classes are mutation-probe-backed and will not be sub-second — they must not ship under a "low-risk" label.** The ~32min→~1s precedent from the trilemma class **does not transfer** to them |
| K2 | **Remove duplicated executions.** Equivalence must be proved by a party **decorrelated from the agent whose diff benefits**, or by a deterministic execution-context diff. **Log the proof.** Two within-CI double-runs are already identified as pure waste — same file, same SHA, same runner, no environment argument |
| K3 | **Close the local/CI gap — ~58s measured**, not the ~90s previously claimed. Exclude environment-irreproducible checks. **`codex-context-guard` has no local equivalent at all today**, despite five justfile recipes for sibling subcommands |
| K4 | **Mechanization never licenses shortening review** (#20, B-174's explicit non-goal). It removes classes *from* the loop; it does not cap the loop |

**The per-class check set (K1), with the cheapest deterministic check per class:**

| Class | Freq | Cheapest check | Wired today |
|---|---|---|---|
| stale-carry text / counts | ≥11 | numeric + placeholder-token repo sweep | partial (one surface) |
| weak/false test witnesses | 9+ | auto re-verify **every** annotation's named mutation | partial (tool exists, applied by hand) |
| unswept consumers | ≥5 | `graft callers <sym> --depth all` before "complete" | no general tool |
| unrun-CLI claims | 4 | assert exit code **and** positive content before "clean" | no |
| cited symbol doesn't exist | 1 | one-line grep, near-zero false positives | no |
| delta-chain version drift | 1 + named pattern | sweep later versions for the cited § | no |
| wrong-fidelity test doubles | 1 | `issubclass()` assertion in a shared fixture helper | no |

**Note on K1's own reliability:** on one arc, **3 of 40 mutation-probe annotations were themselves
false**. The check that verifies witnesses must therefore be mechanical re-verification of the named
mutation, not a re-read of the annotation.

### 3.2 Proposed — the grounding-gate family

Not clearly inside D-A's Layer-2 scope; recorded so it is not lost, and marked unratified.

| # | Proposal |
|---|---|
| K5 | **Upgrade what each round carries, before touching how many rounds run.** Structured feedback carrying location + observed value + **admissible alternatives** raised success **+42–44pp**, with the ablation showing *most of the gain is in the alternatives*; evidence-carrying feedback gained **+8.3 pts vs +1.7** for generic retry. **Prose-vs-JSON made no difference — content, not format** |
| K6 | **Closed-schema review findings that classify their own scope** — a finding must declare `task_relevance` / `scope_relation` / `introduced_by_current_task` before it may block. Makes out-of-scope churn structurally unrepresentable; directly attacks the arms-race class (7 named instances) |
| K7 | **Route by arc type and finding class, not round number.** Invention arcs get budgeted long loops; applying arcs get a *tested* stop rule. Split the retry budget by class — route a design-level miss back to **re-grounding (P3)**, not another review pass (P2) |
| K8 | **A structural grounding gate before implementation** — a think-step that cannot skip to action, plus an externally-authored done-condition before code starts. `postedit-lint.sh` is already wired **advisory-only**; upgrading its verdict for a defined class is a small contained change, and `PostToolUse` + `preventContinuation` can force-stop a bad edit **in the same turn** rather than a round later |

**K7 depends on ADR-HE-3 M5.** Routing by arc type requires `arc_type` pre-registered at *open*;
against today's close-declared label the routing key is hindsight-contaminated and the rule would be
unfalsifiable. **K7 must not be built before M5 lands.**

---

## 4. Rationale

**Why upstream rather than inside review.** The measured error-class split settles it: the defects
driving long arcs are the class that *does not* respond to more rounds. Adding review capacity to a
<35%-per-10-rounds class buys churn; removing the class buys the whole tail. This is also the only
intervention that reduces cost without touching a decorrelation guarantee.

**Why "mechanize" is not a euphemism for "cap."** #20 states the non-goal explicitly, and this is the
single most likely misreading of the entire corpus: a P1-motivated reader sees "we removed defect
classes" and concludes "therefore fewer rounds are needed." The data forbids it — round 2 out-yields
round 1, and one arc produced genuine findings through round 48 of 49. K4 exists to make the
non-inference explicit rather than implied.

**Why the equivalence proof in K2 must be decorrelated.** "These two runs are equivalent, so delete
one" is exactly the claim an agent optimizing its own diff is worst placed to make, and the failure is
silent — a deleted run produces no signal proving it was needed. Requiring a decorrelated party or a
deterministic context diff, **and logging the proof**, is the same discipline HE-2 applies to
verdicts: the claim must be independently checkable after the fact.

**Why the local/CI gap is the highest-leverage speed item.** It converts a 4.95-min CI failure-plus-push
cycle into a ~58s local one, and it is the precondition for "converge locally, push once" — which
targets the 20% of branches burning ≥6 CI runs and the 13.7% CANCELLED rate directly. Its numbers were
also **wrong by 5×, 12× and 30×** until measured, which is why HE-3's instrument work sequences ahead
of any efficiency claim made here.

**What this record does not claim.** The marginal-yield curve is **underpowered** — real per-round
finding counts exist for only 3 arcs / 18 rounds. Nothing here supports a strong claim about
late-round yield in either direction. K7's "tested stop rule" is therefore a *proposal to test*, not a
stop rule; ADR-HE-3's instrumentation is its prerequisite.

---

## 5. Consequences

**Becomes possible.** The ~85 min/arc residual of self-inflicted findings becomes addressable.
Deterministic checks are cheap to run every turn, so a class removed stays removed rather than
depending on reviewer attention.

**Becomes harder.** Each mechanized class is a new check to maintain, and a false-positive check is
worse than none — it trains the agent to route around it. The 2 mutation-probe-backed classes carry
real wall-clock, so K1 cannot be sold as uniformly cheap.

**Now constrained.** No mechanization may be cited as grounds for a round cap (#20, #11, #17). No
duplicated execution may be removed on the beneficiary's own say-so (K2). Adoption is not
self-authorizing however favorable the measurement (#19).

**Deliberately not attempted.** Best-of-N / parallel variant generation as a speed fix — a measured
**null result** at this model's temperature, corroborated externally by findings that auto-designed
multi-agent systems underperform simpler self-consistency at up to 10× cost. This is worth stating
because it is the intuitive fix for a wall-clock complaint and it does not work here.

---

## 6. Open items

1. **Is §3.2 (K5–K8) authorized under D-A?** D-A names *"safety + measurement + speed."* K5–K8 are
   quality-of-round and grounding work — arguably speed by another route, but not named.
   **Recommendation:** treat K8 as authorized (it is a contained upgrade of an already-wired advisory
   hook) and K5–K7 as requiring explicit scope confirmation. **Tiebreaker:** does any Layer-2 item in
   STAGE7 §4 reference feedback content or grounding gates? If not, they are a new layer.
2. **K7's stop rule for `applying` arcs** — cannot be designed until HE-3 M5 provides an uncontaminated
   `arc_type`, and cannot be validated until the round-log→arc mapping exceeds 3 of 18 arcs.

---

## 7. Alternatives considered

| Alternative | Why rejected |
|---|---|
| **A flat numeric round cap** | The intuitive fix for P1, and falsified by this repo's own data — 49 productive rounds on one PR, round-2 yield above round-1. Violates #11/#17 and #20. See ADR-HE-2 §7 |
| **Best-of-N / parallel variant generation** | Measured null result at this model's temperature; external evidence that auto-designed multi-agent systems underperform CoT self-consistency at up to 10× cost |
| **Re-running `codex-check` after CI-green on the same SHA** | The justfile recipe and the CI job invoke the **byte-identical** script. Zero new information |
| **Adopting an agent framework** to get mechanization for free | Standing framework-pull ban. The two candidate sources fail independently: one's model layer does a literal `import litellm`; the other's tutorials are built on LangGraph/CrewAI/LlamaIndex |
| **Fast mode** for throughput | 6× price for 2.5× throughput — fails the token-economics constraint, which is measurably excellent (98.0% cache-read) and explicitly must not be touched |
| **Collapsing review layers to cut the 68%** | Attacks the symptom at the cost of the guarantee; 93.4% of findings are single-tool catches. The 68% is *where* the time goes, not *why* the loop is long — P3 is why |

---

## 8. References

**Verified at HEAD (`17011f89c`) this session.**

- `tools/codex_context_guard.py` **present**; `tools/codex_review.py` **absent**
- `tools/arc_metrics.py:812-832` cohort splitting — baseline vs treated grouped by **exact lever
  set**, deliberately not collapsing every non-empty `levers_active` into one TREATED cohort (the
  instrument K1/K3 claims would be measured against)
- **Scope limit on K3's claim:** `codex_context_guard` is referenced in `justfile` but appears in
  **no file under `.github/`** — so it reaches CI through a recipe, and this record does **not**
  independently verify the CI path. K3's *"no local equivalent"* claim is carried from the corpus,
  not re-derived here

**Council-recorded / measured-in-corpus, not independently re-verified here.** The 68%-of-Bash,
109.9-min-median, 5-round-median and 22,063-call figures; the 6-of-8 self-inflicted retrospective;
the ~60%→~29% `leg-selfcheck` mitigation and ~85 min/arc residual; the >80%/<35% error-class split;
the corrected gate timings (20.4s / 1.67s / 0.51s / 9.98s) and ~58s aggregate; the +42–44pp and
+8.3-vs-+1.7 feedback results; the 3-of-40 false mutation-probe annotations; the null best-of-N result
— all `SYNTHESIS-loop-v2-reconciliation.md` §§1–5 and `STAGE7-FINAL-opus-grounded-findings.md` §3,
with R1's checklist (#11, #17, #19, #20) at `R1-uwt09-prior-art.md` §7. Ratified scope: **D-A** and
Arcs 4–6, `BUILD-PLAN-operator-ratified-2026-08-17.md`.

---

## 9. Filing footer

§3.1 is ratified under D-A; §3.2 is proposed and explicitly unratified. Superseding requires a new
`ADR-HE-N` citing this one. H_E tooling only.
