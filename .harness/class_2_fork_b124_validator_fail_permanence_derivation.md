# Class 2 Fork — B-124 (derivation sub-decision): what replaces the demoted `validator.fail.permanence` derivation?

**Filed:** 2026-08-09 · doc-only filing, design-phase posture (no `design-substrate/**` or code touched by
this PR). **Register row `B-124`** stays `registered_finding`; this filing does not ratify anything and does
not edit the register — any status/`pr:` cross-stamp is a separate leg.

**Venue + authority.** `Spec_Control_Plane_v1_116.md` §1.3 (the operator-ratified `B-138` disposition-(a)
leg, 2026-08-09) demotes the pre-existing `validator.fail.permanence` derivation clause with the retry-exit
taxonomy it was keyed to, states that *"a replacement wire derivation is deliberately NOT declared at this
delta,"* and routes the choice to `B-124` by name: *"[the arc] must either materialize the retry-exit
classification at the emission site, ratify an outcome-based narrowing WITH §21.6 re-specified, or select
another carrier — and until it does, `validator.fail.permanence` stays declared-unwired."* This filing is
that routed sub-decision.

**Coupled but distinct from `B-124`'s already-closed §10.2 half.** `B-124`'s prior grounding leg (PR #1277,
recorded on the row) split the row into two independent halves: **(A)** the §10.2 tail-keep trigger, closed
by wiring the attribute at the emission site (a live path exists, `Leg 1`), and **(B)** the §9.2
always-sampled floor, which is name-gated and re-scoped forward to `B-137`'s step-(3) posture decision —
**out of scope here, and this filing does not reopen it.** The row's Leg 1 estimate (~3 functional lines,
outcome-derived) predates `B-138`'s v1.116 §1.3 finding that the naive outcome wire is **lossy**, which is
exactly what this filing resolves.

**Grounding HEAD.** `4b3a33ce`. Every cite below was re-resolved by direct read at this HEAD.

---

## §1 The question, and what carries it

`ValidatorFramework._build_span_attributes` (`harness-cp/src/harness_cp/validator_framework.py:320-352`) is
the sole producer of the `validator.evaluate` span's `validator.fail.*` attributes. On any non-`PASS`
outcome it unconditionally sets two fields and conditionally sets two more (`:341-349`):

```python
if result.outcome != ValidatorOutcome.PASS:
    attrs["validator.fail.next_action"] = next_action.value
    attrs["validator.fail.escalation_owed"] = (
        next_action == ValidatorNextAction.ESCALATE_HITL
    )
    if result.fail_class is not None:
        attrs["validator.fail.class"] = result.fail_class.value
    if result.fail_detail_hash is not None:
        attrs["validator.fail.detail_hash"] = result.fail_detail_hash
```

**It never sets `validator.fail.permanence`.** No other production call site does either —
`validator_fail_permanence()` (`harness-cp/src/harness_cp/validator_fail_taxonomy.py:169-176`) has zero
callers across `harness-{runtime,cp,od}/src` (grep-confirmed; only the definition, one docstring reference
at `harness-od/src/harness_od/tail_keep_classification.py:60`, and three test assertions at
`harness-cp/tests/test_validator_fail_taxonomy.py:76-83`).

**Why this is a fork rather than an impl task.** The demoted derivation clause was a correct function over
a taxonomy (`ValidatorRetryExitClass`) the wire producer does not hold — `B-138` settled that the wire
authoritatively carries `ValidatorFailClass` (C-CP-25→C-CP-28 §25.2), a disjoint five-value domain from the
retry-exit taxonomy (C-CP-21 §21.1). Re-deriving permanence therefore has no single correct repair: it
requires either a new producer field, a declared narrowing of a cleared contract, or a different carrier
entirely — three substantive alternatives, which is Class 2 (in-execution operator decision) per root
`CLAUDE.md` §4.3, not Class 1.

---

## §2 What the producer actually holds, at HEAD

| Type | Fields (verified) | Cite |
|---|---|---|
| `ValidatorResult` | `outcome: ValidatorOutcome`, `fail_class: ValidatorFailClass \| None`, `revalidation_payload`, `escalation_brief: HITLEscalationBrief \| None`, `fail_detail_hash: str \| None` — five fields, no more | `validator_framework_types.py:154-171` |
| `ValidatorEvaluation` | wraps `ValidatorResult` and adds `span_attributes`, `next_action: ValidatorNextAction`, `burden_count: int` | `validator_framework_types.py:174-189` |
| `ValidatorOutcome` (5) | `PASS` / `REVALIDATE` / `ESCALATE` / `PERMANENT_FAIL` / `OPERATOR_BURDEN_EXCEEDED` | `validator_framework_types.py:42-65` |
| `ValidatorFailClass` (5) | `schema_violation` / `semantic_inconsistency` / `safety_policy` / `resource_constraint` / `external_rejection` | `validator_framework_types.py:70-89` |
| `ValidatorNextAction` (4) | `PROCEED` / `RETRY` / `ESCALATE_HITL` / `ABORT` | `validator_framework_types.py:105-115` |

The target taxonomy — the one the demoted derivation actually consumed — lives entirely outside this
type family:

| Type | Members (verified) | Cite |
|---|---|---|
| `ValidatorRetryExitClass` (5) | `transient-retry` / `Reflexion-recoverable` / `HITL-recoverable` / `permanent-fail-exit` / `terminal-fail-exit` | `validator_fail_taxonomy.py:39-62` |
| `validator_fail_permanence(fail_class)` | `"permanent"` iff `fail_class ∈ {PERMANENT_FAIL_EXIT, TERMINAL_FAIL_EXIT}` (`_PERMANENT_CLASSES`), else `"transient"` | `validator_fail_taxonomy.py:161-176` |

Not one field on `ValidatorResult` or `ValidatorEvaluation` is typed as `ValidatorRetryExitClass`, and no
function in `harness-cp/src` or `harness-od/src` converts between the two families (grepped; see §3(ii)).

---

## §3 Grounding findings

### (i) The lossiness is confirmed from two directions, not one `[HIGH]`

`ValidatorRetryExitClass.PERMANENT_FAIL_EXIT`'s own docstring: *"SKIP STAIRCASE; route directly to C11 HITL
(validator-escalation)"* (`validator_fail_taxonomy.py:58-59`). `HITL_RECOVERABLE`'s docstring: *"C11 HITL
primitive (validator-HITL placement per §17.1 validator-escalation)"* (`:54-56`). Both retry-exit-taxonomy
members route to HITL. At the CP-25/28 outcome layer that §1.3 identifies as the only candidate carrier,
routing to HITL presents as `ValidatorOutcome.ESCALATE` (`ESCALATE_HITL`'s docstring:
*"ValidatorOutcome ∈ {ESCALATE, OPERATOR_BURDEN_EXCEEDED}"*, `validator_framework_types.py:111-115`) — so
`outcome` cannot discriminate `permanent-fail-exit` from `HITL-recoverable`, which have **opposite**
permanence. The same collision recurs on `next_action`: both present as `ESCALATE_HITL`
(`validator_framework.py:342`). Neither disposition-shaped field the producer holds can carry the
distinction. §1.3 states this; this filing re-derived it independently from the enum bodies and it holds.

### (ii) A hypothesis tested and falsified: `fail_class` cannot rescue the derivation `[HIGH]`

§1.3's prose is loose in letter — *"the only candidate the producer holds — the validator outcome"* — since
the producer in fact holds five fields and `fail_class: ValidatorFailClass` is already on the wire
(`validator_framework.py:347`). One might therefore propose deriving permanence from `fail_class` instead
of `outcome`. **This is foreclosed.** `ValidatorFailClass` is a **cause-of-failure** axis — *why* validation
failed (`schema_violation`, `safety_policy`, …) — not a **retry-disposition** axis, and its own docstring
says so explicitly: *"Distinct from C-CP-21 §21.1 ValidatorRetryExitClass (post-fail retry-exit
classification)"* (`validator_framework_types.py:73-74`, `:18-20`). A repo-wide grep for any
`ValidatorFailClass ↔ ValidatorRetryExitClass` mapping — function signature, dict literal, or `match`
statement — returns **zero** hits across `harness-{cp,runtime,od}/src`; the only cross-references are
docstring statements that the two are distinct. §1.3's letter is imprecise, but its substance is correct:
no field the producer holds — outcome, `fail_class`, or `next_action` — carries retry-disposition
information. This is recorded so `fail_class` is not re-proposed as a cheap escape from Reading A.

### (iii) The retry-exit classification IS produced in production — on a different path entirely `[HIGH]`

`_classify_provider_exception` (`harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:281-418`)
maps provider/dispatch exceptions to `ValidatorRetryExitClass | None` and feeds the transient staircase.
This is the **dispatch/provider-exception** path — LLM call failures, memory-tool executor faults, breaker
waiver decisions — entirely separate from the **Validator evaluation** path (`validator_framework.py`),
which never imports or references `ValidatorRetryExitClass` (grep of `validator_framework.py` +
`validator_framework_types.py` for `RetryExitClass` returns zero hits; the only "retry-exit" text anywhere
in those two files is docstring prose distinguishing the two taxonomies, at `validator_framework_types.py:18-20,73-74`).
So the classification the demoted derivation needs **exists in the system** — it is just produced on the
wrong surface for this emission site to consume it directly.

### (iv) The two `validator.fail.permanence` readers do not share a fix — carried forward from `B-124`'s prior leg, not re-litigated here `[HIGH]`

`is_classification_trigger`'s §10.2 row-1 check reads `span.attributes.get(VALIDATOR_FAIL_PERMANENCE_ATTR)`
unconditionally off **any** span, after the two name checks and before the event scan
(`harness-od/src/harness_od/tail_keep_classification.py:157-160`). `is_always_sampled`'s §9.2 row is
resolved differently: `_conditional_always_sampled` first gates on
`event_name.startswith(_VALIDATOR_FAIL_PREFIX)` (`_VALIDATOR_FAIL_PREFIX = "validator.fail."`,
`harness-od/src/harness_od/sampling_mode.py:222`) and **only then** reads the attribute
(`sampling_mode.py:239-241`) — the read is real, but it is gated behind a name match the live
`validator.evaluate` span never satisfies (the span is named `validator.evaluate`, not `validator.fail`
or `validator.fail.*`). **Stated precisely: `is_always_sampled` does read attributes for this row, but only
once its name gate fires, and the live producer's span name never fires it** — a sharper statement than
"never attributes," though the practical consequence (wiring the attribute alone does not close the §9.2
half) is the one `B-124`'s prior leg already reached and this filing does not disturb. **Out of scope for
this fork**: the §9.2 half stays routed to `B-137`'s step-(3) posture decision (the head-sampler-realization
question), independent of what this filing decides for the derivation itself.

### (v) What a live floor is actually worth, so no reading overclaims it `[HIGH]`

Per `B-137` (measured, not assumed): even where a §9.2-style always-sampled row is realized, the shipped
head sampler applies the §10.3 per-cell ratio in **both** §9.1 modes, so only the head-**admitted** fraction
ever reaches a tail-side rule at all — measured **10.4%** admission at `base_rate=0.1`
(`team-binding × self-hosted-server`) and **20.9%** at `base_rate=0.2`
(`multi-tenant-compliance × managed-cloud`). This bears on the §9.2 half (already out of scope, §3(iv)), not
directly on the §10.2 half this filing's Reading A materializes — `is_classification_trigger` runs at
`TailKeepSpanProcessor.on_end`, downstream of head admission, so a live §10.2 trigger still only preserves
sibling spans for carriers the head already admitted. No reading below claims a full floor; a wired
`validator.fail.permanence` closes a real gap in the §10.2 trigger, not the head-sampling ceiling above it.

---

## §4 The readings

### Reading A — materialize the retry-exit classification at the emission site

**A-i (the only non-lossy form).** `ValidatorResult` gains an optional
`retry_exit_class: ValidatorRetryExitClass | None = None`, populated by the Validator implementation (the
only party that knows whether a fail is `HITL-recoverable` or a hard exit — the framework has no visibility
into that judgment). `_build_span_attributes` derives `validator.fail.permanence` via the existing
`validator_fail_permanence()` whenever the field is populated.

- **Cost.** A `ValidatorResult` schema change — a CP contract amendment at the C-CP-25/C-CP-28 §25.2 surface
  (a new field, X-AL-3-relevant), every operator-authored Validator implementation becomes a potential
  supplier, and the absent-field case needs a defined meaning (declared-unwired, matching today).
- **What it forecloses.** Nothing — it is strictly additive over the current schema.
- **What would falsify it.** If no Validator implementation in practice can supply the retry-exit judgment
  at `.validate()` time (e.g. the distinction is only knowable downstream, at dispatch), the field would sit
  permanently `None` and A-i degrades to Reading D with extra schema surface.

**A-ii (a fabrication, explicitly foreclosed — do not re-propose as a cheap A).** Derive
`retry_exit_class` *inside* the framework from `(outcome, fail_class, next_action, escalation_brief)`
instead of adding a producer field. §3(i)/§3(ii) grounded that none of those four axes carries the
distinction: `outcome`/`next_action` collide on the exact HITL-routing ambiguity §1.3 identified, and
`fail_class` is a cause-of-failure axis with a docstring saying so. A framework-internal derivation from
these fields would not *materialize* a classification the system holds — it would *invent* one, and every
candidate rule collapses to the same lossy outcome-based projection §1.3 already rejected. **Named and
ruled out here so it is not mistaken for a low-cost variant of A.**

### Reading B — ratify the outcome-based narrowing, with §21.6 re-specified

Wire `validator.fail.permanence = "permanent"` iff the CP-25/28 abort path fires
(`result.outcome == ValidatorOutcome.PERMANENT_FAIL`, equivalently `next_action == ValidatorNextAction.ABORT`),
else `"transient"` — roughly 3 functional lines at `_build_span_attributes`. **This does not answer the
question §1.3 posed.** `ValidatorOutcome.PERMANENT_FAIL` is CP-25/28's own concept (*"Workflow aborts with
`fail_class` propagation,"* `validator_framework_types.py:63-64`) — a Validator directly returning a
permanent-fail verdict — and is a different axis from the retry-exit taxonomy's `permanent-fail-exit` /
`terminal-fail-exit` members, both of which (per §3(i)) surface as `ESCALATE`, not `PERMANENT_FAIL`. Wiring
this rule would genuinely distinguish something (the CP-25 abort path from everything else) but it is **not**
a narrowed version of the retry-exit permanence concept §21.6 was built around — it answers a related but
distinct question under the same attribute name.

- **Cost.** ~3 functional lines, plus a mandatory CP spec delta re-specifying §21.6 to state honestly what
  the wire delivers (a declared narrowing of a cleared contract must be ratified, not absorbed — root
  `CLAUDE.md` §4.4).
- **What it forecloses.** If A-i ever lands, §21.6's re-specified text needs retracting again — an
  irreversible-in-the-cheap-sense cost (a later retraction, not merely an addition).
- **Its virtue.** The §10.2 trigger goes live now, for the abort path, honestly described as such rather
  than as retry-exit permanence.
- **What would falsify it.** If the operator does not consider CP-25's own `PERMANENT_FAIL` outcome a
  meaningful trigger for tail-keep preservation independent of the retry-exit taxonomy, Reading B has no
  remaining virtue and should not be selected.

### Reading C — select another carrier

Decouple the §10.2 row-1 trigger from `validator.fail.permanence` and key it on something the producer
genuinely and unambiguously holds today — e.g. `validator.fail.escalation_owed` (already emitted,
`validator_framework.py:343-345`) and/or `validator.outcome` directly, read as their own signal rather than
as a stand-in for permanence.

- **Cost.** An OD contract change to §10.2 row 1's carrier (`Spec_Operational_Discipline_v1_38.md`
  amendment), plus code changes at both `tail_keep_classification.py` and the sampler.
- **What it forecloses.** Permanently splits the §10.2 trigger's meaning from §21.6's permanence semantics
  — two readers of one conceptual floor become readers of two differently-named things, which is exactly
  the coherence cost `B-124`'s prior leg found when it discovered the two existing readers already don't
  share a fix (§3(iv)). This reading adds a *third* divergent carrier rather than resolving the split.
- **What would falsify it.** If `escalation_owed` or `outcome` turn out to already answer the operational
  question §10.2 row 1 exists for (preserve traces of hard validator failures) as well as permanence would,
  Reading C is cheaper than A-i and should be reconsidered — but this filing did not find that argument
  made anywhere on the record, and does not make it here.

### Reading D — defer the derivation, recorded with a demand trigger *(RECOMMENDED)*

`validator.fail.permanence` stays declared-unwired — the status quo `B-138`'s v1.116 §1.3 deliberately
chose over shipping a lossy value. No spec amendment, no code change, no test change. The row records why,
and what would reopen it.

- **Rationale.**
  1. **The two live readers do not share a fix, and one of them is already deferred.** The §9.2 half is
     out of scope here and already routed to `B-137`'s step-(3) posture decision (§3(iv)); wiring A-i's
     schema extension for the §10.2 half alone extends a CP contract for half the value a full derivation
     would deliver, and a second CP-contract touch is owed if the §9.2 posture question later requires a
     different carrier.
  2. **Reading B is a silent-narrowing risk with a real retraction cost.** It answers a different question
     under the permanence name and, if A-i later lands, needs its §21.6 text walked back — the one
     irreversible-flavored cost among the readings (§4 Reading B).
  3. **Reading C permanently forks one attribute's meaning across two readers**, compounding rather than
     resolving the split §3(iv) already found.
  4. **Deferring keeps the wire honest.** A declared-but-unwired attribute tells a reader nothing false. A
     wired-but-lossy or wired-but-reinterpreted one (B, C) tells a reader something that is not quite what
     the contract's name implies.
- **Demand trigger.** Reopens on either: (a) `B-137`'s step-(3) posture decision for the §9.2-realization
  family, since candidates there re-open how the floor resolves at the SDK boundary and may settle a carrier
  question this row could inherit; or (b) any arc that gives a Validator implementation surface a
  retry-exit-shaped disposition for its own reasons (independent of this row), which would make A-i's
  producer-field cost already-paid rather than newly-owed.
- **Honesty check.** This reading leaves a declared attribute unwired. It is not dressed as a fix — it is
  the status quo, argued for rather than merely left standing.

---

## §5 Recommendation — Reading D, runner-up Reading A-i, and the discriminator

**RECOMMENDED: Reading D.** `[MODERATE]` The dominant fact is §3(iv): the §9.2 half — the more valuable of
the two readers, since it governs unconditional preservation rather than a per-trace tail-keep trigger — is
**already** deferred to `B-137` and is **not** closeable by anything this row could do to the emission site.
Building A-i's schema extension now buys only the §10.2 half, at the cost of a CP contract amendment whose
value may need revisiting once `B-137` settles the SDK-boundary realization question. Reading B is rejected
because it answers a different, adjacent question under the contract's existing name and carries the
workspace's own named asymmetry (an addition later is free; a retraction later is not — `B-98` §3(v),
cited by the `B-88` filing at the same reasoning). Reading C is rejected because it compounds a
coherence problem already on the record rather than resolving it.

**RUNNER-UP: Reading A-i**, *not* Reading B or C. If the operator judges the §10.2 half worth closing now
independent of `B-137`'s timeline, A-i is the only non-lossy path and its cost (one optional field, cleanly
additive) is the smallest of the three live options.

**THE DISCRIMINATOR.** `[HIGH]`

> **Is the §10.2 half worth a standalone CP contract amendment before `B-137` settles the §9.2-realization
> posture — knowing that a live §10.2 trigger only preserves traces for carriers the head sampler already
> admitted (§3(v): ~10%–21% at production base rates)?**

- If **yes**, select **Reading A-i** now.
- If **no** — the value is small enough, and close enough to a question `B-137` will reopen the carrier
  question for anyway — select **Reading D**, which I recommend.

---

## §6 Council position — **No**, unchanged from the row

The register row's own council field: *"No. Wiring a declared-but-unset attribute inside a cleared schema,
with a named owner (C7/OD)."* This filing's grounding does not change that. The derivation sub-decision
this fork carries is narrower than the row's original framing — it is a choice between a producer-schema
extension (A-i), a declared narrowing of an existing contract (B), a carrier swap (C), or deferral (D), all
within one owner's domain (the CP/OD validator-observability seam), with no nameable cross-domain tension
between two specific voices. **Reading B is the one candidate that comes closest to owing a convening** —
it is a substantive observability-taxonomy commitment (the contract would say something about permanence
that is not, in fact, permanence in the retry-exit sense) — but the tension is against the contract's own
prior text, not between two operator concerns with opposing incentives, so it does not meet the nameable
-tension discriminator (root `CLAUDE.md` §10.9 posture amendment 1). No convening is recommended for any
reading, including B.

---

## §7 What this filing does NOT do

- It does not re-open the §10.2/§9.2 split — that is `B-124`'s prior leg's finding, carried forward at §3(iv)
  and left undisturbed.
- It does not re-litigate `B-138`'s taxonomy disposition (a) or the `ValidatorFailClass` domain ruling —
  those are settled at `Spec_Control_Plane_v1_116.md` §1.3 and cited, not re-argued.
- It does not touch `design-substrate/**`, any `CLAUDE.md`, or any code.
- It does not change register row `B-124`'s status. `B-124` stays `registered_finding`.
- It does not claim any reading delivers a full observability floor — §3(v) states the head-sampling ceiling
  explicitly so no reading is read as overclaiming.

---

## §8 Sequencing, and what each leg would owe

| Leg | Owes | Gate |
|---|---|---|
| **This filing** (doc-only) | The filing itself; no register edit | — |
| **Ratification** | Operator selects a reading via `AskUserQuestion`; a `§9 RATIFICATION` section would be appended to this filing; register row `B-124`'s status/`pr:` pointer updated on a separate leg | Operator |
| **Spec leg** *(A-i or B only)* | `Spec_Control_Plane_v1_116.md` → next delta version, by a dedicated spec-writer; clearance marker at `.harness/clearance/` per root `CLAUDE.md` §4.5 | X-AL-3 guard + adversarial review |
| **Impl leg** *(A-i or B only)* | The field/derivation + witnesses, by execution through the real `TailKeepSpanProcessor` (not by grep, per the standing verification-shape discipline) | CI + `merge-gate` 3-lens (code-touching) |
| **Under C** | An OD spec amendment to §10.2 row 1's carrier + code changes at both readers | X-AL-3 guard + adversarial review + CI |
| **Under D** *(recommended)* | Nothing beyond this filing; the row's `close_out` gains a one-line note recording the reading and its demand trigger | — |

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_2_fork_b124_validator_fail_permanence_derivation.md` (new) |
| Register row | `B-124`, stays `registered_finding` |
| Design-substrate touched | None (doc-only filing) |
| Code touched | None |
| Grounding HEAD | `4b3a33ce` |
| Council | No (§6) |
| Out of scope | The §9.2 half of `B-124` (routed to `B-137` step (3)); `B-138`'s taxonomy disposition (settled) |
| Recommendation | Reading D (defer), runner-up Reading A-i |
