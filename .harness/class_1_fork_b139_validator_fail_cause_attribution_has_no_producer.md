# Class 1 Fork — `B-139`: `validator.fail.cause_attribution` is declared always-emitted at THREE canonical surfaces, but the declared producer's own contract shape cannot carry it

**Filed:** 2026-08-15 (`B-139` grounding leg — steps (1) and (2)'s probe, which the register row made mandatory before any disposition)
**Status:** OPEN — Class 1 (architectural defect; design-phase artifact requires revision)
**Halt target:** any arc that consumes `validator.fail.cause_attribution` as a present attribute, or that relies on the C5 FM-J rule (*"a fail-class without `cause_attribution` is FM-J"*) as an enforced invariant.
**Routing target:** `ADR-D5` §1.10.1 bullet 2, `C-CP-21` §21.5 row 2, **and** `.claude/skills/council/c5-validation-contract/SKILL.md` §33-38 + §234-236 — the THREE surfaces that jointly declare the attribute always-emitted. Secondarily `C-CP-25` §25.2 (`ValidatorResult`), if the operator elects a wire-it reading. **The C5 surface was MISSED in this fork's first draft and added at out-of-family review round 1** — it is load-bearing, because it is where the FM-J rule actually lives.
**Detection mode:** exhaustive fixed-string search over all **seven** `harness-*/src` trees (`as`, `core`, `cp`, `cxa`, `is`, `od`, `runtime`) + a read of the producer's own input shapes. No new test was authored — this fork reports an ABSENCE, and the honest witness for an absence is the search that found nothing, not a test that asserts nothing.

---

## §1 — What the register row asked, and what grounding answered

`B-139`'s close-out made two things mandatory before any disposition: **(1)** re-verify zero
producers at HEAD, and **(2)** decide between **(a)** wiring the emission and **(b)**
re-declaring the condition via back-flow — pricing (a) honestly, because the row suspected
*"the producer does not currently hold a cause to emit."*

Both are now executed. **Step (1) — CONFIRMED, the row is not falsified.** A fixed-string
search for `validator.fail.cause_attribution` across all seven trees —
`harness-{as,core,cp,cxa,is,od,runtime}/src` — returns **five hits, and none is a producer**:

| Hit | What it actually is |
|---|---|
| `harness-cp/src/harness_cp/validator_fail_taxonomy.py:144` | the **declaration** (`attribute_name=...`) |
| `harness-cp/src/harness_cp/validator_fail_taxonomy.py:156` | a cardinality docstring |
| `harness-od/src/harness_od/content_structure_discipline.py:158` | a name in a content-structure list |
| `harness-od/src/harness_od/idempotency_join_dedup.py:358` | prose naming a §14.5.3 value |
| `harness-od/src/harness_od/idempotency_join_dedup.py:375` | a comment |

**A near-miss was ruled out rather than counted.** `harness-runtime/src/harness_runtime/api.py:1182`
writes `cause_attribution=`, which matches a loose search and would falsify the row if it were
this attribute. It is not: it constructs a `PauseStateCauseAttribution` on a
`PauseStateAuditPayload` — the pause-state audit carrier, a different namespace entirely.
`retry.cause_attribution` (`retry_breaker_fallback.py:1321,1376,1391,1418`) is likewise a
**different attribute** in the retry namespace, and it *does* have producers — which is
precisely why the loose search is misleading and the fixed-string one is the sound instrument.

## §2 — The defect: the declaration and the producer's contract shape are irreconcilable as written

**Step (2)'s probe is decisive, and it prices disposition (a) much higher than the row assumed.**

`ValidatorResult` — the operator-supplied return shape, `C-CP-25` §25.2, at
`harness-cp/src/harness_cp/validator_framework_types.py:171-188` — carries exactly five
fields: `outcome`, `fail_class`, `revalidation_payload`, `escalation_brief`,
`fail_detail_hash`. **There is no cause field, and no field from which a cause is derivable.**

The producer site is no better supplied. `ValidatorFramework._build_span_attributes` is called
at `validator_framework.py:237` and `:305` with `step`, `result`, `next_action`, and
`burden_count` — **none of which carries a cause**. The runtime escalation composer
(`validator_escalation_composer.py:143-153`) is the same story.

So the contradiction is not "someone forgot a line." It is structural:

> **Three canonical surfaces declare an attribute unconditionally emitted on every
> validator-failure event, while the contract shape the declared producer returns has no
> member that could carry its value.**

The cause values the declaration enumerates (10 base + 5 F5 `secret_*` refinements) live in
`§21.2`'s staircase branches and in the retry/breaker machinery — **on the other side of the
seam** from the validator that is supposed to emit them.

## §3 — Why this is Class 1 and not a Phase-7 absorption

Wiring it would require **either** extending `ValidatorResult` (an operator-facing contract at
`C-CP-25` §25.2 — every operator-supplied validator in existence returns this shape) **or**
threading cause state from the staircase/retry machinery across the seam into the validator
framework. Both are design-substrate changes. Choosing either silently at Phase 7 is exactly
the X-AL-3 silent-absorption failure mode, and §1.3's authority chain puts the choice above
this workspace.

## §4 — Dispositions

**(A) Wire it — extend `ValidatorResult` with a cause member.** Honest cost: it changes an
operator-facing return contract, so every existing operator validator must supply (or default)
the new field, and the §25.2 cardinality table grows a row. It also does not, by itself, solve
availability — the operator's validator would have to *know* the cause, which for the
staircase-derived values it generally does not.

**(B) Thread the cause across the seam.** Keeps `ValidatorResult` intact by having the
framework derive the cause from the staircase/retry context at emission time. Honest cost: it
creates a new CP-internal dependency from the validator framework onto retry/breaker state,
and the §21.2 branches would have to expose a stable cause value. This is the reading that
best preserves the *declaration's* intent, at the price of new coupling.

**(C) — RECOMMENDED — demote the declaration from always-emitted to conditional, at ALL
THREE surfaces.** **This scope was CORRECTED at out-of-family review round 1**, and the
correction is load-bearing: the first draft named only ADR-D5 and C-CP-21, but
`c5-validation-contract/SKILL.md:33-38` independently states *"Every fail-class signal
carries a `cause_attribution` annotation"* and *"Emitting a fail-class without attribution is
failure mode FM-J"*, and `:234-236` repeats the obligation. Demoting only the first two would
leave C5 still requiring what nothing produces — so (C) as first written could NOT have made
the corpus "true today", which was its entire justification. This is the `B-138` precedent applied to its sibling attribute: **demote, do not
delete**. `B-138` corrected the `class` domain and demoted the permanence derivation clause
rather than removing it, and the third §21.5 attribute was left declared-required with no
owner precisely because that leg stopped short — which is what minted `B-139`. Demoting is
also the only disposition that makes the corpus *true today* rather than true-after-a-build.

**The choice is the operator's.** (C) is recommended because it is reversible, requires no
operator-facing contract break, and follows a precedent this workspace already ratified; (A)
and (B) both remain open if the cause-conditioned staircase branch is judged to need the
attribute enforced.

## §5 — The FM-J framing must be dispositioned in the same breath (step 3)

`ADR-D5` §1.10.1 attaches a named failure mode to this attribute: *"a fail-class without
`cause_attribution` is FM-J per `c5-validation-contract` SKILL.md."* With zero producers,
**every** validator failure the harness emits today is FM-J by that rule. Either the rule is
live debt (and the corpus currently describes a harness in permanent violation), or it is
aspirational and must say so. A declared failure-mode name attached to an unwired attribute is
the stale-carry-text class this workspace already documents — it must be answered explicitly,
not left to the reader.

## §6 — What would falsify this fork

A producer writing the exact key `validator.fail.cause_attribution` anywhere in `harness-*/src`
(the fixed-string search above is the instrument — a loose `cause_attribution` search returns
`retry.*` and pause-state hits and must not be used), **or** a member of `ValidatorResult` /
the `_build_span_attributes` inputs that carries a cause and was missed here.
