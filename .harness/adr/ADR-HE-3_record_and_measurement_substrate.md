# ADR-HE-3 — Record and measurement substrate

**Filed** 2026-08-17 · **Repo at** `17011f89c` · **Axes** information substrate · operational
discipline · **Class** Foundational (F) for what the loop records about itself

**Scope.** What the system durably records, and what licenses a claim that a change helped.
Companion to [ADR-HE-1](ADR-HE-1_loop_lanes_coordination_architecture.md) (coordination),
[ADR-HE-2](ADR-HE-2_review_gate_and_completion_semantics.md) (verdict validity), and
[ADR-HE-4](ADR-HE-4_defect_mechanization_and_grounding.md) (mechanization + grounding).
Corpus and authority chain: **HE-1 §0**.

---

## 1. Status

**ACCEPTED** for §3.1 — BUILD-PLAN Arcs 2, 3 and 7, plus ratified decisions **D-B** and **D-D**.
**OPEN** for §6, which carries one genuine field-shape collision between a ratified decision and a
later council ruling.

---

## 2. Context

**Nothing in the loop's own performance claims is currently computable.** Measured: only **3 of 18
arcs** have an unambiguous round-log→arc mapping, so the marginal-yield curve cannot be computed at
usable N; transcript token usage carries **no arc/PR join key**, so cost per arc is not derivable;
and no model, prompt, or config-version field exists anywhere in the ledger schema — which falsified
a proposal (E11) that stratification was checkable against existing logs.

Two further defects are structural rather than missing-data:

- **`arc_type` is declared at close, not open** — so every existing label is hindsight-contaminated,
  and **zero arcs are labeled `applying`**. This matters because the corpus's central claim about
  review yield is that *the discriminator is arc type, not round number*; that claim currently rests
  on a field that cannot support it (self-corrected as E12).
- **`lane_id` does not exist** — `grep -c lane_id` → **0 [V]** — so no lane attribution is possible,
  and it was **dropped from the ratified plan** despite being recommended in the lanes research.

**The corpus's own error record is the strongest argument for this substrate.** Across the two arcs,
**63 logged corrections** (14 loop + 49 lanes), *a majority caught by a layer other than the one that
made the claim*. Gate timings alone were wrong by **5×, 12× and 30×** until measured. A design that
cannot measure itself cannot tell a fix from a regression.

---

## 3. Decision

> **Extend the existing records in place to one common field set; pre-register what a row means at
> the moment it is created rather than at close; and never derive a duration from the gap between
> two records.**

### 3.1 Committed

| # | Commitment | Source |
|---|---|---|
| M1 | **Extend, do not replace.** No new hash-chained ledger. Deliver the *function* (one common field set) by extension of `.harness/arc-metrics.jsonl` and a structured sibling to `.harness/merge-gate-log.md` | **D-B**, L0.2′ |
| M2 | **One common `finding` field set**, emitted by both: `{finding_id, location, observed_evidence, expected_contract, severity, finding_type, lineage_claim, producer}` where `producer ∈ {deterministic_check_id, reviewer_identity}`. **Explicitly load-bearing** — without it, "problems prevented per hour" is uncomputable without a re-parsing pass | L0.2′ |
| M3 | **Adjudication is append-only.** Never overwrite a finding row in place; append a new row with the same `finding_id` and a later timestamp. This is the accepted mitigation for dropping hash-chain tamper-evidence with the ledger — *weaker than a hash chain, adequate here* | D-A × D-B |
| M4 | **Ledger gains** `reviewer_identity`, `prompt_version`, `config_hash`, `arc_type_declared_at ∈ {open, close}`, and per-round terminal outcome | L0.2′ |
| M5 | **Pre-register `arc_type` at arc open.** Today it is required only at close, so labels are hindsight | Arc 2 |
| M6 | **Carry `lane_id` from the start** — one field now versus a migration later, on exactly the two files the split-brain and duplicate-append defects implicate | v1 §5 item 2 |
| M7 | **Phase timing as explicit start+end pairs** — queue / execute / capture / absorb / edit / verify. `result_capture` fires on **both** process-exit **and** log-write-completion, **recorded separately**. **Hard rule: never derive phase timing from inter-record deltas** | Arc 3 |
| M8 | **`concurrent_lanes` is `derived`, never `declared`** — a count taken from observed state, not operator judgement | HE-1 D7 |
| M9 | **Shadow trial wired live, off the blocking path** (D-D overrides "offline corpus analysis first"). **Kill condition:** after **15 scored rounds**, kill if the second reviewer's unique-catch count is not distinguishable from zero, **judged by an adjudicator of neither model family**. **Wall-clock is explicitly NOT a kill criterion** for a lens off the critical path | **D-D**, Arc 7 |

### 3.2 Why M7's "never derive from deltas" is a hard rule, not a preference

Two records adjacent in a log are not two ends of one interval — an intervening record can be
dropped, reordered, or written by another lane. A delta silently becomes a *different quantity* than
the one being named, and the resulting number is indistinguishable from a real measurement. M7 makes
the interval an explicit fact rather than an inference, which is the same discipline as HE-2's
parse-don't-infer rule applied to time instead of verdicts.

---

## 4. Rationale

**Why extension over a new ledger.** Two live records already exist —
`.harness/arc-metrics.jsonl` (18 rows) and `.harness/merge-gate-log.md` (~121 entries), neither
hash-chained. A new ledger would either absorb them or coexist; **coexistence recreates the
four-ledger outcome the new ledger existed to prevent.** *Six rounds of review never asked which* —
it took an adversarial pass (F2-03) to surface the question at all, and D-B answered it. This is also
why HE-1 flags an outstanding one-source-of-truth audit over the resulting store set: extension
avoids *creating* authorities, but does not by itself prove the existing set has exactly one per
fact.

**Why the common field set is the part that had to survive.** The ledger design was dropped; the
*shape* was not. Without one field set across both emitters, every cross-cutting question ("problems
prevented per hour", refresh-collision incidence by lane-count cohort) needs a bespoke re-parsing
pass, which is how measurement debt compounds into never measuring at all.

**Why pre-registration at open is a correctness fix, not a convenience.** A label applied at close is
written by a party who already knows the outcome. Using it to justify a claim about *how the arc
should have been run* is circular — precisely the error self-corrected as E12. Pre-registration is
the cheapest available defense against outcome-contaminated evidence, and it is the same discipline
M9's pre-committed kill condition applies to the shadow trial.

**Why the shadow trial runs live rather than offline first.** D-D overrides the offline-corpus-first
sequencing. The measurement being sought is the second reviewer's **unique-catch rate under real
conditions**; a retrospective over a corpus generated under different conditions answers a different
question. The pre-committed kill condition plus a neither-family adjudicator is what keeps a live
trial from becoming a permanent unevaluated addition — and #19 forbids it becoming permanent merely
because an evaluator emits GO.

**What measurement cannot settle — recorded so it is not over-claimed.** Behavioral endogeneity caps
what the shadow study can establish: the loop's participants change behavior when measured. And
**comprehension debt** — the gap between what the loop ships and what the operator understands —
*grows faster as loops get faster*, so optimizing wall-clock carries a cost that does not appear in
wall-clock. Neither is a reason to skip measuring; both are reasons not to treat a measured GO as
dispositive.

---

## 5. Consequences

**Becomes possible.** Cohort comparison by lane count — the mechanism already exists
(`arc_metrics.py:812-832` implements cohort splitting) and **every historical row is an implicit N=1
baseline**. Refresh-collision incidence becomes correlatable against `concurrent_lanes` using
instrumentation that already emits.

**Becomes harder.** Every emitter must now agree on a field set, so adding a check means authoring
its `producer` identity rather than printing a message. Append-only adjudication means the log grows
monotonically and readers must reduce by `finding_id` rather than trusting the last row.

**Now constrained — and this is the sequencing consequence that matters.** A subset of the ratified
build order exists to make *measurement* trustworthy rather than to make lanes *safe*: M4–M7 and the
`ARC_METRICS_{REPO,LEDGER}` env overrides are instrument-correctness. They gate **Arc 4 onward and
every efficiency claim**, not lane operation. This is the substantive claim behind this session's
withdrawn "Phase 0a/0b" proposal (HE-1 §0), re-expressed against the ratified Arc order rather than
a fourth numbering scheme: **lane safety and measurement trustworthiness are different gates, and
conflating them makes the safety floor look larger than it is while leaving instrument items
un-sequenced against the arcs that consume them.**

**Concrete dangling prerequisite.** `REPO` and `LEDGER` are bare module-level assignments at
`arc_metrics.py:44-45` with **no env override [V]**, unlike `QUEUE_DIR` at `:59-63` and `MERGED_REF`
at `:79` **[V]**. The mandatory same-instant concurrency probe cannot be constructed without
per-process `REPO`/`LEDGER`, so `ARC_METRICS_REPO` / `ARC_METRICS_LEDGER` must land **before** that
probe can go GREEN. No build item owned this until it was surfaced adversarially.

---

## 6. Open item — the field-shape collision

**A ratified shape and a later council ruling disagree on the finding record, and neither party saw
the other.**

- **Ratified (D-A × D-B, 2026-08-17):** an **8-field** shape — `{finding_id, location,
  observed_evidence, expected_contract, severity, finding_type, lineage_claim, producer}` — declared
  *"load-bearing"*.
- **Council ruling R-25 (later):** retarget emission onto the **proven 3-field** record, because
  `codex_context_guard.Finding` carries only `severity, code, message` (`:113-117` **[V]**), is
  JSON-emittable and CI-wired, whereas the 8-field shape has **no implementation** — `finding_id` has
  **zero matches across `.py` files [V]**. R-25's proposal encodes the extra dimensions into a
  namespaced `code` string.

Both are sound on their own terms: the ratified shape is what makes the metric computable; the
council's is what exists and is proven. They are not reconcilable by picking the "later" one, because
the later one is a *council* ruling and the earlier one is an *operator ratification* — and on this
corpus's authority chain, ratification outranks council.

**Recommendation.** Implement the 8-field shape as the **record**, and treat `Finding`'s 3 fields as
a **projection** of it for the CI surface that already consumes them (`severity` ← mapped from
`finding_type`/fail-class; `code` ← namespaced). This satisfies D-B (extend, don't replace) and R-25's
real concern (don't invent an unproven emitter) without dropping the fields M2 calls load-bearing.
Encoding eight fields into a 3-field record's `code` string is a lossy substitute for a schema and
would make the metric un-queryable again.

**Tiebreaker:** confirm whether any consumer parses `Finding.code` positionally today. If one does, a
namespaced-string extension is a breaking change and the projection must be additive.

---

## 7. Alternatives considered

| Alternative | Why rejected |
|---|---|
| **A new hash-chained append-only ledger** (the original L0.2) | Superseded by **D-B**. Two live records already exist and are not hash-chained, so this was new territory rather than an in-place upgrade; coexistence would recreate the multi-ledger outcome it existed to prevent |
| **sqlite as the durable record** | L-5: a new shared DB + WAL surface, **no correctness gain**, and it loses git-diffability. JSONL stays |
| **A third durable store for landing state** | Folded into the existing merge-door lease payload instead (HE-1 D5); L-5 / D-B both argue against proliferation |
| **Derive phase timing from inter-record deltas** | The measurement silently answers a different question than the one asked, and is indistinguishable from a real one. M7 forbids it outright |
| **Offline corpus analysis before wiring the shadow trial** | Overridden by **D-D**. A retrospective over a differently-generated corpus does not answer the live unique-catch question |
| **Wall-clock as a shadow-trial kill criterion** | Explicitly rejected: the lens runs **off** the blocking path, so its wall-clock does not bind the loop. Killing on it would discard a lens for a cost it does not impose |
| **Declaring `arc_type` at close** (status quo) | Outcome-contaminated by construction; produced zero `applying` labels and cannot support the arc-type-over-round-number claim that rests on it |

---

## 8. References

**Verified at HEAD (`17011f89c`) this session.**

- `tools/arc_metrics.py` — `REPO`/`LEDGER` bare at `:44-45` (no env override) · `QUEUE_DIR` `:59-63` ·
  `MERGED_REF` `:79` · cohort splitting `:812-832`
- `lane_id` → **0 occurrences** repo-wide · `finding_id` → **0 matches** across `.py` files
- `tools/codex_context_guard.py` — `Finding` `:113-117`, exactly `severity, code, message`
- `.harness/arc-metrics.jsonl` and `.harness/merge-gate-log.md` both present

**Ratified / council-recorded, not independently re-verified.** Decisions D-A, D-B, D-D and Arcs 2/3/7
(`BUILD-PLAN-operator-ratified-2026-08-17.md`) · L0.2′ reconciliation (v1 §3.1) · ruling R-25 and the
E11/E12 corrections (`HARNESS-LOOP-AND-LANES-DESIGN-v2.md` §10a;
`STAGE7-FINAL-opus-grounded-findings.md` §2) · the 3-of-18 round-log mapping, the missing arc/PR join
key, and the 63-correction count (`SYNTHESIS-loop-v2-reconciliation.md` §7; v1 provenance note)

---

## 9. Filing footer

§3.1 is ratified; §6 is not and carries an unresolved ratified-vs-council collision. Superseding
requires a new `ADR-HE-N` citing this one. H_E tooling only.
