# Class 1 Fork — `B-139`: `validator.fail.cause_attribution` is declared always-emitted at TWO canonical surfaces (plus a derived C5 carrier), but the declared producer's own contract shape cannot carry it

**Filed:** 2026-08-15 (`B-139` grounding leg — steps (1) and (2)'s probe, which the register row made mandatory before any disposition)
**Status:** OPEN — Class 1 (architectural defect; design-phase artifact requires revision)
**Halt target:** any arc that consumes `validator.fail.cause_attribution` as a present attribute, or that relies on the C5 FM-J rule (*"a fail-class without `cause_attribution` is FM-J"*) as an enforced invariant.
**Routing target (canonical):** `ADR-D5` §1.10.1 bullet 2 **and** `C-CP-21` §21.5 row 2 — the two CANONICAL surfaces, per the §1.3 authority chain (canonical design artifacts live under `design-substrate/`). Secondarily `C-CP-25` §25.2 (`ValidatorResult`), if the operator elects a wire-it reading.
**Owed synchronization (derived, NOT a back-flow target):** `.claude/skills/council/c5-validation-contract/SKILL.md` carries the same obligation at **six sites, not two** (`:33-38` reconciliation, `:128` vocabulary rule, `:161` taxonomy, `:234-236`, `:254` self-audit, `:277` FM-J) — the apply arc must sweep every semantic occurrence, not the two first cited (round-4 correction). This is where the FM-J rule text actually lives. It is **derived guidance downstream of the ADR**, so it does not vote on the disposition — but it MUST be synchronized once the canonical surfaces are amended, or stale skill text will keep asserting a requirement nothing produces. *(Scope corrected twice under out-of-family review: round 1 caught that the first draft omitted C5 entirely; round 2 caught that promoting it to a co-equal canonical surface inverted the authority chain.)*
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
`retry.cause_attribution` (`harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:1321,1376,1391,1418`) is likewise a
**different attribute** in the retry namespace, and it *does* have producers — which is
precisely why the loose search is misleading and the fixed-string one is the sound instrument.

## §2 — The defect: the declaration and the producer's contract shape are irreconcilable as written

**Step (2)'s probe is decisive, and it prices disposition (a) much higher than the row assumed.**

`ValidatorResult` — the operator-supplied return shape, `C-CP-25` §25.2, at
`harness-cp/src/harness_cp/validator_framework_types.py:171-188` — carries exactly five
fields: `outcome`, `fail_class`, `revalidation_payload`, `escalation_brief`,
`fail_detail_hash`. **There is no cause field, and no field from which a cause is derivable.**

The producer site is no better supplied. `ValidatorFramework._build_span_attributes` is called
at `harness-cp/src/harness_cp/validator_framework.py:237` and `:305` with `step`, `result`, `next_action`, and
`burden_count` — **none of which carries a cause**. The runtime escalation composer
(`validator_escalation_composer.py:143-153`) is the same story.

So the contradiction is not "someone forgot a line." It is structural:

> **Two canonical surfaces — echoed by a derived C5 carrier — declare an attribute
> unconditionally emitted on every validator-failure event, while the contract shape the
> declared producer returns has no member that could carry its value.**

**The cause values do not live anywhere — a claim this fork INHERITED from the register row
and has now re-grounded (out-of-family review round 3).** The row said the values "live in
§21.2's staircase branches and the retry/breaker machinery", and the first draft of this fork
repeated it. That is FALSE at HEAD: `StaircaseTransition.on_cause` is typed
`ValidatorRetryExitClass` (`validator_fail_transient_staircase.py:64`) and its own docstring
says so explicitly — *"(not a fail-cause token)"* at `:66` — while
`_classify_provider_exception` (`retry_breaker_fallback.py:281`) likewise returns
`ValidatorRetryExitClass | None`. The staircase carries the **5-class retry-exit taxonomy**,
not the 15-value attribution alphabet (10 base + 5 F5 `secret_*` refinements). §21.2's own
branch labels (`capability_shortfall_transient`,
`contract_violation_not_yet_routed_to_Reflexion`) are not §21.5 wire tokens either.

**The cause-source inventory — VERIFIED PER SURFACE, and deliberately not asserted as
complete.** This is the one claim in this fork that churned across review rounds 3, 4 and 5
(*"they live in the staircase"* → *"no source anywhere"* → *"one typed carrier"* → *"per-surface
carriers exist"*), so it is now stated as verified facts with cites rather than as an
inventory, and the completeness question is handed to the apply arc rather than guessed a
fourth time:

| Surface | Typed carrier | Live producer |
|---|---|---|
| 5 F5 `secret_*` refinements | **YES** — `SecretFailClass` StrEnum, `harness-as/src/harness_as/secret_fail_class.py:33-41` (C-AS-07 §7.1) | **PARTIAL — 3 of 5.** `SecretResolutionError` is constructed **11×** (AST-counted): 8× in `harness-runtime/src/harness_runtime/config/provider_secrets.py`, 3× in `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py`, **0 in `types.py`**. Those 11 constructions carry only `SECRET_UNKNOWN` and `SECRET_UNAVAILABLE`. `SECRET_LOCKED` reaches production by a **separate path** — `_emit_secret_fetch_span(..., fail_class=SecretFailClass.SECRET_LOCKED)` after catching `SecretAllowlistDeniedError`, at `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:817-824`. **`SECRET_EXPIRED` and `SECRET_REVOKED` have NO production reference at all.** So the arm has two distinct producer paths covering 3 of 5 values. |
| `replay_semantic_divergence` (ADR-D6's ADDITION, not one of the base set) | **YES** — `ReplaySemanticDivergenceError.validator_fail_cause_attribution`, pinned `Literal[...]`, `harness-od/src/harness_od/idempotency_join_dedup.py:375-377` | **NO** — the only occurrence in `src` is its own definition |
| the **10 base values**, for a general validator failure | — | **NO** — nothing maps a `ValidatorResult` onto them |
| `§21.2` staircase / retry | **NO** — `StaircaseTransition.on_cause` is `ValidatorRetryExitClass` (`harness-cp/src/harness_cp/validator_fail_transient_staircase.py:64`), and its docstring says so at `:66`: *"(not a fail-cause token)"*; `_classify_provider_exception` (`harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:281`) returns the same class | n/a |

> **The precise defect is therefore narrower than "nothing exists": per-surface typed causes
> DO exist and some are live, but there is no general mapping from a validator failure onto
> the base alphabet — which is exactly what an always-emitted declaration on EVERY
> validator-failure event requires.**

**This re-prices (B) DOWN from the round-3 wording** (it is not inventing classification from
scratch — the `secret_*` arm is already typed and live) **while leaving the gap real** for the
base values. A complete per-value inventory is **owed at the apply arc**, and this fork does
not assert one.

**An UNDISCHARGED CROSS-ADR OBLIGATION constrains every disposition.** `ADR-D6` §1.5.2
(`design-substrate/ADR-D6_v1_2.md:346-352`) extends the C5 catalog with
`replay_semantic_divergence` and states that *"ADR-D5 v1.2 §1.10.1 ... absorbs the new value at
the next D5 revision (forward-flagged; not blocking this revision)"*. `B-141` assigns that
synchronization to this row
(`.harness/b-141-validator-fail-class-cascade-2026-08-12.md:115-121`). An amendment that
demotes D5's declaration **while leaving D6's absorb-at-next-revision instruction standing**
would mint a fresh contradiction — the next D5 revision *is* the one this fork routes.

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

**(B) Derive the cause and thread it to the emission site.** **Re-priced THREE times; this is the
current pricing.** The `secret_*` arm is typed and **partly** live — `SecretFailClass` exists
and 3 of its 5 values reach production by **two distinct paths** — `SECRET_UNKNOWN` and
`SECRET_UNAVAILABLE` via the 11 AST-counted `SecretResolutionError` constructions, and
`SECRET_LOCKED` via `_emit_secret_fetch_span` after a `SecretAllowlistDeniedError`
(`runtime_tool_dispatcher.py:817-824`) — while `SECRET_EXPIRED` and `SECRET_REVOKED`
have **none** — so even that arm is part wiring, part
classification, not pure wiring as round 8 stated. What is missing is a **general mapping** from an
arbitrary validator failure onto the **10 base values**: nothing today classifies a
`ValidatorResult` into that alphabet, and `ValidatorRetryExitClass` is a different (5-class)
taxonomy that must not be silently conflated with it. So (B) is *part wiring, part new
classification*, plus the CP-internal coupling from the validator framework onto
retry/breaker state. Its honest cost sits **between** a pure wiring change and inventing a
taxonomy from scratch — and a complete per-value inventory (owed, §8) is what would price the
remaining share exactly.

**(C) — RECOMMENDED — demote the declaration from always-emitted to conditional at BOTH
canonical surfaces, AND synchronize the derived C5 carrier in the same arc.** **The scope was
corrected twice under review**, and the net correction is load-bearing: the first draft named
only ADR-D5 and C-CP-21 and would have left `c5-validation-contract/SKILL.md:33-38` still
stating *"Every fail-class signal carries a `cause_attribution` annotation"* and *"Emitting a
fail-class without attribution is failure mode FM-J"* (repeated at `:234-236`) — so (C) as
first written could NOT have made the corpus "true today", which was its entire
justification. C5 is **derived guidance, not a canonical surface**: it does not vote on the
disposition, but leaving it unsynchronized reproduces the defect in the carrier operators
actually read. This is the `B-138` precedent applied to its sibling attribute: **demote, do not
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
`retry.*` and pause-state hits and must not be used); **or** a member of `ValidatorResult` /
the `_build_span_attributes` inputs that carries a cause and was missed here; **or** a LIVE
constructor of `ReplaySemanticDivergenceError` (or any other producer) that actually emits a
value from the 15-value alphabet at runtime, which would re-price (B) back down toward a
wiring change.

---

## §7 — Confidence tags on this fork's non-trivial claims

| Claim | Confidence | Basis |
|---|---|---|
| No producer writes `validator.fail.cause_attribution` anywhere in `harness-*/src` | **HIGH** | fixed-string search over all seven trees; each of the five hits classified by reading |
| `ValidatorResult` and the `_build_span_attributes` inputs carry no cause | **HIGH** | direct read of `harness-cp/src/harness_cp/validator_framework_types.py:171-188` + both call sites |
| The staircase carries `ValidatorRetryExitClass`, not a cause token | **HIGH** | the type annotation at `:64` and its own docstring at `:66` say so verbatim |
| The `secret_*` arm is typed and **partly** live (3 of 5 values, via TWO producer paths) | **HIGH** | `SecretFailClass` enum; **11 AST-counted** `SecretResolutionError` constructions carrying `SECRET_UNKNOWN`/`SECRET_UNAVAILABLE`, plus a separate `_emit_secret_fetch_span` path for `SECRET_LOCKED`; `SECRET_EXPIRED` / `SECRET_REVOKED` unreferenced. *An earlier draft said "14" from `rg -c`, which counts matching LINES per file, not calls — corrected by AST at review round 9.* |
| `ReplaySemanticDivergenceError` has no live constructor | **MEDIUM** | a `src`-scoped count returned only its own definition; a dynamic/reflective construction would not be caught by that method |
| The per-surface inventory above is **complete** | **LOW — explicitly not claimed** | it was wrong in rounds 3, 4 and 5; completeness is owed at the apply arc, not asserted here |
| (C) is the right disposition | **MEDIUM** | it is the cheapest, most reversible, and precedented option — but it is an operator ratification, not a finding |

## §8 — Open questions, contested claims, recommended next probes

**Open questions (for the operator, at ratification).**
1. Which disposition — (A), (B), or (C)? This fork recommends (C) but does not decide it.
2. Is the FM-J rule **live debt** or **aspirational**? §5 routes this and deliberately does not answer it; with zero producers, every validator failure is FM-J by the rule as written.
3. Does the D5 amendment absorb `replay_semantic_divergence` (per ADR-D6 §1.5.2's forward flag) in the *same* revision that demotes the always-emitted claim? Doing one without the other leaves the corpus inconsistent either way.

**Contested / superseded claims — recorded so ratification is not misled.**
- The register row's premise that the cause values *"live in §21.2's staircase branches and the retry/breaker machinery"* is **DISPROVEN** (§2). This fork repeated it in its first draft.
- This fork's own round-3 wording, *"the alphabet has no source anywhere"*, is **also wrong** and was corrected at rounds 4-5. Neither statement should be quoted forward.

**Recommended next probes (for the apply arc, not blocking ratification).**
1. **Complete the per-value inventory** — for each of the 10 base values, does any typed carrier or live producer exist? This fork verified four surfaces and explicitly declines to claim completeness.
2. **Probe for a dynamic constructor** of `ReplaySemanticDivergenceError` (the one MEDIUM-confidence claim above) before treating that carrier as inert.
3. **Sweep C5's six sites** together (`:33-38`, `:128`, `:161`, `:234-236`, `:254`, `:277`) — a partial sync leaves the skill self-contradictory.

